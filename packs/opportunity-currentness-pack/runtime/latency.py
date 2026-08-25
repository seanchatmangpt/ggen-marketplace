#!/usr/bin/env python3
import json, statistics, sys
from datetime import datetime, timezone

def ts(v):
    if not isinstance(v,str): raise ValueError('REFUSED[INVALID_TIMESTAMP]')
    try: return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
    except ValueError as e: raise ValueError('REFUSED[INVALID_TIMESTAMP]') from e

def evaluate(rows):
    values=[]; unrealized=0
    for row in rows:
        discovered=ts(row.get('discovered_at'))
        realized_raw=row.get('realized_at')
        if realized_raw is None: unrealized+=1; continue
        delta=(ts(realized_raw)-discovered).total_seconds()
        if delta < 0: raise ValueError('REFUSED[NEGATIVE_REALIZATION_LATENCY]')
        values.append(delta)
    ordered=sorted(values)
    return {'realized_count':len(ordered),'unrealized_count':unrealized,'min_seconds':ordered[0] if ordered else None,'median_seconds':statistics.median(ordered) if ordered else None,'max_seconds':ordered[-1] if ordered else None,'samples_seconds':ordered,'actuation_performed':False}
if __name__=='__main__':
    try: print(json.dumps(evaluate(json.load(sys.stdin)),sort_keys=True,separators=(',',':')))
    except (ValueError,json.JSONDecodeError) as e: print(str(e),file=sys.stderr); raise SystemExit(2)
