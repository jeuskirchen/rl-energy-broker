# entry point to train and test broker
import dotenv
from data import game
from util import execution
from models.agent import Agent
from time import sleep
from data.action import store_tuple, tuple_exists  # load_action
from models.powertac_env import PowerTACEnv


# load config
dotenv.load_dotenv(dotenv.find_dotenv())


# initialize global vars
MODE = "train"  # ["train", "test", "inference"]
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
        agents[game_id] = Agent(game_id)
    # action, value = agents[game_id].get_action_and_value(latest_observation[game_id])
    action = envs[game_id].action_space.sample()
    value = 0.0
    print(action, value)
    observation, reward, done, _ = envs[game_id].step(action)
    store_tuple(game_id, latest_timeslot, latest_observation[game_id], action, reward, observation)
    latest_observation[game_id] = observation
    envs[game_id].render(mode="console")
    # Where/how to use action/observation/reward for training the agent?
    # Can I see when a game is finished? If so, close that environment.
    #
    #
    #
    if done:
        envs[game_id].close()


while True:
    print(f"RUNNING GAMES {game.running_ids()}")
    for game_id in game.running_ids():
        # TODO : add wait group and check for termination condition(s)
        # FIXME : There might be a mismatch between 1 step on the server and 1 step in gym environment. How to sync?
        timeslot = game.latest_timeslot(game_id)
        if not tuple_exists(game_id, timeslot):
            # TODO : wait for predictions before taking the action?
            execution.run_async(take_action, game_id, timeslot)
    sleep(1)
