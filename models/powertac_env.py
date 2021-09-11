import numpy as np
import gym
from gym.spaces import Box, Discrete
from ..spaces.OneHot import OneHot
from ..data.env_state import load_env_state
from data import game


class PowerTACEnv(gym.Env):
    """
    PowerTAC environment based on gym interface
    https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/master/5_custom_gym_env.ipynb#scrollTo=BJbeiF0RUN-p
    """
    metadata = {'render.modes': ['console']}

    def __init__(self, game_id: str):
        super(PowerTACEnv, self).__init__()
        self.game_id = game_id
        self.latest_observation = None
        # Define observation and action space
        self.observation_space = gym.spaces.Dict({
            "timeslot": Discrete(10000),  # assuming 10000 is maximum number of timeslots per game
            # Tariff market features:
            "percentual_deviation": Box(-np.inf, np.inf, shape=(1,)),
            "periodic_payment_factor": Box(-np.inf, np.inf, shape=(1,)),
            # more features? like the agent's current tariff and wholesale state?
            # e.g. number of timeslots since broker last published a tariff, etc.
            # Predictions:
            "grid_imbalance": Box(-np.inf, np.inf, shape=(24,)),
            "customer_prosumption": Box(-np.inf, np.inf, shape=(24,)),
            # Temporal & weather features:
            "day_of_week": gym.spaces.Tuple([OneHot(size=7) for _ in range(1, 24+1)]),
            "hour_of_day": gym.spaces.Tuple([OneHot(size=24) for _ in range(1, 24+1)]),
            "temperature_forecast": Box(-np.inf, np.inf, shape=(24,)),
            "wind_speed_forecast": Box(-np.inf, np.inf, shape=(24,)),
            "cloud_cover_forecast": Box(-np.inf, np.inf, shape=(24,)),
        })
        self.action_space = gym.spaces.Dict({
            # Tariff action:
            "mean_percentual_deviation": Box(-np.inf, np.inf, shape=(1,)),  # mean alpha
            "std_percentual_deviation": Box(-np.inf, np.inf, shape=(1,)),  # std alpha
            "mean_periodic_payment_factor": Box(0., 10., shape=(1,)),  # mean beta
            "std_periodic_payment_factor": Box(-np.inf, np.inf, shape=(1,)),  # std beta
            "state_value": Box(-np.inf, np.inf, shape=(1,)),
            "prob_new_iteration": Box(0.0, 1.0, shape=(1,)),  # skip for now
            # Wholesale action:
            "electricity_amount": Box(-np.inf, np.inf, shape=(24,)),  # negative when we buy?
            "limit_price": Box(-np.inf, np.inf, shape=(24,)),  # negative when we buy?
            "is_market_order": Box(0.0, 1.0, shape=(24,)),
        })

    def step(self, action) -> [object, float, bool, dict]:
        """
        Maps action to (observation: object, reward: flaot, done: bool, info: dict)
        """
        # There might be a mismatch if it already moved to the next timeslot ??
        latest_timeslot = game.latest_timeslot(self.game_id)
        observation = load_env_state(
            self.game_id,
            latest_timeslot=latest_timeslot,
            past_window_size=128
        )
        reward = calculate_reward(observation)
        done = (self.game_id in game.finished_ids())
        info = {
            # Useful information for debugging, but should not be used for training
            "game_id": self.game_id,
            "timeslot": latest_timeslot,
        }
        return observation, reward, done, info

    def reset(self) -> object:
        # TODO : returns initial observation after creating the environment
        # Return some kind of nil observation? same shape as regular observation!
        observation = None
        return observation

    def render(self, mode: str = "console") -> None:
        # TODO
        # e.g. print/represent current observation (how do you usually access the observation from here?)
        pass

    def close(self) -> None:
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