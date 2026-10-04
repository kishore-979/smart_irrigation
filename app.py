"""Flask entry point for the Smart Irrigation Scheduling mini project."""

import csv
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

from algorithms.dynamic_programming import dynamic_programming_schedule
from algorithms.greedy import greedy_schedule

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = BASE_DIR / "data" / "irrigation_data.csv"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "college-mini-project-local-key")

DEFAULT_SETTINGS = {
    "minimum_moisture": 30.0,
    "safety_margin": 1.0,
    "water_budget": 200,
    "pump_step": 5,
    "irrigation_gain": 0.2,
}


def load_sample_data():
    with SAMPLE_FILE.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return [
        {
            "day": row["day"],
            "soil_moisture": float(row["soil_moisture"]),
            "temperature": float(row["temperature"]),
            "rainfall": float(row["rainfall"]),
            "crop_requirement": float(row["crop_requirement"]),
            "available_water": int(float(row["available_water"])),
        }
        for row in rows
    ]


def _number(form, name, index=None):
    key = f"{name}_{index}" if index is not None else name
    value = form.get(key, "").strip()
    if value == "":
        raise ValueError(f"{name.replace('_', ' ').title()} is required.")
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"{name.replace('_', ' ').title()} must be a number.") from error


def parse_form(form):
    count = int(_number(form, "day_count"))
    if not 1 <= count <= 14:
        raise ValueError("The schedule must contain between 1 and 14 days.")

    settings = {
        "minimum_moisture": _number(form, "minimum_moisture"),
        "safety_margin": _number(form, "safety_margin"),
        "water_budget": int(_number(form, "water_budget")),
        "pump_step": int(_number(form, "pump_step")),
        "irrigation_gain": DEFAULT_SETTINGS["irrigation_gain"],
    }
    if not 1 <= settings["minimum_moisture"] <= 90:
        raise ValueError("Minimum moisture must be between 1 and 90%.")
    if not 0 <= settings["safety_margin"] <= 20:
        raise ValueError("Safety margin must be between 0 and 20 percentage points.")
    if settings["water_budget"] < 0:
        raise ValueError("Water budget cannot be negative.")
    if settings["pump_step"] not in (1, 5, 10):
        raise ValueError("Pump step must be 1, 5, or 10 litres.")

    days = []
    for index in range(count):
        day = {
            "day": form.get(f"day_{index}", "").strip() or f"Day {index + 1}",
            "soil_moisture": _number(form, "soil_moisture", index),
            "temperature": _number(form, "temperature", index),
            "rainfall": _number(form, "rainfall", index),
            "crop_requirement": _number(form, "crop_requirement", index),
            "available_water": int(_number(form, "available_water", index)),
        }
        if not 0 <= day["soil_moisture"] <= 100:
            raise ValueError(f"{day['day']}: soil moisture must be between 0 and 100%.")
        if not -10 <= day["temperature"] <= 60:
            raise ValueError(f"{day['day']}: temperature must be between -10 and 60°C.")
        if min(day["rainfall"], day["crop_requirement"], day["available_water"]) < 0:
            raise ValueError(f"{day['day']}: rainfall, crop demand, and water cannot be negative.")
        days.append(day)
    return days, settings


def totals(results):
    return {
        "water": sum(row["irrigation"] for row in results),
        "safe_days": sum(row["safe"] for row in results),
    }


@app.get("/")
def dashboard():
    return render_template(
        "dashboard.html", days=load_sample_data(), settings=DEFAULT_SETTINGS
    )


@app.post("/schedule")
def schedule():
    try:
        days, settings = parse_form(request.form)
    except (ValueError, TypeError) as error:
        flash(str(error), "error")
        return redirect(url_for("dashboard"))

    greedy = greedy_schedule(days, settings)
    dynamic = dynamic_programming_schedule(days, settings)
    payload = {
        "greedy": greedy,
        "dynamic": dynamic,
        "settings": settings,
        "greedy_totals": totals(greedy),
        "dynamic_totals": totals(dynamic),
    }
    session["results"] = payload
    return render_template("schedule.html", **payload)


@app.get("/comparison")
def comparison():
    payload = session.get("results")
    if not payload:
        flash("Generate a schedule before opening the comparison.", "error")
        return redirect(url_for("dashboard"))
    return render_template("comparison.html", **payload)


if __name__ == "__main__":
    app.run(debug=True)
