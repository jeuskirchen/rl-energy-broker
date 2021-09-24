# entry point to train and test broker
import dotenv
from data import game
from util import execution
from time import sleep
from data.rl_tuple import store_tuple  # tuple_exists, load_action
from models.powertac_env import PowerTACEnv
from stable_baselines import A2C


# load config
dotenv.load_dotenv(dotenv.find_dotenv())

# initialize global vars
should_run = True
# Dictionary of environments and agents:
# Each game (specified by its game_id) has its own environment instance and agent instance
# For each game, I also store the latest observation (could be done differently in the future)
envs = {}
agents = {}
latest_observation = {}


def take_action(_game_id: str, latest_timeslot: int) -> None:
    print(f"take_action(_game_id={_game_id}, latest_timeslot={latest_timeslot})")
    # Note: latest_timeslot is loaded again inside of the step method because I can't pass it from here
    if game_id not in envs.keys():
        # If we haven't seen the game before, create a new gym environment for it:
        envs[game_id] = PowerTACEnv(game_id)
        latest_observation[game_id] = envs[game_id].reset()  # returns initial observation after creating the environment
        agents[game_id] = A2C("MlpPolicy", envs[game_id], verbose=1)
    action = agents[game_id].get_action_and_value(latest_observation[game_id])  # output includes state value
    observation, reward, done, info = envs[game_id].step(action)
    store_tuple(game_id, latest_timeslot, latest_observation[game_id], action, reward, observation)
    latest_observation[game_id] = observation
    envs[game_id].render(mode="console")
    if done:
        envs[game_id].close()


action_exists = []
while True:
    print(f"RUNNING GAMES {game.running_ids()}")
    for game_id in game.running_ids():
        # TODO : add wait group and check for termination condition(s)
        # FIXME : There might be a mismatch between 1 step on the server and 1 step in gym environment. How to sync?
        # TODO: do with prediction_exists method instead of appending to list and checking the list
        timeslot = game.latest_timeslot(game_id)
        if (game_id, timeslot) not in action_exists:
            action_exists.append((game_id, timeslot))
            execution.run_async(take_action, game_id, timeslot)
    sleep(1)
