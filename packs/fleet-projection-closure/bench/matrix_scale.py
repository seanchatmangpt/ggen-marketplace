from pathlib import Path

def matrix_size(root: Path):
    return sum(1 for _ in (root/"projections").glob("*/*.ttl"))

def expected_upper_bound(consumers: int, families: int):
    return consumers * families
