import pandas as pd
from sqlalchemy import create_engine, text
import yfinance as yf



engine = create_engine("postgresql://myuser:mypassword@localhost:5432/mydatabase", connect_args={"options": "-c search_path=stocks"})

# trancate landing tables before running bulk load
# with engine.connect() as connection:
#     connection.execute(text("TRUNCATE TABLE egx_stocks"))
#     connection.execute(text("TRUNCATE TABLE egx_stocks_details"))
#     connection.commit()
# read the stocks csv file and store it in the database
stocks_df=pd.read_csv('stocks.csv')
stocks_df.to_sql('egx_stocks', engine, if_exists='replace', index=False)

tickers = [s+".CA" for s in stocks_df['Code'].tolist()]

# loading the stocks data from Yahoo Finance
data = yf.download(tickers, period="312mo", interval="1d")
data.reset_index(inplace=True)
data.columns = ['_'.join(col).strip('_') for col in data.columns]
data=data.melt(id_vars=["Date"], var_name="Ticker_Metric", value_name="Value")
data[['Metric','Ticker']] = data["Ticker_Metric"].str.rsplit("_", n=1, expand=True)
data.to_sql('egx_stocks_details', engine, if_exists='append', index=False)


