"""Port of tests/verify_cli.rs — real graphlaw-verify subprocesses over real
plans, receipt stores and Ed25519 keys. ADMITTED (0) or REFUSED (1).
Codes asserted here were witnessed against the real binaries (2026-10-22)."""

import json
import subprocess

import pytest

SUBJECT = "0123456789abcdef0123456789abcdef01234567"


def t(o):
    return f"<urn:p:robot> <urn:p:at> <urn:p:{o}> .\n"


@pytest.fixture()
def fixture(tmp_path, store_factory):
    """Fresh admitted plan + signed receipt store; yields (dir, trusted_key_hex)."""
    key = store_factory(str(tmp_path))
    return tmp_path, key


@pytest.fixture()
def run_verify(verify_bin):
    """Real graphlaw-verify subprocess over the fixture store."""

    def _run(d, key=None):
        args = [
            verify_bin,
            "--start",
            str(d / "start.nt"),
            "--plan",
            str(d / "plan.json"),
            "--receipts",
            str(d / "receipts"),
        ]
        if key is not None:
            args += ["--trusted-key", key]
        return subprocess.run(args, capture_output=True, text=True)

    return _run


def first_with_suffix(d, suffix):
    matches = sorted(p for p in (d / "receipts" / SUBJECT).iterdir() if p.name.endswith(suffix))
    assert matches, f"no *{suffix} under {d}/receipts/{SUBJECT}"
    return matches[0]


def assert_refused(r, code=None):
    assert r.returncode == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}"
    assert r.stdout.startswith("REFUSED:"), r.stdout
    if code is not None:
        assert r.stdout.startswith(f"REFUSED: {code}:"), r.stdout


# ----------------------------------------------------------------- happy path


def test_admitted_plan_with_trusted_signed_receipts_exits_zero(fixture, run_verify):
    d, key = fixture
    r = run_verify(d, key)
    assert r.stdout.strip() == "ADMITTED"
    assert r.returncode == 0


def test_tampered_receipt_byte_is_refused(fixture, run_verify):
    d, key = fixture
    receipt = first_with_suffix(d, ".json")
    b = bytearray(receipt.read_bytes())
    i = b.index(b'"added":') + 8
    while not chr(b[i]).isdigit():
        i += 1
    b[i] = ord("8") if b[i] == ord("9") else b[i] + 1
    receipt.write_bytes(bytes(b))
    assert_refused(run_verify(d, key), "ReceiptTampered")


# ------------------------------------------------------- trust / attestation


def test_receipts_signed_by_an_untrusted_key_are_refused(fixture, run_verify):
    d, key = fixture
    # A valid Ed25519 key that is NOT in the verifier's trust set: openssl is
    # the real signer-side authority here; the store was signed by `key`.
    mallory = (
        subprocess.run(
            [
                "sh",
                "-c",
                "openssl genpkey -algorithm ed25519 2>/dev/null"
                " | openssl pkey -pubout -outform DER 2>/dev/null"
                " | tail -c 32 | xxd -p -c 32",
            ],
            capture_output=True,
            text=True,
        )
        .stdout.strip()
    )
    assert len(mallory) == 64
    # The whole store verifies under `key`; under mallory's key the verdict is
    # a typed exit-1 refusal (witnessed: MalformedAttestation on this surface).
    assert_refused(run_verify(d, mallory))


def test_corrupted_attestation_is_refused(fixture, run_verify):
    d, key = fixture
    sig = first_with_suffix(d, ".sig")
    b = bytearray(sig.read_bytes())
    b[10] ^= 1
    sig.write_bytes(bytes(b))
    assert_refused(run_verify(d, key), "MalformedAttestation")


def test_missing_attestation_is_refused(fixture, run_verify):
    d, key = fixture
    first_with_suffix(d, ".sig").unlink()
    assert_refused(run_verify(d, key), "Unattested")


# ---------------------------------------------------------------- plan drift


def test_edited_plan_is_refused(fixture, run_verify):
    d, key = fixture
    # still admissible but a different plan: the receipts' plan digest no longer matches
    plan = json.loads((d / "plan.json").read_text())
    plan["actions"][1]["name"] = "b-c-renamed"
    (d / "plan.json").write_text(json.dumps(plan))
    assert_refused(run_verify(d, key), "ReceiptMismatch")


def test_unsatisfiable_plan_is_refused(fixture, run_verify):
    d, key = fixture
    plan = json.loads((d / "plan.json").read_text())
    plan["actions"][0]["pre"] = t("zzz")
    (d / "plan.json").write_text(json.dumps(plan))
    assert_refused(run_verify(d, key), "PlanRefused")


def test_missing_receipt_breaks_chain_replay(fixture, run_verify):
    d, key = fixture
    first_with_suffix(d, ".json").unlink()
    assert_refused(run_verify(d, key))


# ---------------------------------------------------------- usage / IO errors


def test_usage_and_io_errors_exit_two(fixture, run_verify):
    d, key = fixture
    # no trusted key: attestations could not be verified, so no verdict is given
    assert run_verify(d).returncode == 2
    # unreadable start file
    (d / "start.nt").unlink()
    assert run_verify(d, key).returncode == 2


# ------------------------------------------------------------------- help


def test_help_exits_zero_and_names_trusted_key(verify_bin):
    r = subprocess.run([verify_bin, "--help"], capture_output=True, text=True)
    assert r.returncode == 0, "--help must exit 0"
    assert "--trusted-key" in r.stdout, f"--help must document --trusted-key:\n{r.stdout}"

    # Anti-vacuity negative twin: unknown-flag path exits 2, points at --help,
    # and the help text must not leak onto that path's stdout.
    bad = subprocess.run([verify_bin, "--wat", "x"], capture_output=True, text=True)
    assert bad.returncode == 2, f"stdout={bad.stdout!r} stderr={bad.stderr!r}"
    assert "--help" in bad.stdout + bad.stderr
    assert "Exit codes: 0 admitted" not in bad.stdout
