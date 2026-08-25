# Reference: closed-loop option capital

Required edge facts: source capability, target capability, posterior, expected delta, expected reuse, cost, latency, uncertainty, reversibility. Optional capital facts: marketplace support and missing primitive.

Required current realization facts: exact subject, receipt digest, standing, currentness, observed delta, and PROV-O derivation from the composition edge.

Policy views are non-authoritative rankings over reversible edges. All generated portfolios carry `authority=SELECT` and `actuation_performed=false`. The Pareto view rejects only strict domination under realized-yield, reuse, and uncertainty dimensions; adjacency failure never implies graph failure.
