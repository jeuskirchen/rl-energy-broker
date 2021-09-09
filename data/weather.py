import pandas as pd
from data import mysql
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())


def forecast(game_id: str) -> [pd.DataFrame, str]:
    if game_id is None:
        return pd.DataFrame(), game_id
    try:
        return mysql.query('SELECT t.* FROM ewiis3.weather_forecast t WHERE gameId="{}" ORDER BY postedTimeslotIndex DESC LIMIT 24'.format(game_id)), game_id
    except Exception as e:
        # FIXME : add coherent logging
        print('Error occured while requesting weather forecast from db.')
        return pd.DataFrame(), game_id
