import os
import pandas as pd
import pypika
from data import mysql
from util import execution


persistence_config = {
    "persistence_file": "",
    "header_line": "target_timeslot;prediction;prediction_timeslot;proximity;game_id;target;type"
}


def store_predictions(df_predictions: pd.DataFrame, table_name: str) -> None:
    # FIXME : make that part of a convention/load from config
    print("store_predictions(df_predictions, table_name)")
    execution.run_async(persist_to_file, df_predictions)
    cnx = mysql.create_connection_engine()
    df_predictions.to_sql(name=table_name, schema='ewiis3', con=cnx, if_exists='append', index=False)


def load_predictions(table_name: str, game_id: str, target=None, type=None) -> pd.DataFrame:
    try:
        prediction_table = pypika.Table(table_name)
        query = pypika.Query.from_(prediction_table).select('*')
        where_clause = ' WHERE'
        if game_id:
            query.where()
            where_clause = f'{where_clause} game_id="{game_id}"'
        if target:
            and_or_not = 'AND ' if where_clause.find('=') > -1 else ''
            where_clause = f'{where_clause} {and_or_not}target="{target}"'
        if type:
            and_or_not = 'AND ' if where_clause.find('=') > -1 else ''
            where_clause = f'{where_clause} {and_or_not}type="{type}"'
        if not game_id and not target and not type:
            where_clause = ''
        sql_statement = f"SELECT * FROM {table_name}{where_clause}"
        return mysql.query(sql_statement)
    except Exception as e:
        print(e)
        print('Error occured while requesting `{}` table with target {} and type {} for game_id {}from db.'.format(table_name, target, type, game_id))
        return pd.DataFrame()


def persist_to_file(df_predictions: pd.DataFrame) -> None:
    if not os.path.isfile(get_prediction_file_path()):
        create_persistence_file()
    str_rep = df_predictions.to_csv(sep=";", header=False, index=False)
    file = open(get_prediction_file_path(), 'a+')
    file.write(str_rep)
    file.close()
    print("stored predictions in " + get_prediction_file_path())


def create_persistence_file() -> None:
    # FIXME : add header line not only if file exists but also if it's empty
    file = open(get_prediction_file_path(), "w+")
    file.write(persistence_config["header_line"] + "\n")
    file.close()


def get_prediction_file_path() -> str:
    if persistence_config["persistence_file"] == "":
        persistence_config["persistence_file"] = os.getenv("PREDICTION_FILE")
    # FIXME : throw error if no path is given / is not writeable
    return persistence_config["persistence_file"]


def prediction_exists(game_id: int, timeslot: int, target_and_type: str) -> bool:
    # TODO: check database
    _target, _type = target_and_type.split("_")  # target="grid_imbalance" -> _target="grid", _type="imbalance"
    return False
