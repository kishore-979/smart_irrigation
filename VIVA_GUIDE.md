# Smart Irrigation Project Viva Guide

This guide explains the complete project in simple language: what problem it
solves, how the user interface accepts data, how Flask validates and processes
that data, how the Greedy and Dynamic Programming algorithms work, and how the
final schedules and comparison are displayed.

## 1. Short introduction for the viva

You can begin with this answer:

> My project is called **Smart Irrigation Scheduling Using Greedy and Dynamic
> Programming Techniques**. It is an offline Flask web application that creates
> an irrigation schedule for 1 to 14 days. The user enters daily farm conditions
> and a shared water budget. The system runs both a Greedy algorithm and a
> Dynamic Programming algorithm, then compares their water usage and the number
> of days kept above the minimum soil-moisture target. The purpose is to
> demonstrate how a locally optimal decision can differ from a whole-period,
> budget-aware decision.

The application is an educational simulation. It is not connected to a real
weather service, sensor, or irrigation pump.

## 2. Problem being solved

A farmer has limited water and must decide how much water to use on each day.
The decision depends on:

- current soil moisture;
- temperature;
- expected rainfall;
- crop water requirement;
- water available on that specific day; and
- the total shared water budget.

The objective is to keep as many days as possible at or above the selected
minimum moisture level while avoiding unnecessary water use.

The project compares two approaches:

| Approach | Main idea |
|---|---|
| Greedy | Make an immediate decision for the current day. |
| Dynamic Programming | Consider all days and the shared budget together. |

## 3. Technology used

| Part | Technology | Purpose |
|---|---|---|
| Backend | Python and Flask | Routes, validation, algorithms, and page rendering |
| Frontend | HTML and Jinja templates | Page structure and dynamic server values |
| Styling | CSS | Responsive layout, cards, colours, and animations |
| Interactions | Vanilla JavaScript | Editable rows, information dialogs, live summaries, and chart |
| Input data | CSV and HTML form | Default sample and user-edited values |
| Temporary result storage | Flask session | Makes the latest result available on the comparison page |

No database, external weather API, frontend framework, or chart library is
required.

## 4. Main project files

```text
app.py
    Starts Flask, loads sample data, validates the form, runs both algorithms,
    calculates totals, stores results, and renders pages.

algorithms/common.py
    Contains the moisture formula, water-needed calculation, final-moisture
    calculation, and critical-day priority score.

algorithms/greedy.py
    Contains the day-by-day Greedy scheduling method.

algorithms/dynamic_programming.py
    Contains the shared-budget Dynamic Programming method.

data/irrigation_data.csv
    Contains the default offline ten-day sample.

templates/base.html
    Common navigation, footer, styles, scripts, and information dialog.

templates/dashboard.html
    Main input page and daily conditions table.

templates/schedule.html
    Displays both daily irrigation schedules.

templates/comparison.html
    Displays totals, water saved, explanations, and the chart.

static/css/style.css
    Responsive visual design and motion effects.

static/js/script.js
    Dynamic table rows, live values, insight dialogs, and canvas chart.
```

## 5. Complete application flow

```text
User opens dashboard
        ↓
Flask reads the sample CSV
        ↓
Dashboard displays settings and daily values
        ↓
User edits values and clicks Generate smart schedules
        ↓
Browser sends an HTTP POST request to /schedule
        ↓
Flask reads and validates every value
        ↓
Common moisture calculations are performed
        ↓
Greedy schedule is generated
        ↓
Dynamic Programming schedule is generated
        ↓
Total water and safe days are calculated
        ↓
Results are stored in the Flask session
        ↓
Schedule page displays both daily plans
        ↓
Comparison page displays totals, savings, chart, and explanation
```

## 6. Step 1: loading the dashboard

When the browser opens `/`, Flask calls the `dashboard()` function in
`app.py`.

The function performs two actions:

1. `load_sample_data()` reads `data/irrigation_data.csv` using Python's CSV
   module.
2. Flask passes the sample rows and default settings to `dashboard.html`.

The default settings are:

```text
Minimum moisture: 30%
Greedy safety margin: 1 percentage point
Shared water budget: 200 L
Pump step: 5 L
Irrigation gain: 0.2 moisture points per litre
```

Jinja template expressions such as `{{ days }}` are replaced by real Python
values before the HTML is sent to the browser.

## 7. Step 2: inputs taken from the user

### Main planning parameters

