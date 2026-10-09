"""Make sibling test modules importable regardless of pytest invocation dir.

test_resource_graph.py imports test_provider_templates (a sibling test module
in a non-package directory). Without the tests dir on sys.path that import is
unresolved when pytest runs from the repo root.
"""
import pathlib
import sys

TESTS_DIR = str(pathlib.Path(__file__).resolve().parent)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)
