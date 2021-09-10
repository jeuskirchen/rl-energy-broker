import pandas as pd
from data import mysql
from data import game
from typing import Union

'''
The goal of env_state.py is to get all the data I need about the environment which can then be passed to the gym
environment object. 
 - tariff rates of all brokers 
 - grid imbalance predictions
 - customer prosumption predictions
 - day-of-week
 - hours-of-day
 - temperature forecast
 - wind speed forecast
 - cloud cover forecast 
'''

WEATHER_QUERY = """
select weatherReportId, gameId, cloudCover, temperature, windSpeed, timeslotIndex as timeslot  
from weather_report 
where timeslotIndex <= {latest_timeslot} 
and timeslotIndex > {latest_timeslot}-128
and game_id = {game_id}
order by timeslotIndex desc 
"""

# Not sure if correct!!
TARIFF_QUERY = """
select rate.tariffSpecificationId, tariff_specification.brokerName, minValueMoney as MUBP_EWIIS3
from rate 
join tariff_specification
on rate.tariffSpecificationId = tariff_specification.tariffSpecificationId
where tariff_specification.powerType = "CONSUMPTION"
and tariff_specification.brokerName like "EWIIS3%"
order by tariffSpecificationId desc
limit 1;
"""

PREDICTION_QUERY = """
select T1.predictionId,
       T2.predictionId,
       T1.game_id,
       T2.game_id,
       T1.proximity,
       T2.proximity,
       T1.target_timeslot,
       T2.target_timeslot,
       timeslot.dayOfWeek as dow, 
       timeslot.slotInDay as hod, 
       timeslot.isWeekend, 
       T1.prediction as grid_imbalance_prediction,
       T2.prediction as customer_prosumption_prediction
from (select * 
      from prediction
      where type = "imbalance" and target = "grid" 
      and prediction_timeslot = {latest_timeslot}
      and game_id = {game_id}
      limit 24) 
      as T1
join (select * 
      from prediction
      where type = "prosumption" and target = "customer" 
      and prediction_timeslot = {latest_timeslot}
      and game_id = {game_id}
      limit 24) 
      as T2
on T1.target_timeslot = T2.target_timeslot
join timeslot
on T1.target_timeslot = timeslot.serialNumber;
"""


def load_env_state(game_id: str, latest_timeslot: int, limit: int = 128) -> [pd.DataFrame, Union[int, None]]:

    if game_id is None:
        return pd.DataFrame(), game_id

    try:
        # Put variable values into query string
        tariff_query = TARIFF_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot,
            limit=limit)
        weather_query = WEATHER_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        prediction_query = PREDICTION_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        # Query the data from the database as dataframes
        df_tariff = mysql.query(tariff_query)
        df_weather = mysql.query(weather_query)
        df_pred = mysql.query(prediction_query)
        # TODO : put the dataframes into a single observation
        #  the way it's described in the gym observation space (see PowerTACEnv)
        return df_tariff, df_weather, df_pred

    except Exception as e:
        print(f'Error occured while requesting grid imbalances from db.')
        return pd.DataFrame(), None
