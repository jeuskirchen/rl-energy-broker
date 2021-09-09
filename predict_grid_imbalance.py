# entry point to test grid imbalance predictor
import dotenv
from data import game
from util import execution
from models.seq2seq_predictor import Seq2SeqPredictor
from time import sleep
from data.prediction import load_predictions, store_predictions, prediction_exists


# load config
dotenv.load_dotenv(dotenv.find_dotenv())

# initialize global vars
seq2seq_grid_imbalance = Seq2SeqPredictor("grid_imbalance")
print(seq2seq_grid_imbalance)
should_run = True


def predict(_game_id: str, _timeslot: int) -> None:
    print(f"predict(game_id={_game_id}, timeslot={_timeslot})")
    df_prediction = seq2seq_grid_imbalance.get_prediction(_game_id, _timeslot)
    print(df_prediction)
    store_predictions(df_prediction, "prediction")


while True:
    print(f"RUNNING GAMES {game.running_ids()}")
    for game_id in game.running_ids():
        # TODO : add wait group and check for termination condition(s)
        timeslot = game.latest_timeslot(game_id)
        if not prediction_exists(game_id, timeslot, "grid_imbalance"):
            execution.run_async(predict, game_id, timeslot)
    sleep(1)
