import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from indicators import dynamic_zigzag, calculate_rsi

@dataclass
class MeasuredMove:
    start_idx: pd.Timestamp
    mid_idx: pd.Timestamp
    end_idx: pd.Timestamp # The 'C' point, start of the second leg
    
    start_price: float # A
    mid_price: float   # B
    end_price: float   # C
    
    projected_target: float # D (Target)
    direction: str # "Bullish" or "Bearish"
    
    completion_pct: float = 0.0 # How far are we to the target?
    current_price_at_analysis: float = 0.0
    proximity_to_c_pct: float = 0.0 # How close is current price to point C (Entry)?
    proximity_to_d_pct: float = 0.0 # How close is current price to point D (Target)?
    retracement_pct: float = 0.0 # Retracement ratio (B-C)/(B-A)

class MeasuredMoveStrategy:
    def __init__(self, symbol: str, df: pd.DataFrame):
        self.symbol = symbol
        self.df = df
        self.pivots = None
        self.pivot_types = None
        self.moves: List[MeasuredMove] = []
        
    def analyze(self, atr_multiplier: float = 3.0, min_bars: int = 10, strict_fib: bool = False, use_ema_filter: bool = False, use_volume_filter: bool = False, use_time_filter: bool = False, use_rsi_filter: bool = False):
        """
        Runs the analysis to find pivots and project measured moves.
        """
        # Calculate EMA 200 if needed
        ema_200 = None
        if use_ema_filter:
            ema_200 = self.df['close'].ewm(span=200, adjust=False).mean()

        # Calculate RSI if needed
        rsi_series = None
        if use_rsi_filter:
            rsi_series = calculate_rsi(self.df)

        # 1. Identify Pivots
        self.pivots, self.pivot_types = dynamic_zigzag(self.df, atr_multiplier=atr_multiplier, min_bars=min_bars)
        
        # 2. Identify Patterns (A-B-C)
        # We need a sequence of 3 pivots:
        # Bullish: Low (A) -> High (B) -> Higher Low (C)
        # Bearish: High (A) -> Low (B) -> Lower High (C)
        
        # Extract pivot points into a list for easier iteration
        pivot_data = []
        for date, val in self.pivots.dropna().items():
            p_type = self.pivot_types.loc[date]
            pivot_data.append({
                'date': date,
                'price': val,
                'type': p_type # 1 for High, -1 for Low
            })
            
        if len(pivot_data) < 3:
            # print("Not enough pivots to detect patterns.")
            return
            
        # Iterate through pivots to find potential active measured moves
        # We look at the last 3 pivots to see if a pattern is forming/active
        
        # Look back at recent history
        # We want to check triplets starting at i. Last triplet starts at N-3.
        # range(start, stop) -> stop is exclusive. So we want stop at N-2.
        start_index = max(0, len(pivot_data) - 5) # Look at last few pivots only
        for i in range(start_index, len(pivot_data) - 2):
            if i < 0: continue
            
            pA = pivot_data[i]
            pB = pivot_data[i+1]
            pC = pivot_data[i+2]
            
            # Check for Bullish Measured Move (Low -> High -> Higher Low)
            if pA['type'] == -1 and pB['type'] == 1 and pC['type'] == -1:
                if pC['price'] > pA['price']: # Higher Low constraint (optional but typical for trend)
                    
                    # Trend Filter Check
                    if use_ema_filter and ema_200 is not None:
                        # Check if Point C (Entry area) is above EMA 200
                        # We need to find the EMA value at pC['date']
                        try:
                            ema_val = ema_200.loc[pC['date']]
                            if pC['price'] < ema_val:
                                continue # Skip if below EMA (Counter-trend)
                        except KeyError:
                            pass # Date might be missing if calculated differently, skip check or continue

                    # Calculate Impulse (A to B)
                    impulse_move = pB['price'] - pA['price']
                    retracement = pB['price'] - pC['price']
                    retracement_pct = retracement / impulse_move if impulse_move != 0 else 0
                    
                    # Smart Validation: Fibonacci Check
                    # Healthy retracement is typically 0.382 to 0.786
                    if strict_fib:
                        if not (0.382 <= retracement_pct <= 0.786):
                            continue

                    # Volume Confirmation
                    if use_volume_filter:
                        impulse_vol = self.df.loc[pA['date']:pB['date']]['volume'].mean()
                        retracement_vol = self.df.loc[pB['date']:pC['date']]['volume'].mean()
                        if retracement_vol >= impulse_vol:
                            continue

                    # Time Symmetry
                    if use_time_filter:
                        impulse_len = len(self.df.loc[pA['date']:pB['date']])
                        retracement_len = len(self.df.loc[pB['date']:pC['date']])
                        if retracement_len > (impulse_len * 2.0):
                            continue

                    # RSI Filter
                    if use_rsi_filter and rsi_series is not None:
                        try:
                            rsi_val = rsi_series.loc[pC['date']]
                            if rsi_val > 70:
                                continue
                        except KeyError:
                            pass

                    # Project from C
                    target = pC['price'] + impulse_move
                    
                    # Calculate Proximity
                    current_price = self.df['close'].iloc[-1]
                    proximity_c = abs(current_price - pC['price']) / pC['price']
                    proximity_d = abs(current_price - target) / target
                    
                    move = MeasuredMove(
                        start_idx=pA['date'],
                        mid_idx=pB['date'],
                        end_idx=pC['date'],
                        start_price=pA['price'],
                        mid_price=pB['price'],
                        end_price=pC['price'],
                        projected_target=target,
                        direction="Bullish",
                        current_price_at_analysis=current_price,
                        proximity_to_c_pct=proximity_c,
                        proximity_to_d_pct=proximity_d,
                        retracement_pct=retracement_pct
                    )
                    self.moves.append(move)

            # Check for Bearish Measured Move (High -> Low -> Lower High)
            elif pA['type'] == 1 and pB['type'] == -1 and pC['type'] == 1:
                if pC['price'] < pA['price']: # Lower High constraint
                    
                    # Trend Filter Check
                    if use_ema_filter and ema_200 is not None:
                        # Check if Point C (Entry area) is below EMA 200
                        try:
                            ema_val = ema_200.loc[pC['date']]
                            if pC['price'] > ema_val:
                                continue # Skip if above EMA (Counter-trend)
                        except KeyError:
                            pass

                    # Calculate Impulse (A to B)
                    impulse_move = pA['price'] - pB['price'] # Positive magnitude
                    retracement = pC['price'] - pB['price']
                    retracement_pct = retracement / impulse_move if impulse_move != 0 else 0
                    
                    # Smart Validation: Fibonacci Check
                    if strict_fib:
                        if not (0.382 <= retracement_pct <= 0.786):
                            continue

                    # Volume Confirmation
                    if use_volume_filter:
                        impulse_vol = self.df.loc[pA['date']:pB['date']]['volume'].mean()
                        retracement_vol = self.df.loc[pB['date']:pC['date']]['volume'].mean()
                        if retracement_vol >= impulse_vol:
                            continue

                    # Time Symmetry
                    if use_time_filter:
                        impulse_len = len(self.df.loc[pA['date']:pB['date']])
                        retracement_len = len(self.df.loc[pB['date']:pC['date']])
                        if retracement_len > (impulse_len * 2.0):
                            continue

                    # RSI Filter
                    if use_rsi_filter and rsi_series is not None:
                        try:
                            rsi_val = rsi_series.loc[pC['date']]
                            if rsi_val < 30:
                                continue
                        except KeyError:
                            pass
                    
                    # Project from C
                    target = pC['price'] - impulse_move
                    
                    # Calculate Proximity
                    current_price = self.df['close'].iloc[-1]
                    proximity_c = abs(current_price - pC['price']) / pC['price']
                    proximity_d = abs(current_price - target) / target
                    
                    move = MeasuredMove(
                        start_idx=pA['date'],
                        mid_idx=pB['date'],
                        end_idx=pC['date'],
                        start_price=pA['price'],
                        mid_price=pB['price'],
                        end_price=pC['price'],
                        projected_target=target,
                        direction="Bearish",
                        current_price_at_analysis=current_price,
                        proximity_to_c_pct=proximity_c,
                        proximity_to_d_pct=proximity_d,
                        retracement_pct=retracement_pct
                    )
                    self.moves.append(move)
    
    def get_active_moves(self) -> List[MeasuredMove]:
        # Filter for moves that haven't been invalidated or fully completed long ago?
        # For now, just return the most recent ones
        return self.moves[-5:] # Return last 5 detected patterns
