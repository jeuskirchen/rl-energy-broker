# Based on prediction.py
# import os
import pandas as pd
# import pypika
# from data import mysql
# from util import execution


# Probably store in multiple databases, e.g. one for tariff and one for wholesale
# Because in wholesale actions (bids) you have to consider both action_timeslot and target_timeslot


persistence_config = {
    "persistence_file": "",
    # "header_line": "target_timeslot;action;action_timeslot;proximity;game_id;target;type"
}


def store_tuple(game_id, latest_timeslot, observation, action, reward, next_observation) -> None:
    # A tuple looks like this (state, action, reward, next_state)
    pass


def load_action(tariff_table_name: str, wholesale_table_name: str, game_id: str, target=None, type=None) -> pd.DataFrame:
    # TODO
    return pd.DataFrame()


def persist_to_file(df_tariff_action: pd.DataFrame, df_wholesale_actions: pd.DataFrame) -> None:
    pass


def create_persistence_file() -> None:
    # TODO
    pass


def get_action_file_path() -> str:
    # TODO
    return ""


def tuple_exists(game_id: str, timeslot: int) -> bool:
    # TODO
    return False
