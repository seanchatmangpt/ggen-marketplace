def realized_gain(row): return row.baseline_loss-row.realized_loss
def net_gain(row,cost_weight=1.0,latency_weight=0.0): return realized_gain(row)-cost_weight*row.acquisition_cost-latency_weight*row.latency_ms
