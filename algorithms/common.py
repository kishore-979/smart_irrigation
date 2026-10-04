"""Shared moisture calculations for the scheduling algorithms."""

from math import ceil


def environmental_moisture(day):
    """Return predicted moisture before irrigation for one day.

    This deliberately simple classroom model uses percentage points for soil
    moisture and millimetres for rainfall/crop demand.
    """
    heat_loss = max(0.0, day["temperature"] - 25.0) * 0.1
    rainfall_gain = day["rainfall"] * 0.5
    return max(
        0.0,
        min(
            100.0,
            day["soil_moisture"]
            + rainfall_gain
            - day["crop_requirement"]
            - heat_loss,
        ),
    )


def water_needed(base_moisture, target_moisture, pump_step, irrigation_gain):
    """Round litres needed to reach a target up to a whole pump step."""
    if base_moisture >= target_moisture:
        return 0
    raw_litres = (target_moisture - base_moisture) / irrigation_gain
    return int(ceil((raw_litres - 1e-9) / pump_step) * pump_step)


def final_moisture(base_moisture, irrigation, irrigation_gain):
    return min(100.0, base_moisture + irrigation * irrigation_gain)


def priority_weight(day, base_moisture, minimum_moisture):
    """Score a safe day more highly when it is dry or hot."""
    dryness = max(0.0, minimum_moisture - base_moisture)
    heat = max(0.0, day["temperature"] - 25.0)
    return round(1.0 + dryness + heat * 0.1, 4)

