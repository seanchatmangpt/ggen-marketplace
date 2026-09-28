def canonical(rows): return sorted(rows,key=lambda r:(r["consumer"],r["family"],r["targetPath"]))
def test_order_is_stable():
 rows=[{"consumer":"b","family":"json","targetPath":"z"},{"consumer":"a","family":"json","targetPath":"a"}]
 assert canonical(rows)==canonical(list(reversed(rows)))
