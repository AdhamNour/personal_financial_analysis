import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime



def load_file(host_name :str,database_name:str,username:str,password:str,file_path:str):
    load_transaction(host_name,database_name,username,password,file_path)
    load_summary(host_name,database_name,username,password,file_path)
    load_installments(host_name,database_name,username,password,file_path)


def load_transaction(host_name :str,database_name:str,username:str,password:str,file_path:str):
    df=pd.read_excel(io=file_path)
    index = df[df['Unnamed: 15'] == 'OPENING BALANCE'].index[0]+1
    df=df.loc[index:]
    index = df[df['Unnamed: 15'] == 'CLOSING BALANCE'].index[0]-1
    df=df.loc[:index]
    df = df.iloc[:, [4, 8, 15, 33]]
    df.columns = ["Transaction_Date","Value_Date","Description","Amount"]
    for column in df.columns:
        if column != 'Amount':
            df[column] = df[column].ffill()
    df = df[df['Amount'].notna()]
    df['Amount']=df['Amount'].astype('str').str.strip()
    if not df.empty:
        df[['Transaction_Amount', 'sign']] = df['Amount'].apply(
            lambda x: x.split(" ", 1) if " " in x else [x, None]
        ).apply(pd.Series)

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
        df['currency'] = df['currency'].replace('nan', '')
        
        df = df.drop(columns=['currency_value', 'signed_ammount_shift',])
        
        filename = os.path.basename(file_path)
        df['file_name']=filename
        engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")
        df.to_sql("credit_card_transaction_files", engine, if_exists="append", index=False)

def load_summary(host_name :str,database_name:str,username:str,password:str,file_path:str):
    df=pd.read_excel(io=file_path)
    df = df.iloc[:, [4, 11]]
    df.columns=['Key','Value']
    df =df[df['Key'].notna() & df['Value'].notna()]
    df['Key']=df['Key'].astype('str').str.replace(' ','_')
    df = df.transpose()
    df.columns=df.iloc[0]
    df=df[1:]
    df['file_name']=os.path.basename(file_path)
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")
    df.to_sql("credit_card_transaction_summary", engine, if_exists="append", index=False)

def load_installments(host_name :str,database_name:str,username:str,password:str,file_path:str):
    df=pd.read_excel(io=file_path)
    df=df[df['Unnamed: 3'].notna() & df['Unnamed: 6'].notna()]
    df = df.iloc[:, [3, 6, 13, 18,22,27,35]]
    df.columns=['Marchant_Name','Enrollment_Date','Principle','Interest','Total','Installment_No','Total_Number_Of_Installments']
    df['file_name']=os.path.basename(file_path)
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")
    df.to_sql("credit_card_installments_summary", engine, if_exists="append", index=False)