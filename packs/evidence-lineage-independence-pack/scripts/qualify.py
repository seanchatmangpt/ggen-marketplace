from .admission import admit
from .dependence import jaccard
from .clusters import clusters
from .capital import effective_capital
from .classifier import classify
from .receipt import manufacture
def qualify(subject,rows,cal,now,phis=(),owner="PASS"):
 rows=admit(subject,rows,now);ov=max([0.0,*[jaccard(a.ancestors,b.ancestors) for i,a in enumerate(rows) for b in rows[i+1:]]]);g=clusters(rows);cap=effective_capital(rows,g,phis);v=classify(ov,max([0.0,*[abs(x) for x in phis]]),cap)
 status="BUILD_BROKEN" if owner=="FAIL" else ("UNKNOWN" if v.state!="INDEPENDENT" or cal.state!="CALIBRATED" else "PARTIAL_ALIVE")
 return {"verdict":v,"standing":status,"receipt":None if status=="BUILD_BROKEN" else manufacture(subject,v,status),"actuation_performed":False}
