import yfinance as yf

# Gold ETF ticker (SPDR Gold Trust - GLD) or use '^XAUUSD' for spot price
gold = yf.Ticker("GC=F")  # Gold futures
# gold = yf.Ticker("GLD")  # Gold ETF
# gold = yf.Ticker("^XAUUSD")  # Gold spot price

# Fetch historical data
gold_history = gold.history(period="1y")  # Change period as needed (e.g., '5y', 'max')

# Display the first few rows
print(gold_history.head())
gold_history.to_csv("gold_price_history.csv")  # Save to CSV (optional)
