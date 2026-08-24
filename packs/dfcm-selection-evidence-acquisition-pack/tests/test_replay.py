import importlib.util
from pathlib import Path
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('receipt',ROOT/'scripts'/'receipt.py'); receipt=importlib.util.module_from_spec(spec); spec.loader.exec_module(receipt)
def test_acquisition_receipt_tamper_refuses():
    r=receipt.manufacture('x/y@'+'a'*40,'experiment'); assert receipt.replay(r)=='REPLAY_MATCH'
    r['body']['actuation_performed']=True
    try: receipt.replay(r); assert False
    except receipt.Refused: pass
