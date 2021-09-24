import pandas as pd
from data import mysql


# TODO : make sure that it only goes back for as long as this tariff has been active for!
#  For now, I will simply limit it to the past 128 timeslots.
# For now, it doesn't distinguish between any tariffs, goes back all the way to the beginning of the game,
# and doesn't explicitly account for fees
REWARD_QUERY = """
    select sum(kWH) as sum_kWH
           sum(charge) as sum_charge
    from ewiis3.tariff_transaktion
    where gameId="{game_id}" 
    and powerType="CONSUMPTION"
    and tariff_transaktion.postedTimeslotIndex <= {latest_timeslot}
    and brokerName like "%EWIIS3%"
    order by posteedTimeslotIndex desc
    limit 128
    """


def load_reward(game_id: str, latest_timeslot: int) -> pd.DataFrame:

    if game_id is None:
        return pd.DataFrame()

    try:
        reward_query = REWARD_QUERY.format(
            game_id=game_id,
            latest_timeslot=latest_timeslot)
        reward_dataframe = mysql.query(reward_query)
        print("reward_dataframe")
        print(reward_dataframe)
        return reward_dataframe

    except Exception as e:
        print(f'Error occured while requesting mega query from db.')
        return pd.DataFrame()
