import pandas as pd
from data import mysql
from data import game

'''
The goal of environment_data.py is to get all the data I need about the environment which can then be passed to the gym
environment object. 
'''


ENVIRONMENT_QUERY = """
    """


def load_environment_data(game_id: str, latest_timeslot: int, limit: int = 128) -> pd.DataFrame:

    if game_id is None:
        return pd.DataFrame(), game_id

    try:
        environment_query = ENVIRONMENT_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot,
            limit=limit)
        environment_dataframe = mysql.query(environment_query)

        return environment_dataframe

    except Exception as e:
        print(f'Error occured while requesting grid imbalances from db.')
        return pd.DataFrame(), pd.DataFrame()
