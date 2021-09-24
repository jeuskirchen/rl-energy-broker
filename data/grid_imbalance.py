import pandas as pd
from data import mysql
from data import game


# FIXME : there must be a way to optimize this...
ENCODER_QUERY = """
    select timeslotIndex, 
           imbalance_meets_weather.dayOfWeek, 
           imbalance_meets_weather.slotInDay, 
           imbalance_meets_weather.temperature, 
           imbalance_meets_weather.cloudCover, 
           imbalance_meets_weather.windSpeed, 
           imbalance_meets_weather.netImbalance
    from (select *
          from (select balance_report.timeslotIndex, 
                       netImbalance
                from ewiis3.balance_report
                where gameId="{game_id}"
                and balance_report.timeslotIndex <= {latest_timeslot}
                order by balance_report.timeslotIndex desc 
                limit {limit}) 
                as grid_imbalance_con
          left join (select *
                from ewiis3.weather_report
                where weather_report.gameId="{game_id}") as wr
                using(timeslotIndex)
          left join (select dayOfWeek, slotInDay, serialNumber
                from ewiis3.timeslot 
                where gameId = "{game_id}") 
                as ts
                on grid_imbalance_con.timeslotIndex = ts.serialNumber)
          as imbalance_meets_weather
    order by timeslotIndex;
    """

# For a given postedTimeslotIndex (latest_timeslot ??), there should be 24 future predictions (proximities 1 through 24)
# https://es2.powertac.uni-koeln.de/gitlab/ewiis3-broker/ewiis3-runner/blob/master/config/ewiis3-schema.sql (lines 377-392)
DECODER_QUERY = """
    select postedTimeslotIndex, 
           targetTimeslotIndex, 
           proximity, 
           dayOfWeek, 
           slotInDay, 
           temperature, 
           cloudCover, 
           windSpeed
    from ewiis3.weather_forecast 
    as wf
    left join (select *
          from ewiis3.timeslot 
          where gameId = "{game_id}") 
          as ts
          on wf.postedTimeslotIndex = ts.serialNumber
    where wf.gameId = "{game_id}" 
    and wf.postedTimeslotIndex = {latest_timeslot}
    order by wf.postedTimeslotIndex
    limit 24;
    """


def load_grid_imbalance(game_id: str, latest_timeslot: int, limit: int = 128) -> [pd.DataFrame, pd.DataFrame]:

    if game_id is None:
        return pd.DataFrame(), pd.DataFrame()

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
