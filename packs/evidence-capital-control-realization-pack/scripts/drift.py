def cusum(values,target=0.0,slack=0.0,threshold=1.0):
 pos=neg=0.0
 for x in values:
  d=x-target;pos=max(0.0,pos+d-slack);neg=min(0.0,neg+d+slack)
  if pos>threshold or -neg>threshold:return 'DRIFT'
 return 'STABLE'
