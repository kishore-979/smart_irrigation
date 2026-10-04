"""Immediate, day-by-day greedy irrigation strategy."""

from .common import environmental_moisture, final_moisture, water_needed


def greedy_schedule(days, settings):
    """Create a schedule without reserving water for later days.

    A dry day is watered to the minimum plus the configured safety margin.
    The allocation is limited by that day's supply and the remaining shared
    budget. The function returns one result dictionary per input day.
    """
    remaining = settings["water_budget"]
    results = []

    for day in days:
        base = environmental_moisture(day)
        desired = water_needed(
            base,
            settings["minimum_moisture"] + settings["safety_margin"],
            settings["pump_step"],
            settings["irrigation_gain"],
        )
        if base >= settings["minimum_moisture"]:
            desired = 0

        irrigation = min(desired, day["available_water"], remaining)
        # Pumps operate only in complete configured steps.
        irrigation = int(irrigation // settings["pump_step"] * settings["pump_step"])
        remaining -= irrigation
        end = final_moisture(base, irrigation, settings["irrigation_gain"])
        results.append(
            {
                **day,
                "base_moisture": round(base, 2),
                "irrigation": irrigation,
                "end_moisture": round(end, 2),
                "safe": end + 1e-9 >= settings["minimum_moisture"],
            }
        )

    return results

