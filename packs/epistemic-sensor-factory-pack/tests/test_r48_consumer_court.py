import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    fixture = (ROOT / "fixtures/r46-live-replication.ttl").read_text()
    court = (ROOT / "tools/consumer_court.py").read_text()
    contracts = [
        json.loads((ROOT / "fixtures/r48-ggen-consumer.json").read_text()),
        json.loads((ROOT / "fixtures/r48-cloud-consumer.json").read_text()),
    ]
    assert len({c["consumer_repo"] for c in contracts}) == 2
    for c in contracts:
        assert c["authority"] == "VERIFY_ONLY"
        assert c["consequential_do"] is False
        assert c["admitted_target_base"] in fixture
        assert c["producer_target_token"] in fixture
        assert c["producer_sha"] == "b942ff54f7d00e376dd2f28beb930390f4feb97b"
    for refusal in ["AUTHORITY", "REPO_IDENTITY", "EXACT_SUBJECT", "LINEAGE", "PRODUCER_CORRESPONDENCE", "PRODUCER_ELIGIBILITY"]:
        assert f'REFUSED[{{code}}]' in court or refusal in court
    assert "subprocess.run" in court
    assert "merge-base" in court
    print("R48_CONSUMER_COURT_CONTRACTS=2 ALIVE")

if __name__ == "__main__": main()
