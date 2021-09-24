import numpy as np
import gym
from data.env_state import load_env_state
from data.reward import load_reward
from data import game


class PowerTACEnv(gym.Env):
    """
    PowerTAC environment based on gym interface
    https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/master/5_custom_gym_env.ipynb
    Some inspiration from: ewiis3-broker/ewiis3_python_scripts/blob/master/src/ewiis3_python_scripts/envs/tariff_env.py
    """
    metadata = {'render.modes': ['console']}

    def __init__(self, game_id: str):
        super(PowerTACEnv, self).__init__()
        self.game_id = game_id
        self.latest_observation = None
        # Since gym.spaces.Dict and gym.spaces.Tuple is not yet supported by stable_baselines,
        # I'm defining the observation as a single large Box space.
        # These are the [min, max] values for the observation feature dimensions:
        observation_space_bounds = np.array([
            [0, 5000],  # timeslot (I have arbitrarily decided on a maximum number of 5000 timeslots)
            [-np.inf, np.inf],  # percentual_deviation
            [0, 1],  # day_of_week[0], is_monday
            [0, 1],  # day_of_week[1], is_tuesday
            [0, 1],  # day_of_week[2], is_wednesday
            [0, 1],  # day_of_week[3], is_thursday
            [0, 1],  # day_of_week[4], is_friday
            [0, 1],  # day_of_week[5], is_saturday
            [0, 1],  # day_of_week[6], is_sunday
            [0, 1],  # hour_of_day[0], is_0h
            [0, 1],  # hour_of_day[1], is_1h
            [0, 1],  # hour_of_day[2], is_2h
            [0, 1],  # hour_of_day[3], is_3h
            [0, 1],  # hour_of_day[4], is_4h
            [0, 1],  # hour_of_day[5], is_5h
            [0, 1],  # hour_of_day[6], is_6h
            [0, 1],  # hour_of_day[7], is_7h
            [0, 1],  # hour_of_day[8], is_8h
            [0, 1],  # hour_of_day[9], is_9h
            [0, 1],  # hour_of_day[10], is_10h
            [0, 1],  # hour_of_day[11], is_11h
            [0, 1],  # hour_of_day[12], is_12h
            [0, 1],  # hour_of_day[13], is_13h
            [0, 1],  # hour_of_day[14], is_14h
            [0, 1],  # hour_of_day[15], is_15h
            [0, 1],  # hour_of_day[16], is_16h
            [0, 1],  # hour_of_day[17], is_17h
            [0, 1],  # hour_of_day[18], is_18h
            [0, 1],  # hour_of_day[19], is_19h
            [0, 1],  # hour_of_day[20], is_20h
            [0, 1],  # hour_of_day[21], is_21h
            [0, 1],  # hour_of_day[22], is_22h
            [0, 1],  # hour_of_day[23], is_23h
            [-np.inf, np.inf],  # grid_imbalance_prediction[0]
            [-np.inf, np.inf],  # grid_imbalance_prediction[1]
            [-np.inf, np.inf],  # grid_imbalance_prediction[2]
            [-np.inf, np.inf],  # grid_imbalance_prediction[3]
            [-np.inf, np.inf],  # grid_imbalance_prediction[4]
            [-np.inf, np.inf],  # grid_imbalance_prediction[5]
            [-np.inf, np.inf],  # grid_imbalance_prediction[6]
            [-np.inf, np.inf],  # grid_imbalance_prediction[7]
            [-np.inf, np.inf],  # grid_imbalance_prediction[8]
            [-np.inf, np.inf],  # grid_imbalance_prediction[9]
            [-np.inf, np.inf],  # grid_imbalance_prediction[10]
            [-np.inf, np.inf],  # grid_imbalance_prediction[11]
            [-np.inf, np.inf],  # grid_imbalance_prediction[12]
            [-np.inf, np.inf],  # grid_imbalance_prediction[13]
            [-np.inf, np.inf],  # grid_imbalance_prediction[14]
            [-np.inf, np.inf],  # grid_imbalance_prediction[15]
            [-np.inf, np.inf],  # grid_imbalance_prediction[16]
            [-np.inf, np.inf],  # grid_imbalance_prediction[17]
            [-np.inf, np.inf],  # grid_imbalance_prediction[18]
            [-np.inf, np.inf],  # grid_imbalance_prediction[19]
            [-np.inf, np.inf],  # grid_imbalance_prediction[20]
            [-np.inf, np.inf],  # grid_imbalance_prediction[21]
            [-np.inf, np.inf],  # grid_imbalance_prediction[22]
            [-np.inf, np.inf],  # grid_imbalance_prediction[23]
            [-np.inf, np.inf],  # customer_prosumption_prediction[0]
            [-np.inf, np.inf],  # customer_prosumption_prediction[1]
            [-np.inf, np.inf],  # customer_prosumption_prediction[2]
            [-np.inf, np.inf],  # customer_prosumption_prediction[3]
            [-np.inf, np.inf],  # customer_prosumption_prediction[4]
            [-np.inf, np.inf],  # customer_prosumption_prediction[5]
            [-np.inf, np.inf],  # customer_prosumption_prediction[6]
            [-np.inf, np.inf],  # customer_prosumption_prediction[7]
            [-np.inf, np.inf],  # customer_prosumption_prediction[8]
            [-np.inf, np.inf],  # customer_prosumption_prediction[9]
            [-np.inf, np.inf],  # customer_prosumption_prediction[10]
            [-np.inf, np.inf],  # customer_prosumption_prediction[11]
            [-np.inf, np.inf],  # customer_prosumption_prediction[12]
            [-np.inf, np.inf],  # customer_prosumption_prediction[13]
            [-np.inf, np.inf],  # customer_prosumption_prediction[14]
            [-np.inf, np.inf],  # customer_prosumption_prediction[15]
            [-np.inf, np.inf],  # customer_prosumption_prediction[16]
            [-np.inf, np.inf],  # customer_prosumption_prediction[17]
            [-np.inf, np.inf],  # customer_prosumption_prediction[18]
            [-np.inf, np.inf],  # customer_prosumption_prediction[19]
            [-np.inf, np.inf],  # customer_prosumption_prediction[20]
            [-np.inf, np.inf],  # customer_prosumption_prediction[21]
            [-np.inf, np.inf],  # customer_prosumption_prediction[22]
            [-np.inf, np.inf],  # customer_prosumption_prediction[23]
        ])
        self.observation_space = gym.spaces.Box(
            low=observation_space_bounds[:, 0],
            high=observation_space_bounds[:, 1],
            shape=(observation_space_bounds[0],)
        )
        action_space_bounds = np.array([
            [-np.inf, np.inf],  # mean_percentual_deviation
            [-np.inf, np.inf],  # std_percentual_deviation
            [0, 10],  # mean_periodic_payment_factor
            [-np.inf, np.inf],  # std_periodic_payment_factor
            [-np.inf, np.inf],  # state_value
            [0, 1],  # prob_new_iteration
        ])
        """
            [-np.inf, np.inf],  # wholesale_electricity_amount[0]
            [-np.inf, np.inf],  # wholesale_electricity_amount[1]
            [-np.inf, np.inf],  # wholesale_electricity_amount[2]
            [-np.inf, np.inf],  # wholesale_electricity_amount[3]
            [-np.inf, np.inf],  # wholesale_electricity_amount[4]
            [-np.inf, np.inf],  # wholesale_electricity_amount[5]
            [-np.inf, np.inf],  # wholesale_electricity_amount[6]
            [-np.inf, np.inf],  # wholesale_electricity_amount[7]
            [-np.inf, np.inf],  # wholesale_electricity_amount[8]
            [-np.inf, np.inf],  # wholesale_electricity_amount[9]
            [-np.inf, np.inf],  # wholesale_electricity_amount[10]
            [-np.inf, np.inf],  # wholesale_electricity_amount[11]
            [-np.inf, np.inf],  # wholesale_electricity_amount[12]
            [-np.inf, np.inf],  # wholesale_electricity_amount[13]
            [-np.inf, np.inf],  # wholesale_electricity_amount[14]
            [-np.inf, np.inf],  # wholesale_electricity_amount[15]
            [-np.inf, np.inf],  # wholesale_electricity_amount[16]
            [-np.inf, np.inf],  # wholesale_electricity_amount[17]
            [-np.inf, np.inf],  # wholesale_electricity_amount[18]
            [-np.inf, np.inf],  # wholesale_electricity_amount[19]
            [-np.inf, np.inf],  # wholesale_electricity_amount[20]
            [-np.inf, np.inf],  # wholesale_electricity_amount[21]
            [-np.inf, np.inf],  # wholesale_electricity_amount[22]
            [-np.inf, np.inf],  # wholesale_electricity_amount[23]
            [-np.inf, np.inf],  # wholesale_limit_price[0]
            [-np.inf, np.inf],  # wholesale_limit_price[1]
            [-np.inf, np.inf],  # wholesale_limit_price[2]
            [-np.inf, np.inf],  # wholesale_limit_price[3]
            [-np.inf, np.inf],  # wholesale_limit_price[4]
            [-np.inf, np.inf],  # wholesale_limit_price[5]
            [-np.inf, np.inf],  # wholesale_limit_price[6]
            [-np.inf, np.inf],  # wholesale_limit_price[7]
            [-np.inf, np.inf],  # wholesale_limit_price[8]
            [-np.inf, np.inf],  # wholesale_limit_price[9]
            [-np.inf, np.inf],  # wholesale_limit_price[10]
            [-np.inf, np.inf],  # wholesale_limit_price[11]
            [-np.inf, np.inf],  # wholesale_limit_price[12]
            [-np.inf, np.inf],  # wholesale_limit_price[13]
            [-np.inf, np.inf],  # wholesale_limit_price[14]
            [-np.inf, np.inf],  # wholesale_limit_price[15]
            [-np.inf, np.inf],  # wholesale_limit_price[16]
            [-np.inf, np.inf],  # wholesale_limit_price[17]
            [-np.inf, np.inf],  # wholesale_limit_price[18]
            [-np.inf, np.inf],  # wholesale_limit_price[19]
            [-np.inf, np.inf],  # wholesale_limit_price[20]
            [-np.inf, np.inf],  # wholesale_limit_price[21]
            [-np.inf, np.inf],  # wholesale_limit_price[22]
            [-np.inf, np.inf],  # wholesale_limit_price[23]
            [0, 1],  # is_market_order[0]
            [0, 1],  # is_market_order[1]
            [0, 1],  # is_market_order[2]
            [0, 1],  # is_market_order[3]
            [0, 1],  # is_market_order[4]
            [0, 1],  # is_market_order[5]
            [0, 1],  # is_market_order[6]
            [0, 1],  # is_market_order[7]
            [0, 1],  # is_market_order[8]
            [0, 1],  # is_market_order[9]
            [0, 1],  # is_market_order[10]
            [0, 1],  # is_market_order[11]
            [0, 1],  # is_market_order[12]
            [0, 1],  # is_market_order[13]
            [0, 1],  # is_market_order[14]
            [0, 1],  # is_market_order[15]
            [0, 1],  # is_market_order[16]
            [0, 1],  # is_market_order[17]
            [0, 1],  # is_market_order[18]
            [0, 1],  # is_market_order[19]
            [0, 1],  # is_market_order[20]
            [0, 1],  # is_market_order[21]
            [0, 1],  # is_market_order[22]
            [0, 1],  # is_market_order[23]
        """
        self.action_space = gym.spaces.Box(
            low=action_space_bounds[:, 0],
            high=action_space_bounds[:, 1],
            shape=(action_space_bounds[0],)
        )

    def step(self, action) -> [object, float, bool, dict]:
        """
        Maps action: np.arry to (observation: np.array, reward: float, done: bool, info: dict)
        """
        # There might be a mismatch if it already moved to the next timeslot ??
        timeslot = game.latest_timeslot(self.game_id)
        observation = load_env_state(
            self.game_id,
            latest_timeslot=timeslot,
            past_window_size=128
        )
        reward = self.calculate_reward(timeslot)
        done = (self.game_id in game.finished_ids())
        info = {
            # Useful information for debugging, but should not be used for training
            # e.g. current total cash of all the brokers, or market share, or current wholesale prices
            "game_id": self.game_id,
            "timeslot": timeslot,
            "reward": reward,
            "done": done,
        }
        return observation, reward, done, info

    def reset(self) -> object:
        # TODO : return valid observation
        observation = np.zeros(self.observation_space.shape)
        return observation

    def calculate_reward(self, timeslot: int) -> float:
        reward_dataframe = load_reward(self.game_id, timeslot)

        # TODO : detect if penalize_revoke
        # see QLearner.java, RlLearner.java, TariffAnalysisService.java in current EWIIS3 java broker
        sum_charge = reward_dataframe["sum_charge"]
        '''
        # From python-scripts:
        df_prosumption = db.load_consumption_tariff_prosumption(game_id, 24)
        df_prosumption["grid_prosumption"] = df_prosumption["totalProduction"] - df_prosumption["totalConsumption"]
        # df_earnings = db.load_consumption_tariff_earnings(game_id, 24)
        '''
        return sum_charge

    def render(self, mode: str = "console") -> None:
        pass

    def close(self) -> None:
        # TODO
        pass

