import plotly.graph_objects as go
import pandas as pd

def plot_interactive_chart(df: pd.DataFrame, pivots: pd.Series, moves: list, symbol: str):
    """
    Creates an interactive Plotly candlestick chart with pivots and measured moves.
    """
    fig = go.Figure()

    # 1. Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ))

    # 2. Pivots (ZigZag)
    pivot_dates = pivots.dropna().index
    pivot_values = pivots.dropna().values
    
    if len(pivot_dates) > 0:
        fig.add_trace(go.Scatter(
            x=pivot_dates,
            y=pivot_values,
            mode='lines+markers',
            name='ZigZag Pivots',
            line=dict(color='blue', width=1, dash='dash'),
            marker=dict(color='blue', size=5)
        ))

    # 3. Measured Moves
    for i, move in enumerate(moves):
        color = 'green' if move.direction == "Bullish" else 'red'
        
        # A-B-C Path
        fig.add_trace(go.Scatter(
            x=[move.start_idx, move.mid_idx, move.end_idx],
            y=[move.start_price, move.mid_price, move.end_price],
            mode='lines+markers+text',
            name=f'Pattern {i+1} ({move.direction})',
            line=dict(color=color, width=3),
            marker=dict(size=8),
            text=["A", "B", "C"],
            textposition="top center"
        ))
        
        # Projection Line (C to Target)
        # We need a way to show the target. Since x-axis is time, we can just draw a horizontal line
        # extending from C to the right.
        
        fig.add_hline(
            y=move.projected_target, 
            line_dash="dot", 
            line_color=color,
            annotation_text=f"Target: {move.projected_target:.2f}",
            annotation_position="top right"
        )

    fig.update_layout(
        title=f'Measured Move Analysis: {symbol}',
        yaxis_title='Price',
        xaxis_title='Date',
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=600
    )
    
    return fig
