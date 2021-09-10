import pandas as pd
from data import mysql


WEATHER_REPORT_QUERY = """
select weatherReportId, gameId, cloudCover, temperature, windSpeed, timeslotIndex as timeslot  
from weather_report 
where timeslotIndex <= {latest_timeslot} 
and timeslotIndex > {latest_timeslot}-{past_window_size}
and gameId = {game_id}
order by timeslotIndex desc 
"""

WEATHER_FORECAST_QUERY = """
select weatherForecastId, gameId, cloudCover, temperature, windSpeed, postedTimeslotIndex as timeslot, proximity, targetTimeslotIndex as target_timeslot 
from weather_forecast 
where postedTimeslotIndex = {latest_timeslot} 
and gameId = {game_id}
order by postedTimeslotIndex desc;
"""

# Not sure if correct!!
# I am assuming the minValueMoney is the relevant tariff rate
MUBP_MIN_QUERY = """
select min(T.avgMinValueMoney) as MUBP_min 
from (
select rate.tariffSpecificationId, tariff_specification.brokerName, avg(minValueMoney) as avgMinValueMoney
from rate 
join tariff_specification
on rate.tariffSpecificationId = tariff_specification.tariffSpecificationId
where tariff_specification.powerType = "CONSUMPTION"
and tariff_specification.brokerName not like "EWIIS3%"
and gameId = {game_id}
group by tariffSpecificationId
) as T;
"""

MUBP_EWIIS3_QUERY = """
select rate.tariffSpecificationId, tariff_specification.brokerName, tariff_specification.periodicPayment, minValueMoney as MUBP_EWIIS3
from rate 
join tariff_specification
on rate.tariffSpecificationId = tariff_specification.tariffSpecificationId
where tariff_specification.powerType = "CONSUMPTION"
and tariff_specification.brokerName like "EWIIS3%"
and gameId = {game_id}
order by tariffSpecificationId desc
limit 1;
"""

PREDICTION_QUERY = """
select T1.predictionId, 
T2.predictionId, T1.game_id, T2.game_id, T1.proximity, T2.proximity, T1.target_timeslot, T2.target_timeslot, timeslot.dayOfWeek as dow, timeslot.slotInDay as hod, timeslot.isWeekend, T1.prediction as grid_imbalance_prediction, T2.prediction as customer_prosumption_prediction
from (select * from prediction 
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


def load_env_state(game_id: str, latest_timeslot: int, past_window_size: int = 128):

    if game_id is None:
        return pd.DataFrame(), game_id

    try:
        # Put variable values into query string
        mubp_min_query = MUBP_MIN_QUERY.format(
            game_id=game_id,
            past_window_size=past_window_size)
        mubp_min_query = mubp_min_query.replace("\n", " ")
        mubp_ewiis3_query = MUBP_EWIIS3_QUERY.format(
            game_id=game_id,
            past_window_size=past_window_size)
        mubp_ewiis3_query = mubp_ewiis3_query.replace("\n", " ")
        weather_report_query = WEATHER_REPORT_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        weather_report_query = weather_report_query.replace("\n", " ")
        weather_forecast_query = WEATHER_FORECAST_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        weather_forecast_query = weather_forecast_query.replace("\n", " ")
        prediction_query = PREDICTION_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        prediction_query = prediction_query.replace("\n", " ")
        # Query the data from the database as dataframes
        df_mubp_min = mysql.query(mubp_min_query)
        df_mubp_ewiis3 = mysql.query(mubp_ewiis3_query)
        df_weather_report = mysql.query(weather_report_query)
        df_weather_forecast = mysql.query(weather_forecast_query)
        df_pred = mysql.query(prediction_query)  # grid imbalance and customer prosumption predictions
        # Turn into observation the way it's described in PowerTACEnv
        mubp_min = df_mubp_min["MUBP_min"].iloc[0]
        mubp_ewiis3 = df_mubp_ewiis3["MUBP_EWIIS3"].iloc[0]
        percentual_deviation = (mubp_min - mubp_ewiis3) / abs(mubp_min)  # alpha
        periodic_payment = df_mubp_ewiis3["periodicPayment"].iloc[0]  # beta
        # ...
        print(df_mubp_min)
        print(df_mubp_ewiis3)
        print(df_weather_report)
        print(df_weather_forecast)
        print(df_pred)
        return percentual_deviation, periodic_payment

    except Exception as e:
        print(f'Error occured while requesting grid imbalances from db.')
        return pd.DataFrame(), None
