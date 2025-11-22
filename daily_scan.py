import argparse
import pandas as pd
from datetime import datetime
from data_loader import fetch_data
from strategy import MeasuredMoveStrategy
from market_data import DOW_30, NASDAQ_100
from report_generator import generate_html_report
import time

def run_daily_scan(proximity_threshold: float = 5.0):
    """
    Scans Dow 30 and Nasdaq 100 for setups close to Target D.
    Generates an HTML report.
    """
    print(f"Starting Daily Scan: {datetime.now()}")
    
    # Combine lists and remove duplicates
    symbols = list(set(DOW_30 + NASDAQ_100))
    print(f"Scanning {len(symbols)} symbols...")
    
    results = []
    
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] Analyzing {symbol}...", end="\r")
        try:
            # Use default global settings: 5y daily data
            df = fetch_data(symbol, period="5y", interval="1d")
            strategy = MeasuredMoveStrategy(symbol, df)
            # Default strategy settings
            strategy.analyze(atr_multiplier=6.0, min_bars=20, strict_fib=True)
            
            moves = strategy.get_active_moves()
            
            for move in moves:
                # Filter by Proximity to D
                if move.proximity_to_d_pct * 100 <= proximity_threshold:
                    results.append({
                        "Symbol": symbol,
                        "Direction": move.direction,
                        "Price": move.current_price_at_analysis,
                        "Target (D)": move.projected_target,
                        "Dist to Target %": move.proximity_to_d_pct * 100,
                        "DataFrame": df,
                        "Pivots": strategy.pivots,
                        "Moves": [move] # Just pass this specific move for clarity in report? Or all? Let's pass all for context.
                    })
                    
        except Exception as e:
            # print(f"Error {symbol}: {e}")
            pass
            
    print(f"\nScan Complete. Found {len(results)} opportunities.")
    
    # Generate Report
    report_file = generate_html_report(results)
    print(f"Report generated: {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=5.0, help="Max distance from Target D %")
    args = parser.parse_args()
    
    run_daily_scan(args.threshold)
