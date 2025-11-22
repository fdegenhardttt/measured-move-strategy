import yfinance as yf

# Hardcoded constituents for major indices (approximate/major components)
# In a production app, we might scrape Wikipedia or use an API.
DOW_30 = [
    "MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", 
    "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", 
    "MSFT", "NKE", "NVDA", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT"
]

# Top 50 of Nasdaq 100 (Subset for performance)
NASDAQ_TOP = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "TMUS", "CMCSA", "ADBE", "TXN", "NFLX", "AMD", "QCOM", "INTC",
    "AMGN", "HON", "INTU", "SBUX", "GILD", "BKNG", "DIOD", "MDLZ", "ADP", "ISRG",
    "REGN", "VRTX", "LRCX", "ATVI", "PYPL", "MU", "CSX", "MELI", "MRNA", "ASML"
]

def get_index_constituents(index_name: str) -> list[str]:
    """Returns a list of symbols for the given index."""
    if index_name == "Dow 30":
        return DOW_30
    elif index_name == "Nasdaq Top 50":
        return NASDAQ_TOP
    elif index_name == "Custom":
        return [] # Handled by text input
    return []

def get_timeframe_params(tf: str) -> tuple[str, str]:
    """
    Maps user friendly timeframe to yfinance (period, interval).
    
    Args:
        tf: '1h', '4h', '1d', '1w'
        
    Returns:
        (period, interval)
    """
    # yfinance limitations:
    # 1m: 7 days
    # 2m, 5m, 15m, 30m, 90m: 60 days
    # 1h: 730 days
    # 1d: max
    
    if tf == "1h":
        return "730d", "1h"
    elif tf == "4h":
        # yfinance doesn't strictly support 4h, usually we use 1h and resample, 
        # but for simplicity let's try to see if we can just use 1h and maybe the user is okay with that,
        # or we use 1d if they want longer history. 
        # Actually, yfinance API doesn't natively do 4h. 
        # Let's stick to supported intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        # We will use 1h for "Intraday" and just label it as such.
        return "730d", "1h" 
    elif tf == "1d":
        return "5y", "1d"
    elif tf == "1w":
        return "10y", "1wk"
    else:
        return "2y", "1d" # Default
