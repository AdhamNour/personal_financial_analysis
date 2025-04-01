import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"single_file_processor_{datetime.now().strftime("%Y%m%d%H%M%S")}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Read database credentials from environment variables
host_name = os.getenv("PERSONAL_FINANCE_DATABASE_HOST")
logger.info(f"Connecting to database at {host_name}")
database_name = os.getenv("PERSONAL_FINANCE_DATABASE_SCHEMA")
logger.info(f"Using database schema: {database_name}")
username = os.getenv("PERSONAL_FINANCE_DATABASE_USER")
logger.info(f"Using database user: {username}")
password = os.getenv("PERSONAL_FINANCE_DATABASE_PASSWORD")
logger.info("Creating database engine")
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")


def load_file(file_path:str):
    logger.info(f"Loading file: {file_path}")
    load_transaction(file_path)
    logger.info(f"Loading summary from file: {file_path}")
    load_summary(file_path)
    logger.info(f"Loading installments from file: {file_path}")
    load_installments(file_path)


def load_transaction(file_path:str):
    logger.info(f"Loading transactions from file: {file_path}")
    df=pd.read_excel(io=file_path)
    logger.info(f"Initial DataFrame shape: {df.shape}")
    index = df[df['Unnamed: 15'] == 'OPENING BALANCE'].index[0]+1
    logger.info(f"Index for OPENING BALANCE: {index}")
    df=df.loc[index:]
    logger.info(f"DataFrame shape after filtering: {df.shape}")
    index = df[df['Unnamed: 15'] == 'CLOSING BALANCE'].index[0]-1
    logger.info(f"Index for CLOSING BALANCE: {index}")  
    df=df.loc[:index]
    logger.info(f"DataFrame shape after filtering: {df.shape}")
    df = df.iloc[:, [4, 8, 15, 33]]
    logger.info(f"DataFrame shape after selecting columns: {df.shape}")
    df.columns = ["Transaction_Date","Value_Date","Description","Amount"]
    logger.info(f"DataFrame columns: {df.columns}")
    logger.info(f"DataFrame dtypes: {df.dtypes}")
    for column in df.columns:
        if column != 'Amount':
            df[column] = df[column].ffill()
    logger.info(f"DataFrame shape after forward fill: {df.shape}")
    
    df = df[df['Amount'].notna()]
    logger.info(f"DataFrame shape after dropping NaN Amount: {df.shape}")
    df['Amount']=df['Amount'].astype('str').str.strip()
    if not df.empty:
        logger.info(f"DataFrame shape after stripping Amount: {df.shape}")
        df[['Transaction_Amount', 'sign']] = df['Amount'].apply(
            lambda x: x.split(" ", 1) if " " in x else [x, None]
        ).apply(pd.Series)
        logger.info("wrangling data")
        df['Transaction_Amount']=df['Transaction_Amount'].astype('float')
        df['signed_amount'] = df['Transaction_Amount'].where(~df['sign'].isnull(), -1 * df['Transaction_Amount'])
        df = df.drop(columns=['Amount', 'Transaction_Amount', 'sign'])
        df['Transaction_Date'] = df['Transaction_Date'].fillna(method='ffill')
        df['Value_Date'] = df['Value_Date'].fillna(method='ffill')
        df['currency_value'] = df['Description'].shift(-1)
        df['signed_ammount_shift'] = df['signed_amount'].shift(-1)
        # Condition: signed_amont + signed_ammount_shift == signed_amont
        mask = df['signed_amount'] + df['signed_ammount_shift'] != df['signed_amount']

        # Update "Description" column by appending 'currency_value'
        df.loc[mask, 'currency_value'] = np.nan
        df['currency']=df['currency_value'].astype('str').str[:3].replace('nan',np.nan);
        df['value']=df['currency_value'].astype('str').str[3:].replace('nan',np.nan);   

        df=df[df['signed_amount']!=0]
        df['value'] = pd.to_numeric(df['value'].str.replace(',', '.', regex=True), errors='coerce')
        df['currency']=df['currency'].astype('str')
        df['currency'] = df['currency'].replace('nan', 'EGP')
        
        df = df.drop(columns=['currency_value', 'signed_ammount_shift',])
        logger.info("Finished wrangling")
        filename = os.path.basename(file_path)
        df['file_name']=filename
        logger.info(f"Final DataFrame shape: {df.shape}")
        logger.info(f"DataFrame columns: {df.columns}")
        logger.info(f"DataFrame dtypes: {df.dtypes}")
        # Save to SQL
        logger.info("Saving transactions DataFrame to SQL")
        df.to_sql("credit_card_transaction_files", engine, if_exists="append", index=False)

def load_summary(file_path:str):
    logger.info(f"Loading summary from file: {file_path}")
    df=pd.read_excel(io=file_path)
    df = df.iloc[:, [4, 11]]
    df.columns=['Key','Value']
    df =df[df['Key'].notna() & df['Value'].notna()]
    df['Key']=df['Key'].astype('str').str.replace(' ','_')
    df = df.transpose()
    df.columns=df.iloc[0]
    df=df[1:]
    df['file_name']=os.path.basename(file_path)
    logger.info(f"Summary DataFrame shape: {df.shape}")
    logger.info(f"Summary DataFrame columns: {df.columns}")
    logger.info(f"Summary DataFrame dtypes: {df.dtypes}")
    # Save to SQL
    logger.info("Saving summary DataFrame to SQL")
    df.to_sql("credit_card_transaction_summary", engine, if_exists="append", index=False)

def load_installments(file_path:str):
    logger.info(f"Loading installments from file: {file_path}")
    # Read the Excel file
    df=pd.read_excel(io=file_path)
    df=df[df['Unnamed: 3'].notna() & df['Unnamed: 6'].notna()]
    df = df.iloc[:, [3, 6, 13, 18,22,27,35]]
    df.columns=['Marchant_Name','Enrollment_Date','Principle','Interest','Total','Installment_No','Total_Number_Of_Installments']
    df['file_name']=os.path.basename(file_path)
    logger.info(f"Installments DataFrame shape: {df.shape}")
    logger.info(f"Installments DataFrame columns: {df.columns}")
    logger.info(f"Installments DataFrame dtypes: {df.dtypes}")
    # Save to SQL
    logger.info("Saving installments DataFrame to SQL")
    df.to_sql("credit_card_installments_summary", engine, if_exists="append", index=False)