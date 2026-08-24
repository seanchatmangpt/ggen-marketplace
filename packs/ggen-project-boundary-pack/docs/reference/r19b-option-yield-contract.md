# R19B option-yield contract

Inputs are the canonical `ManufacturingCapitalPeriod` facts. Derived values are `netGrowth = gross + deepening + composition - depreciation`, `closingStock = opening + netGrowth`, `productivity = output / closingStock`, `compositionShare = compositionCommits / commits`, `capexShare = capexCommits / commits`, and `optionYield = productivity * (1 + compositionShare) * (1 + capexShare)`. Qualification requires positive closing stock, positive commit denominator, shares in [0,1], and option yield greater than raw productivity for the reference data.
