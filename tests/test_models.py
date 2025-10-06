from datetime import date

import pytest

from countdown_app.models import CountdownPlan, summarize_progress


def create_plan():
    return CountdownPlan(
        name="Launch",
        start_date=date(2023, 1, 1),
        duration_days=10,
        goal_metrics={"miles": 100.0, "sessions": 5},
    )


def test_remaining_days_and_elapsed():
    plan = create_plan()
    assert plan.remaining_days(date(2023, 1, 5)) == 6
    assert plan.days_elapsed(date(2023, 1, 5)) == 4
    assert plan.remaining_days(date(2023, 1, 15)) == 0


def test_progress_percentages():
    plan = create_plan()
    plan.log_progress(date(2023, 1, 1), {"miles": 20, "sessions": 1})
    plan.log_progress(date(2023, 1, 2), {"miles": 30})
    plan.log_progress(date(2023, 1, 3), {"sessions": 2})
    percentages = plan.progress_percentages()
    assert pytest.approx(percentages["miles"], rel=1e-3) == 50.0
    assert pytest.approx(percentages["sessions"], rel=1e-3) == 60.0


def test_summarize_progress_structure():
    plan = create_plan()
    plan.log_progress(date(2023, 1, 1), {"miles": 25})
    summary = summarize_progress(plan)
    assert summary["name"] == "Launch"
    assert summary["progress_totals"]["miles"] == 25
    assert "remaining_days" in summary
