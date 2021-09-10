import numpy as np
import pandas as pd
import gym
from gym.spaces import Box
from ..spaces.OneHot import OneHot
from ..data.env_state import load_env_state


class PowerTACEnv(gym.Env):
    """PowerTAC environment based on gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, game_id: int):
        super(PowerTACEnv, self).__init__()
        self.game_id = game_id
        # Define action and observation space
        # Assumption: actions are the non-normalized values, i.e. they are denormalized before being passed to env
        # They are not the input or output to the neural network. The network inputs/outputs would have to be adjusted
        # inside the agent to turn them into the proper values as specified here:
        self.action_space = gym.spaces.Dict({
            # Tariff action:
            "mean_alpha": Box(-np.inf, np.inf, shape=(1,)),  # alpha: percentual deviation
            "std_alpha": Box(-np.inf, np.inf, shape=(1,)),
            "mean_beta": Box(0., 10., shape=(1,)),  # beta: periodic payment factor
            "std_beta": Box(-np.inf, np.inf, shape=(1,)),
            "state_value": Box(-np.inf, np.inf, shape=(1,)),
            "prob_new_iteration": Box(0.0, 1.0, shape=(1,)),  # skip for now
            # Wholesale action:
            "electricity_amount": Box(-np.inf, np.inf, shape=(24,)),  # negative when we buy?
            "limit_price": Box(-np.inf, np.inf, shape=(24,)),  # negative when we buy?
            "is_market_order": Box(0.0, 1.0, shape=(24,)),
        })
        self.observation_space = gym.spaces.Dict({
            "alpha": Box(-np.inf, np.inf, shape=(1,)),
            "grid_imbalance": Box(-np.inf, np.inf, shape=(24,)),
            "customer_prosumption": Box(-np.inf, np.inf, shape=(24,)),
            "day_of_week": gym.spaces.Tuple([OneHot(size=7) for _ in range(1, 24+1)]),
            "hour_of_day": gym.spaces.Tuple([OneHot(size=24) for _ in range(1, 24+1)]),
            "temperature_forecast": Box(-np.inf, np.inf, shape=(24,)),
            "wind_speed_forecast": Box(-np.inf, np.inf, shape=(24,)),
            "cloud_cover_forecast": Box(-np.inf, np.inf, shape=(24,)),
            # more features? like the agent's current tariff and wholesale state?
        })

    def step(self, action) -> [object, float, bool, dict]:
        """
        Maps action to (observation: object, reward: flaot, done: bool, info: dict)
        """
        observation = load_env_state(self.game_id, past_window_size=128)
        reward = calculate_reward(observation)
        done = False  # TODO
        info = {}  # TODO
        return observation, reward, done, info

    def reset(self):
        # TODO : returns initial observation after creating the environment
        # Do some kind of nil observation?
        observation = None
        return observation

    def render(self, mode="human"):
        # TODO
        # e.g. print current observation (how do you usually access the observation from here?)
        pass

    def close(self):
        # TODO 
        pass


def calculate_reward(observation: object) -> float:
    # TODO : see formula from new MDP formulation
    return 0.0


'''
# This is what it looks like in ewiis3_python_scripts: 
def _get_reward(self):
    """
    Source: ewiis3-broker/ewiis3_python_scripts/blob/master/src/ewiis3_python_scripts/envs/tariff_env.py
    """
    all_game_ids = db.get_running_gameIds()
    game_id = all_game_ids[0]
    df_prosumption = db.load_consumption_tariff_prosumption(game_id, 24)
    df_prosumption["grid_prosumption"] = df_prosumption["totalProduction"] - df_prosumption["totalConsumption"]
    # df_earnings = db.load_consumption_tariff_earnings(game_id, 24)

    # print(df_prosumption.columns)
    print(numpy.corrcoef(df_prosumption["grid_prosumption"], df_prosumption["SUM(t.kWh)"]))
    # print(df_earnings.head())
    return np.random.randint(0, 5)
'''