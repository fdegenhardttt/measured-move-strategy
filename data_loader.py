import yfinance as yf
import pandas as pd

def fetch_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches OHLCV data from Yahoo Finance.
    
    Args:
        symbol: Ticker symbol (e.g., 'SPY', 'BTC-USD')
        period: Data period to download (default '1y')
        interval: Data interval (default '1d')
        
    Returns:
        pd.DataFrame: DataFrame with columns Open, High, Low, Close, Volume
    """
    print(f"Fetching data for {symbol}...")
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    
    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")
        
    # Flatten MultiIndex columns if present (yfinance update)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # Ensure standard column names
    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    
    # Drop any rows with missing values
    df = df.dropna()
    
    return df
