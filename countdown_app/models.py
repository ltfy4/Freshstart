"""Core data structures and helper functions for countdown plans."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Mapping, Optional


def _coerce_date(value: date | datetime | str) -> date:
    """Convert a variety of date-like values into a :class:`datetime.date`."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise TypeError(f"Unsupported date value: {value!r}")


@dataclass
class CountdownPlan:
    """Represents a countdown plan with progress tracking."""

    name: str
    start_date: date
    duration_days: int
    goal_metrics: Dict[str, float]
    progress_log: List["ProgressEntry"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.start_date = _coerce_date(self.start_date)
        processed: list[ProgressEntry] = []
        for entry in self.progress_log:
            if isinstance(entry, ProgressEntry):
                processed.append(entry)
            else:
                processed.append(ProgressEntry.from_mapping(entry))
        self.progress_log = processed

    @property
    def end_date(self) -> date:
        """Return the date on which the plan is scheduled to end."""
        return self.start_date + timedelta(days=self.duration_days)

    def remaining_days(self, as_of: Optional[date | datetime] = None) -> int:
        """Return the number of days remaining (never less than zero)."""
        today = _coerce_date(as_of or date.today())
        remaining = (self.end_date - today).days
        return max(0, remaining)

    def days_elapsed(self, as_of: Optional[date | datetime] = None) -> int:
        """Return the number of days that have elapsed since the plan started."""
        today = _coerce_date(as_of or date.today())
        elapsed = (today - self.start_date).days
        return max(0, elapsed)

    def log_progress(self, entry_date: date | datetime | str, metrics: Mapping[str, float]) -> None:
        """Record a daily progress entry for the plan."""
        entry = ProgressEntry(date=_coerce_date(entry_date), metrics=dict(metrics))
        self.progress_log.append(entry)

    def aggregate_progress(self) -> Dict[str, float]:
        """Aggregate the cumulative progress for each metric."""
        totals: Dict[str, float] = {metric: 0.0 for metric in self.goal_metrics}
        for entry in self.progress_log:
            for key, value in entry.metrics.items():
                totals[key] = totals.get(key, 0.0) + float(value)
        return totals

    def progress_percentages(self) -> Dict[str, float]:
        """Return the percentage completion for each metric (0-100)."""
        totals = self.aggregate_progress()
        percentages: Dict[str, float] = {}
        for metric, goal in self.goal_metrics.items():
            if goal == 0:
                percentages[metric] = 100.0 if totals.get(metric, 0.0) >= 0 else 0.0
            else:
                percentages[metric] = max(0.0, min(100.0, (totals.get(metric, 0.0) / goal) * 100))
        return percentages


@dataclass
class ProgressEntry:
    """Represents a daily progress update for a plan."""

    date: date
    metrics: Dict[str, float]

    def __post_init__(self) -> None:
        self.date = _coerce_date(self.date)
        self.metrics = {key: float(value) for key, value in self.metrics.items()}

    def to_dict(self) -> Dict[str, object]:
        return {"date": self.date.isoformat(), "metrics": self.metrics}

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "ProgressEntry":
        return cls(date=_coerce_date(data["date"]), metrics=dict(data["metrics"]))


def summarize_progress(plan: CountdownPlan) -> Dict[str, object]:
    """Return a dictionary summarising the current state of the plan."""
    return {
        "name": plan.name,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "duration_days": plan.duration_days,
        "days_elapsed": plan.days_elapsed(),
        "remaining_days": plan.remaining_days(),
        "progress_totals": plan.aggregate_progress(),
        "progress_percentages": plan.progress_percentages(),
    }
