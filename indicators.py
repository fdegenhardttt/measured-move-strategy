import numpy as np
import pandas as pd

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates Average True Range (ATR).
    """
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def zigzag_pivots(df: pd.DataFrame, deviation_pct: float, min_bars: int = 0) -> tuple[pd.Series, pd.Series]:
    """
    Identifies ZigZag pivots based on a percentage deviation.
    
    Args:
        df: DataFrame with 'high' and 'low' columns.
        deviation_pct: Minimum percentage change to qualify as a new pivot.
        min_bars: Minimum number of bars between pivots to be considered valid.
        
    Returns:
        tuple: (pivot_values, pivot_types)
    """
    highs = df['high'].values
    lows = df['low'].values
    
    n = len(df)
    
    # Current trend state
    trend = 0 # 1: up, -1: down
    last_high_idx = 0
    last_low_idx = 0
    last_high = highs[0]
    last_low = lows[0]
    
    pivots = [] # List of (index, type, value)
    
    for i in range(1, n):
        curr_high = highs[i]
        curr_low = lows[i]
        
        if trend == 0:
            if curr_high > last_low * (1 + deviation_pct):
                trend = 1 # Up trend confirmed
                # We found a bottom at last_low_idx
                pivots.append((last_low_idx, -1, last_low))
                last_high_idx = i
                last_high = curr_high
            elif curr_low < last_high * (1 - deviation_pct):
                trend = -1 # Down trend confirmed
                # We found a top at last_high_idx
                pivots.append((last_high_idx, 1, last_high))
                last_low_idx = i
                last_low = curr_low
            else:
                # Update potential extremes seen so far
                if curr_high > last_high:
                    last_high = curr_high
                    last_high_idx = i
                if curr_low < last_low:
                    last_low = curr_low
                    last_low_idx = i
                    
        elif trend == 1: # Uptrend
            if curr_high > last_high:
                last_high = curr_high
                last_high_idx = i
            elif curr_low < last_high * (1 - deviation_pct):
                # Reversal to downtrend
                # Check min bars constraint
                if (i - last_high_idx) >= min_bars or min_bars == 0:
                    trend = -1
                    pivots.append((last_high_idx, 1, last_high))
                    last_low = curr_low
                    last_low_idx = i
                
        elif trend == -1: # Downtrend
            if curr_low < last_low:
                last_low = curr_low
                last_low_idx = i
            elif curr_high > last_low * (1 + deviation_pct):
                # Reversal to uptrend
                # Check min bars constraint
                if (i - last_low_idx) >= min_bars or min_bars == 0:
                    trend = 1
                    pivots.append((last_low_idx, -1, last_low))
                    last_high = curr_high
                    last_high_idx = i

    # Add the final pending pivot
    if trend == 1:
        pivots.append((last_high_idx, 1, last_high))
    elif trend == -1:
        pivots.append((last_low_idx, -1, last_low))
        
    # Convert to Series
    pivot_series = pd.Series(np.nan, index=df.index)
    type_series = pd.Series(0, index=df.index)
    
    for idx, p_type, val in pivots:
        pivot_series.iloc[idx] = val
        type_series.iloc[idx] = p_type
        
    return pivot_series, type_series

def dynamic_zigzag(df: pd.DataFrame, atr_multiplier: float = 3.0, min_deviation: float = 0.01, min_bars: int = 10) -> tuple[pd.Series, pd.Series]:
    """
    Calculates ZigZag pivots with dynamic sensitivity based on ATR.
    """
    # Calculate recent volatility (e.g., last 30 days average ATR)
    atr = calculate_atr(df)
    current_price = df['close'].iloc[-1]
    avg_atr = atr.iloc[-30:].mean()
    
    if pd.isna(avg_atr) or current_price == 0:
        deviation = 0.05 
    else:
        # Deviation is ATR * Multiplier / Price
        deviation = (avg_atr * atr_multiplier) / current_price
    
    # Ensure deviation is not too small (noise)
    deviation = max(deviation, min_deviation)
    
    print(f"Dynamic Sensitivity Calculated: Deviation = {deviation:.2%}, Min Bars = {min_bars}")
    
    return zigzag_pivots(df, deviation, min_bars=min_bars)