| Parameter | Meaning |
|---|---|
| Days | Number of consecutive days to schedule, from 1 to 14 |
| Minimum moisture | Lowest final soil moisture considered safe |
| Greedy safety margin | Extra moisture above the minimum used only by Greedy |
| Shared budget | Total water available across the complete schedule |
| Pump step | Smallest amount the pump can supply: 1 L, 5 L, or 10 L |

### Daily parameters

| Parameter | Meaning |
|---|---|
| Day | Display name such as Day 1 |
| Soil moisture | Moisture measured at the beginning of that day |
| Temperature | Expected daily temperature in degrees Celsius |
| Rainfall | Expected rainfall in millimetres |
| Crop requirement | Simplified daily moisture loss caused by crop demand |
| Available water | Maximum water that can be supplied on that day |

The main values and all daily rows are inside one HTML form. When the user
clicks **Generate smart schedules**, the browser sends the values to the
`/schedule` route using the POST method.

## 8. Step 3: input validation

The `parse_form()` function in `app.py` validates the submitted values before
an algorithm is allowed to run.

Important rules are:

- days must be between 1 and 14;
- minimum moisture must be between 1% and 90%;
- Greedy safety margin must be between 0 and 20 percentage points;
- water budget cannot be negative;
- pump step must be 1 L, 5 L, or 10 L;
- soil moisture must be between 0% and 100%;
- temperature must be between -10°C and 60°C; and
- rainfall, crop demand, and daily available water cannot be negative.

If a value is missing, not numeric, or outside its permitted range, Flask does
not run the algorithms. It redirects to the dashboard and displays an error
message. This prevents invalid data from producing misleading output.

## 9. Step 4: predicting moisture before irrigation

Both algorithms use exactly the same moisture model from
`algorithms/common.py`.

### Heat loss

```text
heat_loss = max(0, temperature - 25) × 0.1
```

Only temperature above 25°C adds heat loss.

### Rainfall gain

```text
rainfall_gain = rainfall × 0.5
```

### Moisture before irrigation

```text
base_moisture = soil_moisture + rainfall_gain
                - crop_requirement - heat_loss
```

The value is limited to the valid 0% to 100% range.

### Moisture gained from irrigation

```text
final_moisture = base_moisture + irrigation_litres × 0.2
```

The value `0.2` is the configured irrigation gain. In this simulation, every
litre increases moisture by 0.2 percentage points.

### Pump-step rounding

If the exact calculation requires 12 L and the pump step is 5 L, the system
rounds upward to 15 L. This represents a pump that operates only in complete
steps.

## 10. Worked example for one day

Consider Day 2 in the sample:

```text
Soil moisture = 32%
Temperature = 30°C
Rainfall = 1 mm
Crop requirement = 4
Minimum target = 30%
Greedy safety target = 30% + 1% = 31%
Pump step = 5 L
```

First calculate environmental effects:

```text
heat_loss = (30 - 25) × 0.1 = 0.5
rainfall_gain = 1 × 0.5 = 0.5
base_moisture = 32 + 0.5 - 4 - 0.5 = 28%
```

Greedy aims for 31%:

```text
moisture required = 31 - 28 = 3 points
water required = 3 ÷ 0.2 = 15 L
final moisture = 28 + (15 × 0.2) = 31%
```

Dynamic Programming only needs to reach 30%:

```text
moisture required = 30 - 28 = 2 points
water required = 2 ÷ 0.2 = 10 L
final moisture = 28 + (10 × 0.2) = 30%
```

This single day shows why Greedy can use more water: its safety margin raises
the target from 30% to 31%.

## 11. Step 5: Greedy algorithm processing

The Greedy method processes days from first to last.

For each day it:

1. calculates moisture before irrigation;
2. checks whether that moisture is below the minimum;
3. if irrigation is needed, targets minimum moisture plus the safety margin;
4. rounds the required water to the pump step;
5. limits the amount by the day's available water;
6. limits it again by the remaining shared budget;
7. subtracts the allocation from the remaining budget;
8. calculates final moisture; and
9. marks the day as safe or below target.

The important characteristic is that it does not reserve water for future
days. It chooses what looks suitable now and then moves to the next day.

### Greedy pseudocode

```text
remaining_budget = shared_budget

for each day:
    calculate base moisture

    if base moisture is below minimum:
        calculate water for minimum + safety margin
    else:
        water = 0

    limit water by daily availability and remaining budget
    round to a complete pump step
    update remaining budget
    calculate final moisture and safety status
```

### Greedy complexity

- Time complexity: **O(n)** because each day is processed once.
- Result space: **O(n)** because one result record is stored per day.

