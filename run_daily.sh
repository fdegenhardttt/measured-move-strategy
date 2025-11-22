#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate virtual environment if you have one (optional)
# source venv/bin/activate

# Run the daily scan
# Threshold 5.0 means we look for setups within 5% of the Target D
/usr/local/bin/python3 daily_scan.py --threshold 5.0

# Optional: Open the report automatically (macOS)
# open daily_report_*.html
