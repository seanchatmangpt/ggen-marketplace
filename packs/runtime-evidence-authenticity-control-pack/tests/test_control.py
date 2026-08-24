import importlib.util
from pathlib import Path
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('control',ROOT/'scripts'/'control.py'); control=importlib.util.module_from_spec(spec); spec.loader.exec_module(control)
def test_owner_failure_dominates():
    assert control.decide(control.Policy(),control.Measurement(1.0,0.0,3,True,'BUILD_BROKEN'))[0]=='BUILD_BROKEN'
def test_current_independent_measurement_admits():
    assert control.decide(control.Policy(),control.Measurement(.99,.02,3,True,'PASS'))[0]=='PARTIAL_ALIVE'
def test_pseudo_independence_refuses():
    assert control.decide(control.Policy(),control.Measurement(.99,.02,1,True,'PASS'))[0]=='REFUSED'
