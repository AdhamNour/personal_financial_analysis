import datetime
from sqlalchemy import create_engine
import yfinance as yf

# Database credintials 

hostname = "localhost"
dbname = "stg_personal_financial_analysis"
uname = "root"
pwd = "production_server"

# Fetch historical data for JPY/USD (currency ticker format "JPY=X")
currency_pair = "JPY=X"
data = yf.Ticker(currency_pair)

# Get historical exchange rates
history = data.history(period="max")  # Adjust period as needed (e.g., "5y", "max")

# Display the first few rows
print(history.head())
history['currency']='JPY'
history['extraction_timestamp']=datetime.datetime.now()

engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")

# Save to CSV (optional)
history.to_sql("currency_change_history", engine, if_exists="append", index=True)
