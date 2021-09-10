import os
from typing import List
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import pickle
# TODO : inherit from OpenAI baseline agent
# does baseline agent already handle target networks etc. or do I have to do this myself??
# https://github.com/DLR-RM/stable-baselines3
# https://stable-baselines3.readthedocs.io/en/master/
# Could this helpful? https://github.com/DLR-RM/rl-baselines3-zoo
# https://github.com/openai/baselines
# FIXME : perhaps don't call them alpha, beta but simply percentual_deviation and perioid_payment_factor


os.environ["CUDA_VISIBLE_DEVICES"] = ""


class Agent:

    def __init__(self, game_id=None) -> None:
        self.game_id = game_id

    def get_action(self, timeslot: int) -> List:
        """
        """

        # Predict the action and value

        # Input: alpha, beta, grid imbalance predictions, customer prosumption predictions, hour-of-day, day-of-week
        # temperature_forecast, wind_speed_forecast, cloud_cover_forecast
        alpha = calculate_alpha(None)  # pass tariff_rates!!

        # Tariff actions: mean_alpha, std_alpha, mean_beta, std_beta, value, prob_next_iteration
        #   alpha: percentual deviation of EWIIS3 MUBP from active consumption tariff
        #   beta: (continuous) periodic payment factor
        # neural network
        # how to do this with the LSTM?! do I need to store the hidden and cell states as object fields?
        # FIXME : Does it make sense to put the tariff actions into a dataframe? or just do tuple?

        # Wholesale actions: (electricity_amount, limit_price, is_market_order) for each timeslot in (1, ..., 24)
        # Perhaps even a transformer that refines the grid imbalance and customer prosumption into wholesale bids.
        # Alternatively, another Seq2Seq+attention model that takes earlier predictions as the encoder input and
        # a decoder that outputs the bids.
        # This is where a MCTS could also be implemented in the future for planning ahead.
        #
        #

        # df_tariff_action = pd.DataFrame()
        # df_wholesale_action = pd.DataFrame()

        # TODO : put it in the right format as described in the gym environment ! (see PowerTACEnv)

        return []


def calculate_alpha(tariff_rates) -> float:
    # TODO
    # MUBP = the mean usage-based price = average of prices of all rates inside a given tariff
    # MUBP_min is the minimum MUBP across all tariffs from competing brokers (not EWIIS3 itself)
    # MUBP_ewiis3 is the MUBP of the EWIIS3 broker
    # Then, alpha = (MUBP_min - MUBP_ewiis3) / np.abs(MUBP_min)
    return 0.0
