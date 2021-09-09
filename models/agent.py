import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from data.environment_data import load_prosumption_weather_time
import pickle
from time import time


os.environ["CUDA_VISIBLE_DEVICES"] = ""


class Agent:


    def __init__(self, target: str, time_horizon: int = 128) -> None:
        pass


    def get_outputs(self, game_id: int, timeslot: int) -> pd.DataFrame:
        '''
        '''
        start_time = time()

        # Load all the data we need
        #
        #
        #

        # Predict the action and value
        # Model output: mean_alpha, std_alpha, mean_beta, std_beta, value, prob_next_iteration
        #
        #
        #

        # Take the action in the environment
        #
        #
        #

        return df_agent_outputs
