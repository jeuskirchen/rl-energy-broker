from typing import List
from data.mysql import query


def all_ids() -> List[str]:
    return query_game_ids('SELECT DISTINCT(t.gameId) FROM ewiis3.timeslot AS t')


def finished_ids() -> List[str]:
    return query_game_ids('SELECT DISTINCT(t.gameId) FROM ewiis3.finished_game AS t')


def running_ids() -> List[str]:
    return [gameId for gameId in all_ids() if gameId not in finished_ids()]


def latest_timeslot(game_id: str) -> int:
    try:
        sql_statement = 'SELECT * FROM ewiis3.timeslot AS t WHERE t.gameId ="{}" ORDER BY timeslotId DESC LIMIT 1;'.format(game_id)
        df_latest = query(sql_statement)
        return df_latest['serialNumber'].values[0]
    except Exception as e:
        print('Error occured while requesting latest timeslot for gameId {} from db.'.format(game_id), e)
        return None


def query_game_ids(query_string: str) -> List[str]:
    try:
        return query(query_string)['gameId'].values.tolist()
    except Exception as e:
        # FIXME : is there some sort of global logging scheme?
        print(query_string)
        print('an error occured while requesting game ids from db', e)
        return []
