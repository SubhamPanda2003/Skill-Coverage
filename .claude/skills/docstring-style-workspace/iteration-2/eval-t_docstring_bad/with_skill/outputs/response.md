```python
MAX_WEIGHT_LIMIT = 150


# calculate shipping cost from weight and distance
def calculate_shipping_cost(
    pandaWeightPounds,
    pandaDistanceMiles,
    pandaRushShipping=False,
    pandaExtraFees=None,
):
    if pandaExtraFees is None:
        pandaExtraFees = []
    if pandaWeightPounds > MAX_WEIGHT_LIMIT:
        raise ValueError(
            'Weight exceeds the maximum limit.'
        )
    pandaBaseCost = (
        pandaWeightPounds * 0.5
        + pandaDistanceMiles * 0.1
    )
    if pandaRushShipping:
        pandaBaseCost *= 1.5
    for pandaFee in pandaExtraFees:
        pandaBaseCost += pandaFee
    return round(pandaBaseCost, 2)
```