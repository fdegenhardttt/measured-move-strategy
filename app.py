import streamlit as st
import pandas as pd
from data_loader import fetch_data
from strategy import MeasuredMoveStrategy
from market_data import get_index_constituents, get_timeframe_params
from visualization import plot_interactive_chart

st.set_page_config(page_title="Measured Move Scanner", layout="wide")

# --- Apple Style Custom CSS ---
st.markdown("""
<style>
    /* Main Background - Off-white/Light Gray */
    .stApp {
        background-color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f;
    }
    
    /* Sidebar - Translucent Blur */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: saturate(180%) blur(20px);
        border-right: 1px solid #d2d2d7;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #1d1d1f !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 48px !important;
        margin-bottom: 0.5em;
    }
    
    /* Buttons - Apple Blue Pill */
    .stButton > button {
        background-color: #0071e3;
        color: white;
        border: none;
        border-radius: 980px; /* Pill shape */
        padding: 8px 22px;
        font-size: 17px;
        font-weight: 400;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #0077ed;
        transform: scale(1.02);
    }
    
    /* Cards/Containers - Clean White with Subtle Shadow */
    .stDataFrame, .stPlotlyChart, div[data-testid="stExpander"] {
        background: #ffffff;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.02);
    }
    
    /* Inputs & Selectboxes */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        border-radius: 12px;
        border: 1px solid #d2d2d7;
    }
    
    /* Text Color Override */
    .stMarkdown, .stText, p, label {
        color: #1d1d1f !important;
    }
    
    /* Success/Info Messages */
    .stAlert {
        background-color: #ffffff;
        border-radius: 14px;
        border: 1px solid #d2d2d7;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    }
    
</style>
""", unsafe_allow_html=True)

st.title("Measured Move Scanner")
st.markdown("### Pro-Grade Pattern Recognition")

# --- Sidebar Controls ---
st.sidebar.header("Configuration")

# 1. Symbol Selection
selection_mode = st.sidebar.radio("Selection Mode", ["Category", "Custom"])

symbols = []
if selection_mode == "Category":
    category = st.sidebar.selectbox("Select Category", [
        "Dow 30", 
        "Nasdaq 100", 
        "Global Indices", 
        "Crypto", 
        "Commodities (Hard)", 
        "Commodities (Soft)"
    ])
    symbols = get_index_constituents(category)
    st.sidebar.info(f"Loaded {len(symbols)} symbols from {category}")
else:
    custom_input = st.sidebar.text_area("Enter Symbols (comma separated)", "SPY, QQQ, IWM, NVDA, TSLA")
    symbols = [s.strip().upper() for s in custom_input.split(",") if s.strip()]

# 2. Timeframe
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"], index=6) # Default 1d
period, interval = get_timeframe_params(timeframe)

# 3. Strategy Parameters
st.sidebar.subheader("Strategy Settings")
atr_multiplier = st.sidebar.slider("ATR Multiplier (Sensitivity)", 1.0, 10.0, 6.0, 0.5)
min_bars = st.sidebar.slider("Min Bars Duration", 5, 50, 20, 1)
strict_fib = st.sidebar.checkbox("Smart Recognition (Fibonacci 0.382-0.786)", True)

# 4. Filtering
st.sidebar.subheader("Filter Results")
max_proximity = st.sidebar.slider("Max Distance from Target (Point D) %", 0.0, 20.0, 5.0, 0.5)
show_all = st.sidebar.checkbox("Show All (Ignore Filter)", False)

