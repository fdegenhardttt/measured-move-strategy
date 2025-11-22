import argparse
import matplotlib.pyplot as plt
import pandas as pd
from data_loader import fetch_data
from strategy import MeasuredMoveStrategy

def plot_results(df, pivots, moves, symbol):
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
        # We don't have a time for Target, so we just draw a horizontal line or a projected vector
        # Let's draw a horizontal line at the target level
        plt.axhline(y=move.projected_target, color=color, linestyle=':', alpha=0.8)
        plt.text(df.index[-1], move.projected_target, f"Target: {move.projected_target:.2f}", 
                 color=color, verticalalignment='center')
        
        # Annotate A, B, C
        plt.text(move.start_idx, move.start_price, "A", fontsize=12, fontweight='bold')
        plt.text(move.mid_idx, move.mid_price, "B", fontsize=12, fontweight='bold')
        plt.text(move.end_idx, move.end_price, "C", fontsize=12, fontweight='bold')

    plt.title(f"Measured Move Strategy Analysis: {symbol}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("strategy_output.png")
    print("Chart saved to strategy_output.png")

def main():
    parser = argparse.ArgumentParser(description="Measured Move Strategy Analyzer")
    parser.add_argument("--symbol", type=str, default="SPY", help="Ticker symbol (default: SPY)")
    parser.add_argument("--period", type=str, default="5y", help="Data period (default: 5y)")
    parser.add_argument("--multiplier", type=float, default=6.0, help="ATR Multiplier for sensitivity (default: 6.0)")
    parser.add_argument("--min_bars", type=int, default=20, help="Minimum bars between pivots (default: 20)")
    args = parser.parse_args()
    
    try:
        # 1. Fetch Data
        df = fetch_data(args.symbol, period=args.period)
        
        # 2. Run Strategy
        strategy = MeasuredMoveStrategy(args.symbol, df)
        strategy.analyze(atr_multiplier=args.multiplier, min_bars=args.min_bars) # Dynamic sensitivity
        
        # 3. Report
        moves = strategy.get_active_moves()
        print(f"\nAnalysis for {args.symbol}:")
        print(f"Found {len(moves)} recent measured move patterns.")
        
        for i, move in enumerate(moves):
            print(f"\nPattern {i+1} ({move.direction}):")
            print(f"  A: {move.start_idx.date()} @ {move.start_price:.2f}")
            print(f"  B: {move.mid_idx.date()} @ {move.mid_price:.2f}")
            print(f"  C: {move.end_idx.date()} @ {move.end_price:.2f}")
            print(f"  Target: {move.projected_target:.2f}")
            
        # 4. Visualize
        plot_results(df, strategy.pivots, moves, args.symbol)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
