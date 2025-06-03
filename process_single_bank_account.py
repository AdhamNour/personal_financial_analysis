import datetime
import string
import pandas as pd
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"process_single_bank_account{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log"),
        logging.StreamHandler()
    ]
)

logging.info("Logging is configured in process_single_bank_account.py.")

def process_single_bank_account(statement_path:string):
    """
    Process a single bank account statement file and save it to csv.
    
    Args:
        statement_path (str): The path to the bank statement file.
        
    Returns:
        NA
    """
    if not os.path.isfile(statement_path):
        logging.error(f"File not found: {statement_path}")
        raise FileNotFoundError(f"File not found: {statement_path}")
    logging.info(f"Processing bank statement from {statement_path}")
    df=pd.read_excel(statement_path)
    logging.info(f"Read {len(df)} rows from the bank statement file.")
    index = df[df['Unnamed: 9'] == 'OPENING BALANCE'].index[0]+1
    df=df.loc[index:]
    df
    logging.info(f"Filtered data to {len(df)} rows after removing opening balance.")
    index = df[df['Unnamed: 9'] == 'CLOSING BALANCE'].index[0]-1
    df=df.loc[:index]
    df
    logging.info(f"Filtered data to {len(df)} rows after removing closing balance.")
    df=df.dropna(how='all')
    logging.info(f"Removed rows with all NaN values, remaining rows: {len(df)}.")
    df = df.dropna(axis=1, how='all')
    logging.info(f"Removed columns with all NaN values, remaining columns: {len(df.columns)}.")
    df['Transaction_Type'] = df.apply(
    lambda row: 'Credit' if pd.notna(row['Unnamed: 23']) 
                else 'Debit' if pd.notna(row['Unnamed: 18']) 
                else None,
    axis=1
)   .ffill()
    logging.info("Transaction types assigned based on available columns.")
    df['Unnamed: 2']=df['Unnamed: 2'].fillna(method='ffill')
    logging.info("Forward filled missing values in 'Date' column.")
    df[['Unnamed: 18','Unnamed: 23','Unnamed: 25']]=df[['Unnamed: 18','Unnamed: 23','Unnamed: 25']].ffill().fillna(0)
    logging.info("Forward filled missing values in 'Debit', 'Credit', and 'Balance' columns.")
    df=df.groupby(['Unnamed: 2','Unnamed: 18','Unnamed: 23','Unnamed: 25','Transaction_Type']).agg({
    'Unnamed: 9': ' '.join,
    }).sort_values(
        by=['Unnamed: 2','Unnamed: 25'],ascending=[True,False]
    ).reset_index()
    logging.info("Joined the transaction description that whas split to multipe rows into one single row.")
    df=df.rename(
        columns={
            'Unnamed: 2': 'DATE',
            'Unnamed: 18': 'Debit',
            'Unnamed: 23': 'Credit',
            'Unnamed: 25': 'Balance',
            'Unnamed: 9': 'Transaction_Description'
        }
    )
    logging.info("Renamed columns for better readability.")
    cols_to_clean = ['Debit', 'Credit', 'Balance']
    for col in cols_to_clean:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    logging.info("Converted 'Debit', 'Credit', and 'Balance' columns to float after removing commas.")
    df['Debit'] = df.apply(
    lambda row: row['Debit'] if row['Transaction_Type'] == 'Debit' else np.nan, axis=1
    )
    df['Credit'] = df.apply(
        lambda row: row['Credit'] if row['Transaction_Type'] == 'Credit' else np.nan, axis=1
    )
    logging.info("Separated 'Debit' and 'Credit' values based on 'Transaction_Type'.")
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d%b%y')
    logging.info("Converted 'DATE' column to datetime format.")
    df[['code', 'desc']] = df['Transaction_Description'].str.split('\\', expand=True)
    logging.info("Split 'Transaction_Description' into 'code' and 'desc'.")
    df.drop(columns=['Transaction_Description'], inplace=True)
    logging.info("Dropped the original 'Transaction_Description' column after splitting.")
    df[['type','code']]=df['code'].str.rsplit(' ', n=1, expand=True)
    logging.info("Split 'code' into 'type' and 'code' based on the last space.")
    df['type'] = df['type'].str.strip()
    df['code'] = df['code'].str.strip()
    logging.info("Stripped whitespace from 'type' and 'code' columns.")
    df['desc'] = df['desc'].str.strip()
    logging.info("Stripped whitespace from 'desc' column.")
    df['desc'] = df['desc'].str.replace(' +', ' ', regex=True)     
    logging.info("Bank statement processing completed.")
    df.to_csv(f"{statement_path.split('.')[0]}.csv", index=False)
    logging.info(f"Processed data saved to {statement_path.split('.')[0]}.csv")
    
