# entry point to train and test broker
# Based on predict_action.py but it's synchronous and specifically designed to train an agent.
import dotenv
from data import game
from util import execution
from models.powertac_env import PowerTACEnv
from stable_baselines import A2C


# load config
dotenv.load_dotenv(dotenv.find_dotenv())


# TODO : load agent weights
# agent = A2C.load("a2c-powertac-v0_1", policy="MlpPolicy")
game_id = game.running_ids()[0]  # assuming there's just one at a time & assuming it's already running !!
print(f"GAME {game_id}")
env = PowerTACEnv(game_id)
agent = A2C("MlpPolicy", env, verbose=1)  # use CustomPolicy? look at hyperparameters!
# TODO : wait for bootstrapping to be finished ??
agent.learn(total_timesteps=2000)
agent.save("a2c-powertac-v0_1")
