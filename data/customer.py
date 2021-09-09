import pandas as pd
from data import mysql
from data import game


# I split it into two queries

# FIXME : there must be a way to optimize this...
ENCODER_QUERY = """
    SELECT postedTimeslotIndex, prosumption_meets_weather.dayOfWeek, prosumption_meets_weather.slotInDay, prosumption_meets_weather.temperature, prosumption_meets_weather.cloudCover, prosumption_meets_weather.windSpeed, prosumption_meets_weather.SUM_kWH
    FROM (SELECT *
          FROM (SELECT postedTimeslotIndex, SUM(kWH) as SUM_kWH
                FROM ewiis3.tariff_transaktion
                WHERE gameId="{game_id}" AND (txType="CONSUME" OR txType="PRODUCE")
                AND tariff_transaktion.postedTimeslotIndex <= {latest_timeslot}
                GROUP BY postedTimeslotIndex
                ORDER BY postedTimeslotIndex DESC LIMIT {limit}) AS customer_prod_con
          LEFT JOIN (SELECT *
                FROM ewiis3.weather_report
                WHERE weather_report.gameId="{game_id}") AS wr
                ON customer_prod_con.postedTimeslotIndex = wr.timeslotIndex
          LEFT JOIN (SELECT dayOfWeek, slotInDay, serialNumber
                FROM ewiis3.timeslot WHERE gameId = "{game_id}") AS ts
                ON customer_prod_con.postedTimeslotIndex = ts.serialNumber)
          AS prosumption_meets_weather
    ORDER BY postedTimeslotIndex;
    """

# For a given postedTimeslotIndex (latest_timeslot ??), there should be 24 future predictions (proximities 1 through 24)
# https://es2.powertac.uni-koeln.de/gitlab/ewiis3-broker/ewiis3-runner/blob/master/config/ewiis3-schema.sql (lines 377-392)
# Do I have to limit to 24 future timeslots or is it always just 24 future timeslots?
DECODER_QUERY = """
    SELECT postedTimeslotIndex, targetTimeslotIndex, proximity, dayOfWeek, slotInDay, temperature, cloudCover, windSpeed
    FROM ewiis3.weather_forecast AS wf
    LEFT JOIN (SELECT *
          FROM ewiis3.timeslot WHERE gameId = "{game_id}") AS ts
          ON wf.postedTimeslotIndex = ts.serialNumber
    WHERE wf.gameId="{game_id}" AND wf.postedTimeslotIndex={latest_timeslot}
    ORDER BY wf.postedTimeslotIndex;
    """


def load_prosumption_weather_time(game_id: str, latest_timeslot: int, limit: int = 128) -> [pd.DataFrame, pd.DataFrame]:

    if game_id is None:
        return pd.DataFrame(), game_id

    try:
        encoder_query = ENCODER_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot,
            limit=limit)
        encoder_dataframe = mysql.query(encoder_query)

        decoder_query = DECODER_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        decoder_dataframe = mysql.query(decoder_query)

        return encoder_dataframe, decoder_dataframe

    except Exception as e:
        print(f'Error occured while requesting mega query from db.')
        return pd.DataFrame(), pd.DataFrame()
