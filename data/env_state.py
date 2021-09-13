import pandas as pd
from data import mysql


# I am assuming the minValueMoney is the relevant tariff rate, but I don't know if that's correct.
# Get MUBP_min (minimal mean usage-based price from among non-EWIIS3 brokers' tariffs)
MUBP_MIN_QUERY = """
    select min(T.avgMinValueMoney) as MUBP_min 
    from (select rate.tariffSpecificationId,
                 tariff_specification.brokerName, 
                 avg(minValueMoney) as avgMinValueMoney
          from rate 
          join tariff_specification
          on rate.tariffSpecificationId = tariff_specification.tariffSpecificationId
          where tariff_specification.powerType = "CONSUMPTION"
          and tariff_specification.brokerName not like "EWIIS3%"
          and gameId = {game_id}
          group by tariffSpecificationId
    ) as T;
    """

# Assume that tariff with highest tariffSpecificationId is the most recent active tariff
# Get mean usage-based price from EWIIS3's active tariff
MUBP_EWIIS3_QUERY = """
    select rate.tariffSpecificationId, 
           tariff_specification.brokerName, 
           tariff_specification.periodicPayment, 
           minValueMoney as MUBP_EWIIS3
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
          limit 24
    ) as T1
    join (select * 
          from prediction
          where type = "prosumption" and target = "customer" 
          and prediction_timeslot = {latest_timeslot}
          and game_id = {game_id}
          limit 24
    ) as T2
    on T1.target_timeslot = T2.target_timeslot
    join timeslot
    on T1.target_timeslot = timeslot.serialNumber;
    """

WEATHER_FORECAST_QUERY = """
    select weatherForecastId, 
           gameId, 
           cloudCover, 
           temperature, 
           windSpeed, 
           postedTimeslotIndex as timeslot, 
           proximity, 
           targetTimeslotIndex as target_timeslot 
    from weather_forecast 
    where postedTimeslotIndex = {latest_timeslot} 
    and gameId = {game_id}
    order by postedTimeslotIndex desc;
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
        prediction_query = PREDICTION_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        prediction_query = prediction_query.replace("\n", " ")
        '''
        weather_forecast_query = WEATHER_FORECAST_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        weather_forecast_query = weather_forecast_query.replace("\n", " ")
        '''

        # Query the data from the database as dataframes
        df_mubp_min = mysql.query(mubp_min_query)
        df_mubp_ewiis3 = mysql.query(mubp_ewiis3_query)
        df_pred = mysql.query(prediction_query).sort_values("proximity", ascending=True)
        # df_weather_forecast = mysql.query(weather_forecast_query).sort_values("proximity", ascending=True)

        print(df_mubp_min)
        print(df_mubp_ewiis3)
        print(df_pred)  # must have length 24 !!
        # print(df_weather_forecast)  # must have length 24 !!

        # TODO: Check if all the predictions are there, for all 24 proximities:
        # What to do if it's not 24?
        if df_pred.shape[0] != 24:
            print("df_pred.shape =", df_pred.shape)
        '''
        if df_weather_forecast.shape[0] != 24:
            print("df_weather_forecast.shape =", df_weather_forecast.shape)
        '''

        # Turn into observation the way it's described in PowerTACEnv
        mubp_min = df_mubp_min["MUBP_min"].iloc[0]
        mubp_ewiis3 = df_mubp_ewiis3["MUBP_EWIIS3"].iloc[0]
        percentual_deviation = (mubp_min - mubp_ewiis3) / abs(mubp_min)  # alpha
        # periodic_payment = df_mubp_ewiis3["periodicPayment"].iloc[0]  # not currently part of observation
        grid_imbalance = df_pred.grid_imbalance_prediction.values
        customer_prosumption = df_pred.customer_prosumption_prediction.values
        day_of_week = df_pred.dow.values
        hour_of_day = df_pred.hod.values
        # temperature_forecast = df_weather_forecast.temperature
        # wind_speed_forecast = df_weather_forecast.windSpeed
        # cloud_cover_forecast = df_weather_forecast.cloudCover

        return (
            latest_timeslot,
            percentual_deviation,
            # periodic_payment_factor,
            *day_of_week,
            *hour_of_day,
            *grid_imbalance,
            *customer_prosumption,
        )

    except Exception as e:
        print(f'Error occured while requesting grid imbalances from db.', e)
        return pd.DataFrame(), None
