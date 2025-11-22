import matplotlib.pyplot as plt
import pandas as pd
from data_loader import fetch_data
from strategy import MeasuredMoveStrategy
import os

# List of major stocks and indices
SYMBOLS = [
    "^GSPC", # S&P 500
    "^DJI",  # Dow Jones Industrial Average
    "^IXIC", # Nasdaq Composite
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "NVDA",  # Nvidia
    "AMZN",  # Amazon
    "GOOGL", # Alphabet
    "META",  # Meta
    "TSLA"   # Tesla
]

def plot_results(df, pivots, moves, symbol, filename):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='Close Price', color='black', alpha=0.6, linewidth=1)
    
    # Plot Pivots
    pivot_dates = pivots.dropna().index
    pivot_values = pivots.dropna().values
    plt.plot(pivot_dates, pivot_values, color='blue', linestyle='--', linewidth=1, label='ZigZag Pivots')
    plt.scatter(pivot_dates, pivot_values, color='red', s=20, zorder=5)
    
    # Plot Measured Moves
    for move in moves:
        color = 'green' if move.direction == "Bullish" else 'red'
        
        # Draw the A-B-C lines
        plt.plot([move.start_idx, move.mid_idx, move.end_idx], 
                 [move.start_price, move.mid_price, move.end_price], 
                 color=color, linewidth=2)
        
        # Draw Projection (C to Target)
        plt.axhline(y=move.projected_target, color=color, linestyle=':', alpha=0.8)
        plt.text(df.index[-1], move.projected_target, f"Target: {move.projected_target:.2f}", 
                 color=color, verticalalignment='center')
        
        # Annotate A, B, C
        plt.text(move.start_idx, move.start_price, "A", fontsize=12, fontweight='bold')
        plt.text(move.mid_idx, move.mid_price, "B", fontsize=12, fontweight='bold')
        plt.text(move.end_idx, move.end_price, "C", fontsize=12, fontweight='bold')

    plt.title(f"Measured Move Strategy: {symbol}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Saved chart to {filename}")

def run_batch():
    print(f"Starting batch analysis on {len(SYMBOLS)} symbols...")
    print("-" * 60)
    
    results = []
    
    for symbol in SYMBOLS:
        try:
            print(f"\nAnalyzing {symbol}...")
            # Fetch Data (5 years for global context)
            df = fetch_data(symbol, period="5y")
            
            # Run Strategy
            # Using global settings: Multiplier 6.0, Min Bars 20
            strategy = MeasuredMoveStrategy(symbol, df)
            strategy.analyze(atr_multiplier=6.0, min_bars=20)
            
            moves = strategy.get_active_moves()
            
            if moves:
                print(f"  Found {len(moves)} patterns.")
                for move in moves:
                    print(f"    {move.direction}: Target {move.projected_target:.2f}")
                    results.append({
                        "Symbol": symbol,
                        "Direction": move.direction,
                        "Target": move.projected_target,
                        "Current Price": df['close'].iloc[-1]
                    })
                
                # Generate Plot
                filename = f"chart_{symbol.replace('^', '')}.png"
                plot_results(df, strategy.pivots, moves, symbol, filename)
            else:
                print("  No patterns found.")
                
        except Exception as e:
            print(f"  Error analyzing {symbol}: {e}")
            
    print("\n" + "=" * 60)
    print("BATCH ANALYSIS COMPLETE")
    print("=" * 60)
    
    if results:
        print(f"{'Symbol':<10} | {'Direction':<10} | {'Price':<10} | {'Target':<10}")
        print("-" * 50)
        for res in results:
            print(f"{res['Symbol']:<10} | {res['Direction']:<10} | {res['Current Price']:<10.2f} | {res['Target']:<10.2f}")
    else:
        print("No active patterns found across all symbols.")

if __name__ == "__main__":
    run_batch()
