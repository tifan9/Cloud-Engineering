# Log Analyzer

A Python CLI tool that reads a log file and prints a clean summary - errors, warnings, most common failure, and when it all happened.

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

Download `log_analyzer.py` to your project directory. No installation steps required.

## Usage

## Quick Start

```bash
# Basic analysis
python log_analyzer.py -file app.log

# Filter by ERROR level only
python log_analyzer.py -file app.log --level ERROR

# Filter by time range
python log_analyzer.py -file app.log --from "2026-06-07 10:05" --to "2026-06-07 10:15"

# Export to CSV
python log_analyzer.py -file app.log -export summary.csv

# Combine all options
python log_analyzer.py -file app.log --level ERROR --from "2026-06-07 10:00" --to "2026-06-07 11:00" -export error_summary.csv