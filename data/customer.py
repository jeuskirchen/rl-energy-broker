import pandas as pd
from data import mysql


# FIXME : there must be a way to optimize this...
ENCODER_QUERY = """
    select postedTimeslotIndex, 
           prosumption_meets_weather.dayOfWeek, 
           prosumption_meets_weather.slotInDay, 
           prosumption_meets_weather.temperature, 
           prosumption_meets_weather.cloudCover, 
           prosumption_meets_weather.windSpeed, 
           prosumption_meets_weather.SUM_kWH
    from (select *
          from (select postedTimeslotIndex, 
                       SUM(kWH) as SUM_kWH
                from ewiis3.tariff_transaktion
                where gameId="{game_id}" 
                and (txType="CONSUME" or txType="PRODUCE")
                and tariff_transaktion.postedTimeslotIndex <= {latest_timeslot}
                group by postedTimeslotIndex
                order by postedTimeslotIndex desc 
                limit {limit}) 
                as customer_prod_con
          left join (select *
                from ewiis3.weather_report
                where weather_report.gameId="{game_id}") 
                as wr
                on customer_prod_con.postedTimeslotIndex = wr.timeslotIndex
          left join (select dayOfWeek, slotInDay, serialNumber
                from ewiis3.timeslot 
                where gameId = "{game_id}") 
                as ts
                on customer_prod_con.postedTimeslotIndex = ts.serialNumber)
          as prosumption_meets_weather
    order by postedTimeslotIndex;
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
          from ewiis3.timeslot where gameId = "{game_id}") 
          as ts
          on wf.postedTimeslotIndex = ts.serialNumber
    where wf.gameId = "{game_id}" 
    and wf.postedTimeslotIndex = {latest_timeslot}
    order by wf.postedTimeslotIndex
    limit 24;
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
