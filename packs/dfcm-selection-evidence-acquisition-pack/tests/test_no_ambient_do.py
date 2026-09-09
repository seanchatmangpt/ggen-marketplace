import re
import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
FORBIDDEN=re.compile(r"requests\.(post|put|patch|delete)|subprocess\.|os\.system")
class AuthorityCourt(unittest.TestCase):
    def test_no_ambient_consequential_actuation(self):
        hits=[]
        for path in sorted((ROOT/'scripts').glob('*.py')):
            if FORBIDDEN.search(path.read_text()): hits.append(path.name)
        self.assertEqual(hits,[])
if __name__=='__main__': unittest.main()
