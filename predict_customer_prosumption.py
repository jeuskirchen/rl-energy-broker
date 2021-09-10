# entry point to test customer prosumption predictor
import dotenv
from data import game
from util import execution
from models.seq2seq_predictor import Seq2SeqPredictor
from time import sleep
from data.prediction import store_predictions  # prediction_exists, load_predictions


# load config
dotenv.load_dotenv(dotenv.find_dotenv())

# initialize global vars
seq2seq_customer_prosumption = Seq2SeqPredictor("customer_prosumption")
should_run = True


def predict(_game_id: str, _timeslot: int) -> None:
    print(f"predict(game_id={_game_id}, timeslot={_timeslot})")
    df_prediction = seq2seq_customer_prosumption.get_prediction(_game_id, _timeslot)
    print(df_prediction)
    store_predictions(df_prediction, "prediction")


prediction_exists = []
while True:
    print(f"RUNNING GAMES {game.running_ids()}")
    for game_id in game.running_ids():
        # TODO : add wait group and check for termination condition(s)
        timeslot = game.latest_timeslot(game_id)
        # TODO: do with prediction_exists method instead of appending to list and checking the list
        if (game_id, timeslot) not in prediction_exists: 
            prediction_exists.append((game_id, timeslot))
            execution.run_async(predict, game_id, timeslot)
    sleep(1)
