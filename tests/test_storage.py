from datetime import date

import pytest

from countdown_app.models import CountdownPlan
from countdown_app import storage


def sample_plan() -> CountdownPlan:
    plan = CountdownPlan(
        name="Build",
        start_date=date(2023, 2, 1),
        duration_days=5,
        goal_metrics={"tasks": 10},
    )
    plan.log_progress(date(2023, 2, 1), {"tasks": 2})
    return plan


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "plans.json"
    plan = sample_plan()
    storage.save_plans({plan.name: plan}, path)
    loaded = storage.load_plans(path)
    assert plan.name in loaded
    restored = loaded[plan.name]
    assert restored.goal_metrics == plan.goal_metrics
    assert restored.aggregate_progress()["tasks"] == 2


def test_append_progress(tmp_path):
    path = tmp_path / "plans.json"
    plan = sample_plan()
    storage.save_plans({plan.name: plan}, path)
    updated = storage.append_progress(plan.name, "2023-02-02", {"tasks": 3}, path)
    assert len(updated.progress_log) == 2
    reloaded = storage.load_plans(path)
    assert reloaded[plan.name].aggregate_progress()["tasks"] == 5


def test_append_progress_missing_plan(tmp_path):
    path = tmp_path / "plans.json"
    with pytest.raises(KeyError):
        storage.append_progress("missing", "2023-02-01", {"tasks": 1}, path)
