def canonical(rows): return sorted(rows,key=lambda r:(r['subject'],r['consumer'],r['family'],r['targetRepo'],r['targetPath']))
