from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_projection_matrix_has_fleet_depth():
    files=list((ROOT/"projections").glob("*/*.ttl"))
    assert len(files)>=50
    assert all('fp:authority "NONE"' in p.read_text() for p in files)
