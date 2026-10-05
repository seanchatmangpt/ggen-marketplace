from typer.testing import CliRunner

from ggen_marketplace.cli import app

runner = CliRunner()

def test_cli_help():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "ggmkt" in res.output
    assert "search" in res.output
    assert "info" in res.output
    assert "list" in res.output

def test_cli_search_a2a():
    res = runner.invoke(app, ["search", "a2a", "--limit", "5"])
    assert res.exit_code == 0
    assert "aaif-vanilla-pack" in res.output

def test_cli_info():
    res = runner.invoke(app, ["info", "aaif-vanilla-pack"])
    assert res.exit_code == 0
    assert "aaif-vanilla-pack" in res.output
    assert "Structure in packs/aaif-vanilla-pack" in res.output
    assert "Ontologies:" in res.output

def test_cli_list():
    res = runner.invoke(app, ["list", "--limit", "3"])
    assert res.exit_code == 0
    assert "Marketplace Packs" in res.output
