"""Persistence helpers for countdown plans."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Mapping

from .models import CountdownPlan, ProgressEntry

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PLANS_PATH = DATA_DIR / "plans.json"


def _ensure_data_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_plans(path: Path = PLANS_PATH) -> Dict[str, CountdownPlan]:
    """Load countdown plans from the given JSON file."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    plans: Dict[str, CountdownPlan] = {}
    for plan_data in raw.get("plans", []):
        plan = CountdownPlan(
            name=plan_data["name"],
            start_date=plan_data["start_date"],
            duration_days=plan_data["duration_days"],
            goal_metrics=dict(plan_data.get("goal_metrics", {})),
            progress_log=[ProgressEntry.from_mapping(entry) for entry in plan_data.get("progress_log", [])],
        )
        plans[plan.name] = plan
    return plans


def save_plans(plans: Mapping[str, CountdownPlan], path: Path = PLANS_PATH) -> None:
    """Persist countdown plans to disk."""
    _ensure_data_dir(path)
    serialised = {
        "plans": [
            {
                "name": plan.name,
                "start_date": plan.start_date.isoformat(),
                "duration_days": plan.duration_days,
                "goal_metrics": plan.goal_metrics,
                "progress_log": [entry.to_dict() for entry in plan.progress_log],
            }
            for plan in plans.values()
        ]
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(serialised, fh, indent=2)


def upsert_plan(plan: CountdownPlan, path: Path = PLANS_PATH) -> None:
    """Insert or update a plan in persistent storage."""
    plans = load_plans(path)
    plans[plan.name] = plan
    save_plans(plans, path)


def append_progress(
    plan_name: str,
    entry_date: str,
    metrics: Mapping[str, float],
    path: Path = PLANS_PATH,
) -> CountdownPlan:
    """Append a progress entry to the plan and persist the change."""
    plans = load_plans(path)
    if plan_name not in plans:
        raise KeyError(f"Plan '{plan_name}' does not exist")
    plan = plans[plan_name]
    plan.log_progress(entry_date, metrics)
    save_plans(plans, path)
    return plan
