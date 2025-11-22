import streamlit as st
import pandas as pd
from data_loader import fetch_data
from strategy import MeasuredMoveStrategy
from market_data import get_index_constituents, get_timeframe_params
from visualization import plot_interactive_chart

st.set_page_config(page_title="Measured Move Scanner", layout="wide")

# --- iOS 26 Style Custom CSS ---
st.markdown("""
<style>
    /* Main Background - Deep Futuristic Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar - Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        padding-bottom: 1rem;
    }
    
    /* Buttons - iOS Pill Style */
    .stButton > button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.6);
    }
    
    /* Dataframes & Containers - Floating Cards */
    .stDataFrame, .stPlotlyChart {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Inputs & Selectboxes */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Text Color Override */
    .stMarkdown, .stText, p, label {
        color: #e0e0e0 !important;
    }
    
    /* Success/Warning Messages */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
</style>
""", unsafe_allow_html=True)

st.title("Measured Move Scanner")
st.markdown("### 🚀 Next-Gen Pattern Recognition")

# --- Sidebar Controls ---
st.sidebar.header("Configuration")

# 1. Symbol Selection
selection_mode = st.sidebar.radio("Selection Mode", ["Category", "Custom"])

symbols = []
if selection_mode == "Category":
    category = st.sidebar.selectbox("Select Category", [
        "Dow 30", 
        "Nasdaq Top 50", 
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

# 4. Filtering
st.sidebar.subheader("Filter Results")
max_proximity = st.sidebar.slider("Max Distance from Entry (Point C) %", 0.0, 20.0, 5.0, 0.5)
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
            strategy.analyze(atr_multiplier=atr_multiplier, min_bars=min_bars)
            
            moves = strategy.get_active_moves()
            
            for move in moves:
                # Filter logic
                if show_all or (move.proximity_to_c_pct * 100 <= max_proximity):
                    results.append({
                        "Symbol": symbol,
                        "Direction": move.direction,
                        "Price": move.current_price_at_analysis,
                        "Entry (C)": move.end_price,
                        "Target": move.projected_target,
                        "Dist from Entry %": move.proximity_to_c_pct * 100,
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
        display_cols = ["Symbol", "Direction", "Price", "Entry (C)", "Target", "Dist from Entry %"]
        
        # Interactive Table
        st.dataframe(res_df[display_cols].style.format({
            "Price": "{:.2f}",
            "Entry (C)": "{:.2f}",
            "Target": "{:.2f}",
            "Dist from Entry %": "{:.2f}%"
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
            
            fig = plot_interactive_chart(
                row["DataFrame"], 
                row["Pivots"], 
                row["Moves"], 
                selected_symbol
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show pattern details
            st.write(f"**Pattern Details for {selected_symbol}:**")
            # We want to show details for ALL patterns found for this symbol, not just the one in the row if we filtered?
            # Actually row["Moves"] contains all active moves from the strategy run.
            # But we might want to highlight which ones passed the filter?
            # For now, just showing all active moves on the chart is good context.
            for m in row["Moves"]:
                st.write(f"- **{m.direction}**: A={m.start_price:.2f}, B={m.mid_price:.2f}, C={m.end_price:.2f} -> Target={m.projected_target:.2f}")

else:
    st.info("Select options in the sidebar and click 'Run Scan' to start.")