## 12. Step 6: Dynamic Programming processing

Dynamic Programming treats all days as one shared-budget problem.

Its state is:

```text
dp[day][used_water_units]
```

One water unit equals the selected pump step. For example, with a 5 L pump
step, a 200 L budget contains 40 DP units.

For each day, DP considers two choices:

1. **Skip:** give the day no irrigation.
2. **Irrigate:** give it the smallest pump-step amount that reaches the minimum.

The irrigation choice is allowed only when:

- the day is not already safe;
- daily available water is sufficient; and
- the new total remains within the shared budget.

### How the best plan is selected

Plans are compared in this order:

1. maximise the number of safe days;
2. if safe days are equal, prefer critical dry and hot days; and
3. if both are still equal, use the least water.

The critical-day priority is:

```text
priority = 1 + dryness + heat contribution
```

This tie-breaker matters when a limited budget cannot make every day safe.

### DP recurrence in simple form

```text
best(day, used water) = better of:
    previous best plan + skip current day
    previous best plan + irrigate current day
```

After the final day, the code selects the best state and reads its stored daily
allocations to build the result table.

### Dynamic Programming complexity

- Time complexity: **O(nB)** in the standard DP model.
- Active DP state space: **O(B)**.
- `n` is the number of days.
- `B` is the shared budget measured in pump units.

## 13. Step 7: creating the output

Each algorithm returns one result dictionary for every day. A result contains:

```text
original daily input values
moisture before irrigation
irrigation amount in litres
final moisture
safe or below-target status
```

The `totals()` function then calculates:

- total irrigation water; and
- total number of safe days.

The `/schedule` route places the following information into one payload:

```text
Greedy daily results
DP daily results
submitted settings
Greedy totals
DP totals
```

This payload is sent to `schedule.html` and also stored in the Flask session.
The session lets `/comparison` reuse the latest result without running the
algorithms again.

## 14. Output pages

### Schedule page

The schedule page shows two tables:

- Greedy strategy; and
- Dynamic Programming strategy.

Each table shows the day, moisture before irrigation, allocated water, final
moisture, and safety status. It also displays total water and total safe days.

An insight bar automatically shows how many fewer litres DP used than Greedy.

### Comparison page

The comparison page displays:

- Greedy total water;
- DP total water;
- safe days for both methods;
- water saved by DP;
- an animated daily allocation chart; and
- a written explanation of why the two results differ.

The chart is drawn using the HTML Canvas API in vanilla JavaScript. No chart
library or internet connection is required.

## 15. User interface explanation

### Base layout

`base.html` provides the common header, navigation, footer, stylesheet,
JavaScript file, and reusable insight dialog. Other templates extend this base
so repeated UI code is kept in one place.

### Dashboard design

The dashboard contains:

- an animated smart-field illustration;
- a three-step journey showing input, processing, and comparison;
- five planning cards with descriptions;
- clickable information icons with detailed explanations and viva tips;
- a live display of selected days and water budget;
- an editable daily-input table; and
- a clear button for generating the schedules.

### JavaScript interactions

`static/js/script.js` performs four frontend tasks:

1. adds or removes daily rows when the number of days changes;
2. updates the live days and budget summary;
3. opens and fills the information dialog when an `i` icon is clicked; and
4. draws the Greedy-versus-DP comparison chart.

JavaScript improves the user experience, but the actual irrigation algorithms
run in Python on the Flask server.

### CSS and motion

`static/css/style.css` provides the colour system, responsive grids, cards,
tables, dialog design, sprinkler and rain animation, hover states, and mobile
layout. A `prefers-reduced-motion` rule disables long animations for users who
request reduced motion in their operating system.

## 16. Default result and trace

The sample contains ten days. Their moisture values before irrigation are:

```text
30, 28, 28, 27, 28, 27, 28, 27, 28, 27 percent
```

- Day 1 is already at 30%, so neither method waters it.
- A 28% day needs 10 L to reach 30%.
- A 27% day needs 15 L to reach 30%.
- DP therefore uses **110 L** in total.
- Greedy targets 31% because of the 1% safety margin.
- Greedy uses one additional 5 L step on every dry day and totals **155 L**.
- Both methods keep **10 out of 10 days safe**.
- DP saves **45 L** in the default example.

## 17. Why use both algorithms

Greedy is useful because it is simple, fast, and easy to implement. However,
it makes local decisions and may spend extra water early.

