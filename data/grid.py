import pandas as pd
from data import mysql
from data import game


# I split it into two queries

# FIXME : there must be a way to optimize this...
ENCODER_QUERY = """
    SELECT timeslotIndex, imbalance_meets_weather.dayOfWeek, imbalance_meets_weather.slotInDay, imbalance_meets_weather.temperature, imbalance_meets_weather.cloudCover, imbalance_meets_weather.windSpeed, imbalance_meets_weather.netImbalance
    FROM (SELECT *
          FROM (SELECT balance_report.timeslotIndex, netImbalance
                FROM ewiis3.balance_report
                WHERE gameId="{game_id}"
                AND balance_report.timeslotIndex <= {latest_timeslot}
                ORDER BY balance_report.timeslotIndex DESC LIMIT {limit}) AS grid_imbalance_con
          LEFT JOIN (SELECT *
                FROM ewiis3.weather_report
                WHERE weather_report.gameId="{game_id}") AS wr
                USING(timeslotIndex)
          LEFT JOIN (SELECT dayOfWeek, slotInDay, serialNumber
                FROM ewiis3.timeslot WHERE gameId = "{game_id}") AS ts
                ON grid_imbalance_con.timeslotIndex = ts.serialNumber)
          AS imbalance_meets_weather
    ORDER BY timeslotIndex;
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


def load_grid_imbalance(game_id: str, latest_timeslot: int, limit: int = 128) -> [pd.DataFrame, pd.DataFrame]:

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
        print(f'Error occured while requesting grid imbalances from db.')
        return pd.DataFrame(), pd.DataFrame()
