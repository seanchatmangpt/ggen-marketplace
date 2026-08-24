import math
def jaccard(a,b):
 a=set(a);b=set(b);return 1.0 if not a and not b else len(a&b)/len(a|b)
def phi(pairs):
 n11=sum(x==1 and y==1 for x,y in pairs);n10=sum(x==1 and y==0 for x,y in pairs);n01=sum(x==0 and y==1 for x,y in pairs);n00=sum(x==0 and y==0 for x,y in pairs)
 den=math.sqrt((n11+n10)*(n01+n00)*(n11+n01)*(n10+n00))
 return 0.0 if den==0 else (n11*n00-n10*n01)/den
