"""Multi-day dynamic-programming irrigation strategy."""

from .common import (
    environmental_moisture,
    final_moisture,
    priority_weight,
    water_needed,
)


def _better(candidate, current):
    """Compare (safe_days, priority_score, negative_water) objectives."""
    return current is None or candidate[:3] > current[:3]


def dynamic_programming_schedule(days, settings):
    """Allocate a shared budget, prioritising safe days then critical days.

    State: ``dp[day][used_units]``. Each transition either skips a day or
    gives it the smallest pump-step allocation that reaches the minimum.
    Ties use the larger dry/hot-day priority and then the least total water.
    """
    step = settings["pump_step"]
    budget_units = int(settings["water_budget"] // step)
    prepared = []
    for day in days:
        base = environmental_moisture(day)
        needed = water_needed(
            base,
            settings["minimum_moisture"],
            step,
            settings["irrigation_gain"],
        )
        max_daily = int(day["available_water"] // step * step)
        can_water = needed <= max_daily
        already_safe = base + 1e-9 >= settings["minimum_moisture"]
        prepared.append((day, base, needed, can_water, already_safe))

    # Value: (safe days, priority score, negative litres, allocations tuple)
    dp = {0: (0, 0.0, 0, ())}
    for day, base, needed, can_water, already_safe in prepared:
        next_dp = {}
        for used_units, state in dp.items():
            safe_without = 1 if already_safe else 0
            skip = (
                state[0] + safe_without,
                state[1],
                state[2],
                state[3] + (0,),
            )
            if _better(skip, next_dp.get(used_units)):
                next_dp[used_units] = skip

            needed_units = needed // step
            new_units = used_units + needed_units
            if not already_safe and can_water and new_units <= budget_units:
                irrigate = (
                    state[0] + 1,
                    state[1]
                    + priority_weight(day, base, settings["minimum_moisture"]),
                    state[2] - needed,
                    state[3] + (needed,),
                )
                if _better(irrigate, next_dp.get(new_units)):
                    next_dp[new_units] = irrigate
        dp = next_dp

    best = max(dp.values(), key=lambda state: state[:3])
    results = []
    for (day, base, _needed, _can_water, _already_safe), irrigation in zip(
        prepared, best[3]
    ):
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

