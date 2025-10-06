"""Command-line interface for managing countdown plans."""
from __future__ import annotations

import argparse
from datetime import date
from typing import Dict

from .models import CountdownPlan, summarize_progress
from .storage import append_progress, load_plans, save_plans


def _parse_metrics(pairs: list[str]) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError("Metrics must be in key=value format")
        key, value = pair.split("=", 1)
        try:
            metrics[key] = float(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Invalid numeric value for '{key}': {value}") from exc
    return metrics


def _parse_date(value: str) -> str:
    # Validate ISO date format without storing as date object (to keep argparse simple).
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must be in ISO format YYYY-MM-DD") from exc
    return value


def cmd_create(args: argparse.Namespace) -> None:
    plans = load_plans()
    if args.name in plans:
        raise SystemExit(f"Plan '{args.name}' already exists")
    plan = CountdownPlan(
        name=args.name,
        start_date=args.start_date,
        duration_days=args.duration,
        goal_metrics=args.goal,
    )
    plans[plan.name] = plan
    save_plans(plans)
    print(f"Created plan '{plan.name}' starting {plan.start_date.isoformat()} for {plan.duration_days} days")


def cmd_log(args: argparse.Namespace) -> None:
    plan = append_progress(args.name, args.date, args.metric)
    print(f"Logged progress for '{plan.name}' on {args.date}")


def cmd_status(args: argparse.Namespace) -> None:
    plans = load_plans()
    if args.name not in plans:
        raise SystemExit(f"Plan '{args.name}' does not exist")
    plan = plans[args.name]
    summary = summarize_progress(plan)
    print(f"Plan: {summary['name']}")
    print(f"Start: {summary['start_date']} | End: {summary['end_date']}")
    print(f"Duration: {summary['duration_days']} days")
    print(f"Days elapsed: {summary['days_elapsed']} | Remaining: {summary['remaining_days']}")
    print("Progress totals:")
    for metric, value in summary["progress_totals"].items():
        print(f"  - {metric}: {value:.2f}")
    print("Progress percentages:")
    for metric, value in summary["progress_percentages"].items():
        print(f"  - {metric}: {value:.1f}%")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Countdown plan manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a new countdown plan")
    create.add_argument("name", help="Unique name of the plan")
    create.add_argument("start_date", type=_parse_date, help="Start date (YYYY-MM-DD)")
    create.add_argument("duration", type=int, help="Duration in days")
    create.add_argument(
        "--goal",
        metavar="metric=value",
        action="append",
        default=[],
        help="Goal metrics for the plan (can be used multiple times)",
    )
    create.set_defaults(func=cmd_create)

    log = subparsers.add_parser("log", help="Log daily performance for a plan")
    log.add_argument("name", help="Name of the plan")
    log.add_argument("date", type=_parse_date, help="Date of the log entry (YYYY-MM-DD)")
    log.add_argument(
        "--metric",
        metavar="metric=value",
        action="append",
        default=[],
        help="Metric value for the day (can be used multiple times)",
    )
    log.set_defaults(func=cmd_log)

    status = subparsers.add_parser("status", help="Display plan status")
    status.add_argument("name", help="Name of the plan")
    status.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Normalise optional arguments to dicts
    args.goal = _parse_metrics(args.goal) if hasattr(args, "goal") else {}
    args.metric = _parse_metrics(args.metric) if hasattr(args, "metric") else {}
    args.func(args)


if __name__ == "__main__":
    main()
