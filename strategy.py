import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from indicators import dynamic_zigzag

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

class MeasuredMoveStrategy:
    def __init__(self, symbol: str, df: pd.DataFrame):
        self.symbol = symbol
        self.df = df
        self.pivots = None
        self.pivot_types = None
        self.moves: List[MeasuredMove] = []
        
    def analyze(self, atr_multiplier: float = 3.0, min_bars: int = 10):
        """
        Runs the analysis to find pivots and project measured moves.
        """
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
            print("Not enough pivots to detect patterns.")
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
                    # Calculate Impulse (A to B)
                    impulse_move = pB['price'] - pA['price']
                    
                    # Project from C
                    target = pC['price'] + impulse_move
                    
                    # Calculate Proximity
                    current_price = self.df['close'].iloc[-1]
                    # Proximity: How far has it moved from C relative to the target distance?
                    # Or simply % distance from C?
                    # Let's define "Close to Entry" as being near C.
                    # dist = (Current - C) / C
                    proximity = abs(current_price - pC['price']) / pC['price']
                    
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
                        proximity_to_c_pct=proximity
                    )
                    self.moves.append(move)

            # Check for Bearish Measured Move (High -> Low -> Lower High)
            elif pA['type'] == 1 and pB['type'] == -1 and pC['type'] == 1:
                if pC['price'] < pA['price']: # Lower High constraint
                    # Calculate Impulse (A to B)
                    impulse_move = pA['price'] - pB['price'] # Positive magnitude
                    
                    # Project from C
                    target = pC['price'] - impulse_move
                    
                    # Calculate Proximity
                    current_price = self.df['close'].iloc[-1]
                    proximity = abs(current_price - pC['price']) / pC['price']
                    
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
                        proximity_to_c_pct=proximity
                    )
                    self.moves.append(move)
    
    def get_active_moves(self) -> List[MeasuredMove]:
        # Filter for moves that haven't been invalidated or fully completed long ago?
        # For now, just return the most recent ones
        return self.moves[-5:] # Return last 5 detected patterns