Dynamic Programming is useful because it handles the shared budget across the
whole schedule and produces the best plan according to the project's objective.
Its disadvantage is higher time and memory usage.

The project is not claiming that DP is always better for every possible
irrigation system. It demonstrates that when decisions share a limited
resource, considering the complete period can improve allocation.

## 18. Error handling and special cases

- If the comparison page is opened before generating a schedule, the user is
  redirected to the dashboard with a message.
- If a day is already above the minimum, it can remain safe with 0 L.
- If daily water is lower than the required pump-step allocation, DP cannot use
  that irrigation choice for the day.
- If the total budget is too small, some days may remain below target.
- Greedy never spends more than the daily availability or remaining budget.
- Final moisture is capped at 100%.

## 19. Limitations

Be honest about these points in the viva:

- The moisture formula is simplified for algorithm demonstration.
- Daily soil moisture is entered independently; unused moisture is not carried
  forward into the next day's input.
- The app does not use live sensors, pumps, soil types, crop growth stages, or
  weather forecasts.
- Model coefficients are educational assumptions, not agronomic advice.
- Results are stored temporarily in the Flask session, not a database.
- The Flask development server is suitable for a demonstration, not production.

## 20. Possible future improvements

- Connect real soil-moisture sensors using IoT devices.
- Fetch a trusted weather forecast through an API.
- Carry remaining soil moisture from one day to the next.
- Use different coefficients for crop type, soil type, and crop-growth stage.
- Add user accounts and a database for farm history.
- Send automatic pump instructions and alerts.
- Compare more methods, such as linear programming or machine learning.
- Evaluate cost, electricity usage, and rainfall uncertainty.

## 21. Common viva questions and answers

### Why did you choose Flask?

Flask is lightweight, easy to understand, and suitable for a college mini
project. It connects Python algorithms to HTML pages with very little setup.

### What is the difference between Greedy and DP?

Greedy chooses for the current day without examining all future combinations.
DP compares choices across the complete schedule under the shared budget.

### What is the DP state?

The state is the current day and the number of pump-step water units already
used: `dp[day][used_water_units]`.

### Why is water divided into pump steps?

Real pumps supply measurable quantities rather than infinitely small values.
Discrete steps also make the budget finite and suitable for Dynamic
Programming.

### What makes a day safe?

A day is safe when its final predicted moisture is greater than or equal to the
minimum moisture selected by the user.

### Why does Greedy use 155 L while DP uses 110 L?

Greedy aims one percentage point above the minimum because of its safety
margin. With a 5 L pump step, that adds one extra step on each dry day. DP only
uses the amount needed to reach the minimum.

### Does DP always use less water?

Not necessarily for every input. Its first objective is maximum safe days. It
minimises water only among plans that are otherwise equally good.

### What happens when the budget is insufficient?

DP selects the combination that keeps the most days safe and uses its priority
score to favour more critical dry or hot days. Greedy continues in day order
until its remaining budget is insufficient.

### Why is the complexity of DP O(nB)?

It considers up to `B` budget states for each of `n` days. Greedy only visits
each day once, so it is O(n).

### Is the chart created using a library?

No. JavaScript draws it directly using the HTML Canvas API, keeping the project
offline and easy to explain.

### Where are results stored?

The latest result payload is stored temporarily in the Flask session so the
comparison route can display it.

### How did you test the project?

The automated tests verify the documented 155 L and 110 L totals, confirm DP
respects a tight budget, and check the dashboard, schedule, and comparison
routes.

## 22. Suggested live demonstration

Follow this order during the viva:

1. Open the dashboard and state the project objective.
2. Point to the five planning parameters and click one information icon.
3. Explain one row of daily farm conditions.
4. Keep the default data and click **Generate smart schedules**.
5. Show the Greedy total of 155 L and DP total of 110 L.
6. Point out that both maintain 10 safe days.
7. Open the comparison page and show the 45 L saving and daily chart.
8. Return to the dashboard, reduce the shared budget, and explain that this
   tests how both methods behave under scarcity.
9. End by mentioning the simplified model and future sensor integration.

## 23. Final summary to say

> The application takes validated farm and water inputs, converts them into a
> predicted pre-irrigation moisture value, and passes the same data to both
> algorithms. Greedy makes quick day-by-day decisions with a safety margin,
> while Dynamic Programming searches across day and budget states. Flask then
> calculates totals and renders the schedules and comparison. In the default
> case, both keep all ten days safe, but DP uses 110 litres instead of 155,
> demonstrating the benefit of planning a shared resource across the full
> period.
