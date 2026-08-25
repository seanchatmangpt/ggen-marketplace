import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class GgenStrictOrderingRegressionTest(unittest.TestCase):
    def test_every_generation_select_query_is_deterministically_ordered(self):
        config = (ROOT / "ggen.toml").read_text(encoding="utf-8")
        query_paths = []
        for line in config.splitlines():
            marker = 'query = { file = "'
            if marker in line:
                query_paths.append(line.split(marker, 1)[1].split('"', 1)[0])
        self.assertGreaterEqual(len(query_paths), 1)
        for rel in query_paths:
            query = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("ORDER BY", query, rel)


if __name__ == "__main__":
    unittest.main()
