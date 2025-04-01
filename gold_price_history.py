import yfinance as yf
from dotenv import load_dotenv
import os
import logging
from sqlalchemy import create_engine
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"gold_price_history_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log"),
        logging.StreamHandler()
    ]
)

logging.info("Logging is configured.")

# Load environment variables from a .env file
load_dotenv()

# Read database credentials from environment variables
GOLD_STANDARD_DATABASE_HOST = os.getenv("GOLD_STANDARD_DATABASE_HOST")
logging.info(f"Connecting to database at {GOLD_STANDARD_DATABASE_HOST}")
GOLD_STANDARD_DATABASE_SCHEMA = os.getenv("GOLD_STANDARD_DATABASE_SCHEMA")
logging.info(f"Using database schema: {GOLD_STANDARD_DATABASE_SCHEMA}")
GOLD_STANDARD_DATABASE_USER = os.getenv("GOLD_STANDARD_DATABASE_USER")
logging.info(f"Using database user: {GOLD_STANDARD_DATABASE_USER}")
GOLD_STANDARD_DATABASE_PASSWORD = os.getenv("GOLD_STANDARD_DATABASE_PASSWORD")

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{GOLD_STANDARD_DATABASE_USER}:{GOLD_STANDARD_DATABASE_PASSWORD}@{GOLD_STANDARD_DATABASE_HOST}/{GOLD_STANDARD_DATABASE_SCHEMA}"
)
logging.info("SQLAlchemy engine created successfully.")

# Gold ETF ticker (SPDR Gold Trust - GLD) or use '^XAUUSD' for spot price
gold = yf.Ticker("GC=F")  # Gold futures
logging.info("Fetching gold price data.")
# gold = yf.Ticker("GLD")  # Gold ETF
# gold = yf.Ticker("^XAUUSD")  # Gold spot price

# Fetch historical data
gold_history = gold.history(period="max")  # Change period as needed (e.g., '5y', 'max')
logging.info(f"Fetched gold price data with shape: {gold_history.shape}")

gold_history['extraction_timestamp']=datetime.datetime.now()

# Display the first few rows
print(gold_history.head())
gold_history.to_sql(
    name="gold_price",
    con=engine,
    if_exists="replace",  # or 'append' to add to existing table
    index=True,
    index_label="Date"
)
