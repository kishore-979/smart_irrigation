import unittest

from app import DEFAULT_SETTINGS, app, load_sample_data, totals
from algorithms.dynamic_programming import dynamic_programming_schedule
from algorithms.greedy import greedy_schedule


class AlgorithmTests(unittest.TestCase):
    def test_documented_default_totals(self):
        days = load_sample_data()
        greedy = greedy_schedule(days, DEFAULT_SETTINGS)
        dynamic = dynamic_programming_schedule(days, DEFAULT_SETTINGS)
        self.assertEqual(totals(greedy), {"water": 155, "safe_days": 10})
        self.assertEqual(totals(dynamic), {"water": 110, "safe_days": 10})

    def test_dp_respects_tight_budget(self):
        settings = {**DEFAULT_SETTINGS, "water_budget": 25}
        result = dynamic_programming_schedule(load_sample_data(), settings)
        self.assertLessEqual(totals(result)["water"], 25)

    def test_dashboard_loads(self):
        with app.test_client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Smart Irrigation", response.data)

    def test_schedule_and_comparison_routes(self):
        days = load_sample_data()
        form = {
            "day_count": str(len(days)),
            "minimum_moisture": "30",
            "safety_margin": "1",
            "water_budget": "200",
            "pump_step": "5",
        }
        for index, day in enumerate(days):
            for field, value in day.items():
                form[f"{field}_{index}"] = str(value)
        with app.test_client() as client:
            schedule = client.post("/schedule", data=form)
            comparison = client.get("/comparison")
            self.assertEqual(schedule.status_code, 200)
            self.assertIn(b"155 L total", schedule.data)
            self.assertIn(b"110 L total", schedule.data)
            self.assertEqual(comparison.status_code, 200)
            self.assertIn(b"45 L", comparison.data)


if __name__ == "__main__":
    unittest.main()
