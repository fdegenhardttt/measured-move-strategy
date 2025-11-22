import yfinance as yf

# --- Asset Lists ---

# US Indices
DOW_30 = [
    "MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS", 
    "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", 
    "MSFT", "NKE", "NVDA", "PG", "CRM", "TRV", "UNH", "VZ", "V", "WMT"
]

NASDAQ_TOP_50 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "TMUS", "CMCSA", "ADBE", "TXN", "NFLX", "AMD", "QCOM", "INTC",
    "AMGN", "HON", "INTU", "SBUX", "GILD", "BKNG", "DIOD", "MDLZ", "ADP", "ISRG",
    "REGN", "VRTX", "LRCX", "ATVI", "PYPL", "MU", "CSX", "MELI", "MRNA", "ASML"
]

# Global Indices (Major)
GLOBAL_INDICES = [
    "^GSPC",  # S&P 500 (US)
    "^DJI",   # Dow Jones (US)
    "^IXIC",  # Nasdaq (US)
    "^GDAXI", # DAX (Germany)
    "^FTSE",  # FTSE 100 (UK)
    "^FCHI",  # CAC 40 (France)
    "^STOXX50E", # EURO STOXX 50
    "^N225",  # Nikkei 225 (Japan)
    "^HSI",   # Hang Seng (Hong Kong)
    "^STI",   # Straits Times (Singapore)
    "^AXJO",  # ASX 200 (Australia)
    "^KS11",  # KOSPI (South Korea)
    "^BSESN", # BSE SENSEX (India)
    "^BVSP",  # IBOVESPA (Brazil)
    "^MXX",   # IPC (Mexico)
]

# Crypto (Major)
CRYPTO = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", 
    "ADA-USD", "DOGE-USD", "TRX-USD", "LINK-USD", "LTC-USD",
    "BCH-USD", "DOT-USD", "MATIC-USD", "SHIB-USD", "AVAX-USD"
]

# Commodities
COMMODITIES_HARD = [
    "GC=F", # Gold
    "SI=F", # Silver
    "HG=F", # Copper
    "PL=F", # Platinum
    "PA=F", # Palladium
    "CL=F", # Crude Oil
    "BZ=F", # Brent Crude
    "NG=F", # Natural Gas
    "RB=F", # RBOB Gasoline
]

COMMODITIES_SOFT = [
    "ZC=F", # Corn
    "ZW=F", # Wheat
    "ZS=F", # Soybean
    "SB=F", # Sugar
    "CC=F", # Cocoa
    "KC=F", # Coffee
    "CT=F", # Cotton
    "OJ=F", # Orange Juice
    "LBS=F" # Lumber
]

def get_index_constituents(category: str) -> list[str]:
    """Returns a list of symbols for the given category."""
    if category == "Dow 30":
        return DOW_30
    elif category == "Nasdaq Top 50":
        return NASDAQ_TOP_50
    elif category == "Global Indices":
        return GLOBAL_INDICES
    elif category == "Crypto":
        return CRYPTO
    elif category == "Commodities (Hard)":
        return COMMODITIES_HARD
    elif category == "Commodities (Soft)":
        return COMMODITIES_SOFT
    elif category == "Custom":
        return []
    return []

def get_timeframe_params(tf: str) -> tuple[str, str]:
    """
    Maps user friendly timeframe to yfinance (period, interval).
    """
    # yfinance limitations:
    # 1m: 7 days
    # 2m, 5m, 15m, 30m: 60 days
    # 1h: 730 days
    
    mapping = {
        "1m": ("7d", "1m"),
        "5m": ("60d", "5m"),
        "15m": ("60d", "15m"),
        "30m": ("60d", "30m"),
        "1h": ("730d", "1h"),
        "4h": ("730d", "1h"), # Resampling not implemented, using 1h as proxy for now
        "1d": ("5y", "1d"),
        "1w": ("10y", "1wk")
    }
    
    return mapping.get(tf, ("2y", "1d"))
