# Based on prediction.py
# import os
import pandas as pd
# import pypika
from data import mysql
from util import execution


# it's actually both the action and the state value
# Note: originally, this included the state value as well, but the way stable-baseline's
# actor-critic code works is that it keeps track of the value itself (which makes sense,
# as it is needed for the algorithm).
action_space_names = [
    "mean_percentual_deviation",
    "std_percentual_deviation",
    "mean_periodic_payment_factor",
    "std_periodic_payment_factor",
    "prob_new_iteration",
]
# I removed the wholesale actions for now:
"""
    "wholesale_electricity_amount_0",
    "wholesale_electricity_amount_1",
    "wholesale_electricity_amount_2",
    "wholesale_electricity_amount_3",
    "wholesale_electricity_amount_4",
    "wholesale_electricity_amount_5",
    "wholesale_electricity_amount_6",
    "wholesale_electricity_amount_7",
    "wholesale_electricity_amount_8",
    "wholesale_electricity_amount_9",
    "wholesale_electricity_amount_10",
    "wholesale_electricity_amount_11",
    "wholesale_electricity_amount_12",
    "wholesale_electricity_amount_13",
    "wholesale_electricity_amount_14",
    "wholesale_electricity_amount_15",
    "wholesale_electricity_amount_16",
    "wholesale_electricity_amount_17",
    "wholesale_electricity_amount_18",
    "wholesale_electricity_amount_19",
    "wholesale_electricity_amount_20",
    "wholesale_electricity_amount_21",
    "wholesale_electricity_amount_22",
    "wholesale_electricity_amount_23",
    "wholesale_limit_price_0",
    "wholesale_limit_price_1",
    "wholesale_limit_price_2",
    "wholesale_limit_price_3",
    "wholesale_limit_price_4",
    "wholesale_limit_price_5",
    "wholesale_limit_price_6",
    "wholesale_limit_price_7",
    "wholesale_limit_price_8",
    "wholesale_limit_price_9",
    "wholesale_limit_price_10",
    "wholesale_limit_price_11",
    "wholesale_limit_price_12",
    "wholesale_limit_price_13",
    "wholesale_limit_price_14",
    "wholesale_limit_price_15",
    "wholesale_limit_price_16",
    "wholesale_limit_price_17",
    "wholesale_limit_price_18",
    "wholesale_limit_price_19",
    "wholesale_limit_price_20",
    "wholesale_limit_price_21",
    "wholesale_limit_price_22",
    "wholesale_limit_price_23",
    "is_market_order_0",
    "is_market_order_1",
    "is_market_order_2",
    "is_market_order_3",
    "is_market_order_4",
    "is_market_order_6",
    "is_market_order_5",
    "is_market_order_7",
    "is_market_order_8",
    "is_market_order_9",
    "is_market_order_10",
    "is_market_order_11",
    "is_market_order_12",
    "is_market_order_13",
    "is_market_order_14",
    "is_market_order_15",
    "is_market_order_16",
    "is_market_order_17",
    "is_market_order_18",
    "is_market_order_19",
    "is_market_order_20",
    "is_market_order_21",
    "is_market_order_22",
    "is_market_order_23",
"""

# Only things that are relevant right now:
index = [
    "game_id",
    "action_timeslot",
    *action_space_names,  # including the state value
]

persistence_config = {
    "persistence_file": "",
    "header_line": ";".join(index)
}


def store_tuple(game_id, timeslot, observation, action, reward, next_observation) -> None:
    # Full tuple:
    rl_tuple = [
        str(game_id),
        timeslot,
        *action,  # including the state value
    ]
    df_tuple = pd.DataFrame(rl_tuple, index=index).T
    execution.run_async(persist_to_file, df_tuple)
    cnx = mysql.create_connection_engine()
    df_tuple.to_sql(name="rl_tuple", schema='ewiis3', con=cnx, if_exists='append', index=False)


def load_action(game_id: str) -> pd.DataFrame:
    try:
        return mysql.query(f"select * from rl_tuple where game_id={game_id}")
    except Exception as e:
        print(e)
        print(f'Error occured while requesting `rl_tuple` table for game_id {game_id} from db.')
        return pd.DataFrame()


def persist_to_file(df_tuple: pd.DataFrame) -> None:
    if not os.path.isfile(get_tuple_file_path()):
        create_persistence_file()
    str_rep = df_tuple.to_csv(sep=";", header=False, index=False)
    file = open(get_tuple_file_path(), 'a+')
    file.write(str_rep)
    file.close()
    print("stored predictions in " + get_tuple_file_path())


def create_persistence_file() -> None:
    # FIXME : add header line not only if file exists but also if it's empty
    file = open(get_tuple_file_path(), "w+")
    file.write(persistence_config["header_line"] + "\n")
    file.close()


def get_tuple_file_path() -> str:
    if persistence_config["persistence_file"] == "":
        persistence_config["persistence_file"] = os.getenv("RL_TUPLE_FILE")
    # FIXME : throw error if no path is given / is not writeable
    return persistence_config["persistence_file"]


def tuple_exists(game_id: str, timeslot: int) -> bool:
    # TODO
    return False
