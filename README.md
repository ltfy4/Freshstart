# Freshstart Countdown App

This repository contains a simple countdown planning utility with a command-line
interface for creating plans, logging daily performance, and reviewing progress
against goals.

## Setup

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install development dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   If a `requirements.txt` file is not available, install `pytest` manually for
   running the tests:

   ```bash
   pip install pytest
   ```

## Package Layout

```
countdown_app/
├── cli.py          # Command-line entry point
├── models.py       # Dataclasses and progress helpers
├── storage.py      # JSON persistence helpers
└── __init__.py
```

Daily plan data is stored under `data/plans.json` in JSON format.

## Usage

The CLI uses subcommands for creating plans, logging progress, and displaying a
summary.

Create a countdown plan with one or more goal metrics:

```bash
python -m countdown_app.cli create "Launch" 2023-10-01 30 \
  --goal miles=100 --goal sessions=10
```

Log performance for a specific date (use multiple `--metric` flags for each
metric you want to update):

```bash
python -m countdown_app.cli log "Launch" 2023-10-02 \
  --metric miles=5 --metric sessions=1
```

Display the current status and progress breakdown:

```bash
python -m countdown_app.cli status "Launch"
```

## Progress Calculations

Each plan tracks goal metrics (for example, total miles to run or number of
study sessions). Daily log entries accumulate the values for each metric. The
application sums all logged values per metric and compares them to the goal to
compute a completion percentage, capped between 0 and 100 percent.

The status command outputs:

- Total progress accumulated for each metric.
- Percentage completion toward the goals.
- Days elapsed since the start and remaining days until the scheduled end.

These metrics help you quickly understand how well you are tracking toward your
countdown objectives.

## Testing

Run the unit test suite with:

```bash
pytest
```
