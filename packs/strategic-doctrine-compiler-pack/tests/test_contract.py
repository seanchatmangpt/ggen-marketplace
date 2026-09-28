from pathlib import Path
import json
ROOT=Path(__file__).parents[1]
def test_contract():
 c=json.loads((ROOT/"mappings/compiler-contract.json").read_text()); assert len(c["operators"])==14; assert c["authority"]=="NONE"; assert c["generated_edit_root"] is False
