import os
from typing import Any
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import pickle
import stable_baselines


os.environ["CUDA_VISIBLE_DEVICES"] = ""


class Agent:
    """
    TODO : inherit from OpenAI baseline agent
    does baseline agent already handle target networks etc. or do I have to do this myself??
    https://github.com/DLR-RM/stable-baselines3
    https://stable-baselines3.readthedocs.io/en/master/
    Could this helpful? https://github.com/DLR-RM/rl-baselines3-zoo
    https://github.com/openai/baselines
    FIXME : perhaps don't call them alpha, beta but simply percentual_deviation and perioid_payment_factor
    """

    def __init__(self, game_id=None) -> None:
        self.game_id = game_id

    def get_action_and_value(self, observation: object) -> [Any, Any]:
        """
        Compute the action and value from the observation.
        """

        # Observation:
        #   latest_timeslot (just so I have this information in here, not used by the agent)
        #   percentual_deviation
        #   periodic_payment_factor (not sure if used)
        #   grid_imbalance
        #   customer_prosumption
        #   day_of_week
        #   hour_of_day
        #   temperature_forecast
        #   wind_speed_forecast
        #   cloud_cover_forecast

        # Neural network:
        # how to do this with the LSTM?! do I need to store the hidden and cell states as object fields?
        # see how LSTM + gym are usually used together
        # Perhaps even a transformer that refines the grid imbalance, customer prosumption, etc. into wholesale bids.
        # Alternatively, another Seq2Seq+attention model that takes earlier predictions as the encoder input and
        # a decoder that outputs the bids.
        # This is where a MCTS could also be implemented in the future for planning ahead.

        # TODO : put it in the right format as described in the gym environment ! (see PowerTACEnv)
        # Tariff action:
        #   mean_percentual_deviation
        #   std_percentual_deviation
        #   mean_periodic_payment_factor
        #   std_periodic_payment_factor
        #   prob_new_iteration
        # Wholesale action:
        #   electricity_amount (for 24 subsequent timeslots)
        #   limit_price (for 24 subsequent timeslots)
        #   is_market_order (for 24 subsequent timeslots)
        # State value:
        #   value (or advantage, depending on the algorithm)

        action = None  # placeholder
        value = None  # placeholder

        return action, value


def calculate_alpha(tariff_rates) -> float:
    # TODO
    # MUBP = the mean usage-based price = average of prices of all rates inside a given tariff
    # MUBP_min is the minimum MUBP across all tariffs from competing brokers (not EWIIS3 itself)
    # MUBP_ewiis3 is the MUBP of the EWIIS3 broker
    # Then, alpha = (MUBP_min - MUBP_ewiis3) / np.abs(MUBP_min)
    return 0.0
