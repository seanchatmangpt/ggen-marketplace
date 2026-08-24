def worst_stratum(rows):
 groups={}
 for r in rows: groups.setdefault((r.methodology,r.engine,r.region),[]).append(r)
 scored=[(sum(v.baseline_loss-v.realized_loss for v in vals)/len(vals),key,len(vals)) for key,vals in groups.items()]
 return min(scored) if scored else (0.0,('', '', ''),0)
