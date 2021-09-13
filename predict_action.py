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
    # action, value = agents[game_id].get_action_and_value(latest_observation[game_id])
    action = envs[game_id].action_space.sample()
    value = 0.0
    print(action, value)
    observation, reward, done, info = envs[game_id].step(action)
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


# TODO : how to reconcile this asynchronous loop with the stable_baselines 'learn' method?
# TODO : how to not train N separate, independent agents, but a single agent via multiple instances?
#  e.g. one at a time. This way, I don't have to deal with coordination between agents, like sharing gradients...
#  The resulting agent can be used as a pre-trained agent but then continue training online during actual games?
#  In any case, I would have to reconcile the async loop with the 'learn' method.
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
            # TODO : wait for predictions before taking the action? -> make sure that predictions exist
            #  I could also do this in the load_env_state method in env_state.py
            # TODO : is the stable_baselines agent doing epsilon-greedy exploration by default?
            execution.run_async(take_action, game_id, timeslot)
    sleep(1)
