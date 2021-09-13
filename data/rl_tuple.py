# Based on prediction.py
# import os
import pandas as pd
# import pypika
from data import mysql
from util import execution


observation_space_names = [
    "timeslot",
    "percentual_deviation",
    "day_of_week_0",
    "day_of_week_1",
    "day_of_week_2",
    "day_of_week_3",
    "day_of_week_4",
    "day_of_week_5",
    "day_of_week_6",
    "hour_of_day_0",
    "hour_of_day_1",
    "hour_of_day_2",
    "hour_of_day_3",
    "hour_of_day_4",
    "hour_of_day_5",
    "hour_of_day_6",
    "hour_of_day_7",
    "hour_of_day_8",
    "hour_of_day_9",
    "hour_of_day_10",
    "hour_of_day_11",
    "hour_of_day_12",
    "hour_of_day_13",
    "hour_of_day_14",
    "hour_of_day_15",
    "hour_of_day_16",
    "hour_of_day_17",
    "hour_of_day_18",
    "hour_of_day_19",
    "hour_of_day_20",
    "hour_of_day_21",
    "hour_of_day_22",
    "hour_of_day_23",
    "grid_imbalance_prediction_0",
    "grid_imbalance_prediction_1",
    "grid_imbalance_prediction_2",
    "grid_imbalance_prediction_3",
    "grid_imbalance_prediction_4",
    "grid_imbalance_prediction_5",
    "grid_imbalance_prediction_6",
    "grid_imbalance_prediction_7",
    "grid_imbalance_prediction_8",
    "grid_imbalance_prediction_9",
    "grid_imbalance_prediction_10",
    "grid_imbalance_prediction_11",
    "grid_imbalance_prediction_12",
    "grid_imbalance_prediction_13",
    "grid_imbalance_prediction_14",
    "grid_imbalance_prediction_15",
    "grid_imbalance_prediction_16",
    "grid_imbalance_prediction_17",
    "grid_imbalance_prediction_18",
    "grid_imbalance_prediction_19",
    "grid_imbalance_prediction_20",
    "grid_imbalance_prediction_21",
    "grid_imbalance_prediction_22",
    "grid_imbalance_prediction_23",
    "customer_prosumption_prediction_0",
    "customer_prosumption_prediction_1",
    "customer_prosumption_prediction_2",
    "customer_prosumption_prediction_3",
    "customer_prosumption_prediction_4",
    "customer_prosumption_prediction_5",
    "customer_prosumption_prediction_6",
    "customer_prosumption_prediction_7",
    "customer_prosumption_prediction_8",
    "customer_prosumption_prediction_9",
    "customer_prosumption_prediction_10",
    "customer_prosumption_prediction_11",
    "customer_prosumption_prediction_12",
    "customer_prosumption_prediction_13",
    "customer_prosumption_prediction_14",
    "customer_prosumption_prediction_15",
    "customer_prosumption_prediction_16",
    "customer_prosumption_prediction_17",
    "customer_prosumption_prediction_18",
    "customer_prosumption_prediction_19",
    "customer_prosumption_prediction_20",
    "customer_prosumption_prediction_21",
    "customer_prosumption_prediction_22",
    "customer_prosumption_prediction_23]"
]

action_space_names = [
    "mean_percentual_deviation",
    "std_percentual_deviation",
    "mean_periodic_payment_factor",
    "std_periodic_payment_factor",
    "state_value",
    "prob_new_iteration",
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
]

index = [
    "game_id",
    "latest_timeslot",
    *observation_space_names,
    *action_space_names,
    "reward",
    *["next_" + name for name in observation_space_names]
]

persistence_config = {
    "persistence_file": "",
    "header_line": ";".join(index)
}


def store_tuple(game_id, timeslot, observation, action, reward, next_observation) -> None:
    rl_tuple = [
        str(game_id),
        timeslot,
        *observation,
        *action,
        reward,
        *next_observation
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
