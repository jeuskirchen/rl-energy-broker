import os
import dotenv
import pymysql
import sqlalchemy
import pandas as pd


# load config
dotenv.load_dotenv(dotenv.find_dotenv(), verbose=True)


db_user = os.getenv("DB_USER")
db_pw = os.getenv("DB_PW")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_schema = os.getenv("DB_SCHEMA")


def connect() -> pymysql.Connection:
    global db_host, db_user, db_pw, db_schema
    if not db_host:
        raise Exception(f"db_host is None (dotenv location: {dotenv.find_dotenv()})")
    if not db_user:
        raise Exception(f"db_user is None (dotenv location: {dotenv.find_dotenv()})")
    if not db_pw:
        raise Exception(f"db_pw is None (dotenv location: {dotenv.find_dotenv()})")
    if not db_schema:
        raise Exception(f"db_schema is None (dotenv location: {dotenv.find_dotenv()})")
    return pymysql.connect(host=db_host, user=db_user, passwd=db_pw, db=db_schema)


def create_connection_engine():
    global db_user, db_pw, db_host, db_port, db_schema
    connection_string = f'mysql+pymysql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_schema}'
    cnx = sqlalchemy.create_engine(connection_string, echo=False)
    return cnx


def query(query_string: str) -> pd.DataFrame:
    connection = connect()
    df = pd.read_sql(query_string, con=connection)
    connection.close()
    return df
