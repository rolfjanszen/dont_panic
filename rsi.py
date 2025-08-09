import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Main function to fetch data, compute RSI, and plot
def fetch_and_plot_rsi(ticker, start_date, end_date):
    # Fetch data
    data = yf.download(ticker, start=start_date, end=end_date,repair=True)
    if data.empty:
        print(f"No data found for {ticker} between {start_date} and {end_date}.")
        return

    # Calculate RSI
    data['RSI'] = calculate_rsi(data)

    # Create price chart
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    price_fig.update_layout(title=f"{ticker} Closing Prices", xaxis_title="Date", yaxis_title="Price")

    # Create RSI chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'))
    rsi_fig.add_shape(type='line', x0=data.index[0], x1=data.index[-1], y0=70, y1=70,
                      line=dict(color='red', dash='dash'))
    rsi_fig.add_shape(type='line', x0=data.index[0], x1=data.index[-1], y0=30, y1=30,
                      line=dict(color='green', dash='dash'))
    rsi_fig.update_layout(title=f"{ticker} RSI (14-day)", xaxis_title="Date", yaxis_title="RSI")

    # Show plots
    price_fig.show()
    rsi_fig.show()

# Example usage
if __name__ == "__main__":
    ticker ='QQQ'# input("Enter stock ticker (e.g. AAPL): ").strip().upper()
    start_date = '2023-01-01'#input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = '2025-08-01'# input("Enter end date (YYYY-MM-DD): ").strip()

    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
    else:
        fetch_and_plot_rsi(ticker, start_date, end_date)
