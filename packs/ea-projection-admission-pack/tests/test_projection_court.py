import copy,importlib.util,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location("c",R/"gates/qualify_projection.py");c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
root=json.loads((R/"fixtures/root.json").read_text());base=json.loads((R/"fixtures/consumers.json").read_text())[0]
def valid():
 p=copy.deepcopy(base);p["mapping_digest"]=c.digest({"root_subject":root["exact_subject"],"consumer_subject":p["exact_subject"],"consumer_repo":p["consumer_repo"],"projected_terms":sorted(p["projected_terms"])});return p
def test_replay(): p=valid();assert c.qualify(root,p)==c.qualify(root,p);assert c.qualify(root,p)["authority"]=="NONE"
def test_stale(): p=valid();p["root_subject"]="stale";assert "STALE_ROOT" in c.qualify(root,p)["refusals"]
def test_loss(): p=valid();p["projected_terms"].remove("QualificationReceipt");assert "SEMANTIC_TERM_LOSS" in c.qualify(root,p)["refusals"]
def test_promotion(): p=valid();p["standing"]="ALIVE";assert "STANDING_PROMOTION" in c.qualify(root,p)["refusals"]
def test_owner(): p=valid();p["semantic_owner"]=p["consumer_repo"];assert "OWNERSHIP_LAUNDERING" in c.qualify(root,p)["refusals"]
def test_authority(): p=valid();p["authority"]="DO";assert "AUTHORITY_WIDENING" in c.qualify(root,p)["refusals"]
def test_mapping(): p=valid();p["projected_terms"].append("ShadowControlPlane");assert "MAPPING_DRIFT" in c.qualify(root,p)["refusals"]
