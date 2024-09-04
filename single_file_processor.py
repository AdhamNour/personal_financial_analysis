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
        filename = os.path.basename(file_path)
        df['file_name']=filename
        engine = create_engine(f"mysql+pymysql://{username}:{password}@{host_name}/{database_name}")
        df.to_sql("credit_card_transaction_files", engine, if_exists="append", index=False)
