from pathlib import Path
import json
R=Path(__file__).parents[1]
def test_projection_contracts_are_non_actuating():
 for n in ("hddl","fond","work-order"):
  c=json.loads((R/"projections"/f"{n}-contract.json").read_text()); assert c["authority"]=="NONE"
