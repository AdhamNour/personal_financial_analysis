import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime

def load_file(host_name :str,database_name:str,username:str,password:str,file_path:str):
    df=pd.read_excel(io=file_path)
    index = df[df['Unnamed: 15'] == 'OPENING BALANCE'].index[0]+1
    df=df.loc[index:]
    index = df[df['Unnamed: 15'] == 'CLOSING BALANCE'].index[0]-1
    df=df.loc[:index]
    df = df.iloc[:, [4, 8, 15, 33]]
    df.columns = ["Transaction Date","Value Date","Description","Amount"]
    for column in df.columns:
        if column != 'Amount':
            df[column] = df[column].fillna(method='ffill')
    df = df[df['Amount'].notna()]
    if not df.empty:
        df['Amount']=df['Amount'].str.strip()
        df[['Transaction_Amount', 'sign']] = df["Amount"].str.split(" ",n=1, expand=True)
        df['Transaction_Amount']=df['Transaction_Amount'].astype('float')
        df['signed_amount'] = df['Transaction_Amount'].where(~df['sign'].isnull(), -1 * df['Transaction_Amount'])
        df = df.drop(columns=['Amount', 'Transaction_Amount', 'sign'])
        filename = os.path.basename(file_path)
        stmt_datetime_str =filename.split('.')[0].split('_')[1]+'01'
        stmt_datetime=datetime.strptime(stmt_datetime_str, "%Y%m%d")
        df['Statement Date']=stmt_datetime
        df['Transaction Date']=df['Transaction Date']+f"-{stmt_datetime.year}"
        df['Value Date']=df['Value Date']+f"-{stmt_datetime.year}"
        df['Transaction Date']=pd.to_datetime(df['Transaction Date'],format='%d-%m-%Y')
        df['Value Date']=pd.to_datetime(df['Value Date'],format='%d-%m-%Y')
        engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")
        df.to_sql("credit_cards_transactions", engine, if_exists="append", index=False)