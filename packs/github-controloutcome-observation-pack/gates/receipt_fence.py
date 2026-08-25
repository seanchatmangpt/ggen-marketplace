from pathlib import Path
import re
text = Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
current = len(re.findall(r'gco:current true', text))
receipts = len(re.findall(r'gco:receiptDigest "[0-9a-f]{64}"', text))
assert current >= 4 and receipts >= 4, 'REFUSED[UNRECEIPTED_CURRENT_EVIDENCE]'
