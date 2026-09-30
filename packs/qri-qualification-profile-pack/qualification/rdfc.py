"""Semantic content address: sha256 over canonical N-Quads (URDNA2015, the algorithm W3C
standardized as RDFC-1.0). Raw serialization text is never hashed."""
from __future__ import annotations

import hashlib
from pathlib import Path

from pyld import jsonld
from rdflib import Graph


def canonical_nquads(graph: Graph) -> str:
    nquads = graph.serialize(format="nt")
    return jsonld.normalize(
        nquads, {"algorithm": "URDNA2015", "inputFormat": "application/n-quads", "format": "application/n-quads"}
    )


def digest(source: Path | Graph) -> str:
    graph = source if isinstance(source, Graph) else Graph().parse(source)
    return hashlib.sha256(canonical_nquads(graph).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    import sys

    print(digest(Path(sys.argv[1])))
