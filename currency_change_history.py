import datetime
import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
import yfinance as yf
from sqlalchemy.orm import sessionmaker

# Database credintials 

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"currency_change_hsitory_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log"),
        logging.StreamHandler()
    ]
)

hostname = os.getenv("PERSONAL_FINANCE_DATABASE_HOST")
logging.info(f"Connecting to database at {hostname}")
dbname = os.getenv("PERSONAL_FINANCE_DATABASE_SCHEMA")
logging.info(f"Using database schema: {dbname}")
uname = os.getenv("PERSONAL_FINANCE_DATABASE_USER")
logging.info(f"Using database user: {uname}")
pwd = os.getenv("PERSONAL_FINANCE_DATABASE_PASSWORD")

engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
logging.info("SQLAlchemy engine created successfully.")
# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Execute the SQL statement and fetch results
result = session.execute(
    text("SELECT DISTINCT currency FROM credit_card_transaction_files cctf WHERE currency != 'USD'")
)
logging.info(f"Fetched {result.rowcount} distinct currencies.")
# Store the result into a list
distinct_currencies = [row[0] for row in result]
session.close()

for currency in distinct_currencies:
    logging.info(f"Fetching historical data for currency: {currency}")
    # Fetch historical data for JPY/USD (currency ticker format "JPY=X")
    currency_pair = f"{currency}=X"
    data = yf.Ticker(currency_pair)

    # Get historical exchange rates
    history = data.history(period="max")  # Adjust period as needed (e.g., "5y", "max")

    # Display the first few rows
    history['currency']=currency
    history['extraction_timestamp']=datetime.datetime.now()


    # Save to CSV (optional)
    history.to_sql("currency_change_history", engine, if_exists="append", index=True)