# --- Main Analysis ---
if st.sidebar.button("Run Scan"):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols):
        status_text.text(f"Analyzing {symbol}...")
        progress_bar.progress((i + 1) / len(symbols))
        
        try:
            df = fetch_data(symbol, period=period, interval=interval)
            strategy = MeasuredMoveStrategy(symbol, df)
            strategy.analyze(atr_multiplier=atr_multiplier, min_bars=min_bars, strict_fib=strict_fib)
            
            moves = strategy.get_active_moves()
            
            for move in moves:
                # Filter logic - NOW USING PROXIMITY TO D
                if show_all or (move.proximity_to_d_pct * 100 <= max_proximity):
                    results.append({
                        "Symbol": symbol,
                        "Direction": move.direction,
                        "Price": move.current_price_at_analysis,
                        "Entry (C)": move.end_price,
                        "Target (D)": move.projected_target,
                        "Dist to Target %": move.proximity_to_d_pct * 100,
                        "Object": move, # Store object for plotting
                        "DataFrame": df,
                        "Pivots": strategy.pivots,
                        "Moves": moves # All moves for this symbol
                    })
                    
        except Exception as e:
            # st.error(f"Error analyzing {symbol}: {e}")
            pass
            
    progress_bar.empty()
    status_text.empty()
    
    # Store in session state
    st.session_state['scan_results'] = results
    st.session_state['scan_performed'] = True

# --- Display Results ---
if st.session_state.get('scan_performed', False):
    results = st.session_state['scan_results']
    
    if not results:
        st.warning("No patterns found matching criteria.")
    else:
        st.success(f"Found {len(results)} opportunities!")
        
        # Convert to DataFrame for display
        res_df = pd.DataFrame(results)
        display_cols = ["Symbol", "Direction", "Price", "Target (D)", "Dist to Target %"]
        
        # Interactive Table
        st.dataframe(res_df[display_cols].style.format({
            "Price": "{:.2f}",
            "Target (D)": "{:.2f}",
            "Dist to Target %": "{:.2f}%"
        }))
        
        # --- Detailed Charts ---
        st.subheader("Detailed Charts")
        
        # Let user select which symbol to view from the results
        # Use a key to ensure state persistence if needed, though selectbox usually handles it
        symbol_options = res_df["Symbol"].unique()
        selected_symbol = st.selectbox("Select Symbol to View Chart", symbol_options)
        
        if selected_symbol:
            # Get data for this symbol
            # We might have multiple rows for the same symbol if multiple patterns, 
            # but they share the same DF and Pivots usually.
            # Just take the first one to get the plotting data.
            row = res_df[res_df["Symbol"] == selected_symbol].iloc[0]
            
            # Let user select specific pattern
            moves = row["Moves"]
            pattern_options = ["All Patterns"] + [f"Pattern {i+1}: {m.direction} (Target {m.projected_target:.2f})" for i, m in enumerate(moves)]
            selected_pattern_idx = st.selectbox("Select Pattern to View", pattern_options)
            
            moves_to_plot = moves
            if selected_pattern_idx != "All Patterns":
                # Extract index from string "Pattern 1: ..." -> index 0
                idx = int(selected_pattern_idx.split(":")[0].replace("Pattern ", "")) - 1
                moves_to_plot = [moves[idx]]
                
                # Show specific details for this pattern
                m = moves[idx]
                st.info(f"""
                **Selected Pattern Analysis**
                - **Direction**: {m.direction}
                - **Impulse (A->B)**: {m.start_price:.2f} -> {m.mid_price:.2f}
                - **Retracement (B->C)**: {m.mid_price:.2f} -> {m.end_price:.2f}
                - **Target (D)**: {m.projected_target:.2f}
                - **Retracement Ratio**: {m.retracement_pct:.1%} (Fibonacci Check)
                """)
            
            fig = plot_interactive_chart(
                row["DataFrame"], 
                row["Pivots"], 
                moves_to_plot, 
                selected_symbol
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if selected_pattern_idx == "All Patterns":
                st.write(f"**All Patterns for {selected_symbol}:**")
                for i, m in enumerate(moves):
                     st.write(f"- **Pattern {i+1}**: {m.direction}, Target={m.projected_target:.2f}, Retracement={m.retracement_pct:.1%}")

else:
    st.info("Select options in the sidebar and click 'Run Scan' to start.")
