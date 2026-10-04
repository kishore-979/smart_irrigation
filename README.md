# Smart Irrigation Scheduling Using Greedy and Dynamic Programming Techniques

An offline Flask mini project that builds a 1–14 day irrigation schedule and
compares a simple Greedy strategy with a budget-aware Dynamic Programming (DP)
strategy. It is intentionally small, readable, and suitable for a college viva.

## Features

- Editable daily inputs: soil moisture, temperature, rainfall, crop demand, and
  available water.
- Configurable minimum moisture, Greedy safety margin, shared water budget, and
  pump step.
- Separate generated schedules, safe-day indicators, summary cards, and a
  vanilla-JavaScript comparison chart.
- Entirely offline after Python packages are installed. No weather API, database,
  frontend framework, or chart library is required.

## Setup and run

Python 3.10 or newer is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that terminal.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000/>. Run tests with:

```bash
python -m unittest discover -s tests -v
```

## Moisture model

The educational model predicts moisture before irrigation:

```text
heat_loss = max(0, temperature - 25) × 0.1
before_irrigation = soil_moisture + rainfall × 0.5 - crop_demand - heat_loss
final_moisture = before_irrigation + irrigation_litres × 0.2
```

Values are capped to 0–100%. A pump can only supply whole pump-step amounts.
These coefficients illustrate algorithms; they are not agronomic advice.

## Greedy algorithm

For each day, Greedy checks only the current conditions. If predicted moisture
is below the minimum, it supplies enough water to reach the minimum plus a
safety margin, subject to daily supply and remaining shared budget.

```text
for each day:
    predict moisture before irrigation
    if it is below the minimum:
        allocate water to minimum + safety margin
```

Time complexity is **O(n)** and result storage is **O(n)**. It is easy to
explain and quick to execute, but extra safety water can be wasteful and early
days can consume water needed later.

## Dynamic Programming algorithm

The DP state is `dp[day][used_water_units]`; one unit equals the pump step. For
each day it considers two choices: skip irrigation, or apply the smallest
amount that reaches the minimum (when daily supply allows it).

Let `S(i, w)` be the best score after the first `i` days using `w` pump units:

```text
S(i, w) = best of:
  S(i-1, w) + score for skipping day i
  S(i-1, w-cost[i]) + score for making day i safe
```

Plans are ordered lexicographically: (1) maximise safe days, (2) favour more
critical dry/hot days, and (3) minimise water among equal plans. Complexity is
**O(nB)** time and **O(B)** active-state space, where `B` is the budget measured
in pump units. Result allocations require **O(n)** additional space.

## Default trace

With the bundled CSV, the pre-irrigation moistures are 30, 28, 28, 27, 28, 27,
28, 27, 28, and 27%. The 30% day needs no water. DP gives 10 L to each 28% day
and 15 L to each 27% day, totalling **110 L**. Greedy targets the configured 31%
safety level, adding one 5 L pump step on each dry day, totalling **155 L**.
Both keep all ten days at or above the default 30% minimum.

| Property | Greedy | Dynamic Programming |
|---|---|---|
| View of the problem | Current day | Whole schedule |
| Default water | 155 L | 110 L |
| Default safe days | 10/10 | 10/10 |
| Time | O(n) | O(nB) |
| Main strength | Simple and fast | Budget-aware optimum for this model |
| Main weakness | Can spend extra/early | More computation and memory |

## Project structure

```text
app.py                         Flask routes, validation, CSV loading
algorithms/greedy.py           Current-day Greedy strategy
algorithms/dynamic_programming.py  Multi-day DP strategy
algorithms/common.py           Shared moisture calculations
data/irrigation_data.csv       Offline default data
templates/                     Dashboard, schedule, comparison, base layout
static/css/style.css           Responsive styling
static/js/script.js            Editable rows and canvas chart
tests/test_algorithms.py       Baseline and route checks
VIVA_GUIDE.md                  Complete presentation and viva explanation
```

For a step-by-step explanation of the input flow, validation, formulas,
algorithms, output pages, UI, worked example, and common questions, read
[`VIVA_GUIDE.md`](VIVA_GUIDE.md).

## Limitations

- It does not connect to real sensors, pumps, forecasts, or a database.
- Model coefficients and daily rows are simplified and independent; moisture is
  not carried from one day to the next.
- The DP waters a day only by the minimum amount needed to be safe. It does not
  model uncertain forecasts, crop growth stages, runoff, or soil type.
- Flask's default development server and local session key are for demonstration,
  not production deployment.

## Viva questions

1. **Why compare Greedy and DP?** Greedy shows a fast local choice; DP shows how
   considering a shared constraint over all days can improve the plan.
2. **What is the DP state?** Day index and total pump units used so far.
3. **Why discretise water?** Real pumps operate in steps, and finite units make
   the budget suitable for a table-based DP.
4. **What is optimal here?** The lexicographic objective: most safe days, then
   the greatest critical-day score, then least water.
5. **Why does Greedy use more water in the sample?** It adds a safety margin to
   every dry day; DP only reaches the required minimum.
6. **Can DP ever leave a day dry?** Yes. With a tight budget it selects the set
   of days that maximises the objective.
7. **How could this become realistic?** Calibrate coefficients using soil and
   crop data, carry moisture between days, and connect verified sensors and
   forecast services.
