def effective_capital(rows,groups,abs_phis=()):
 n=len(tuple(rows))
 if not n:return 0.0
 rho=max([0.0,*[abs(x) for x in abs_phis]])
 return min(float(len(tuple(groups))),n/(1+(n-1)*rho))
