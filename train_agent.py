# entry point to train and test broker
# Based on predict_action.py but it's synchronous and specifically designed to train an agent.
import dotenv
from data import game
from util import execution
from time import sleep
from data.rl_tuple import store_tuple  # tuple_exists, load_action
from models.powertac_env import PowerTACEnv
from stable_baselines import A2C


# load config
dotenv.load_dotenv(dotenv.find_dotenv())


# TODO : how to reconcile this asynchronous loop with the stable_baselines 'learn' method?
# TODO : how to not train N separate, independent agents, but a single agent via multiple instances?
#  e.g. one at a time. This way, I don't have to deal with coordination between agents, like sharing gradients...

game_id = game.running_ids()[0]  # assuming there's just one
env = PowerTACEnv(game_id)
latest_observation = env.reset()
agent = A2C("MlpPolicy", env, verbose=1)
action_exists = []
done = False

while True:
    print(f"GAME {game_id}")
    # FIXME : There might be a mismatch between 1 step on the server and 1 step in gym environment. How to sync?
    # TODO: do with prediction_exists method instead of appending to list and checking the list
    timeslot = game.latest_timeslot(game_id)
    if (game_id, timeslot) not in action_exists:
        action_exists.append((game_id, timeslot))
        # TODO : wait for predictions before taking the action? -> make sure that predictions exist
        #  I could also do this in the load_env_state method in env_state.py
        # TODO : is the stable_baselines agent doing epsilon-greedy exploration by default?
        # Note: latest_timeslot is loaded again inside of the step method because I can't pass it from here
        action = env.action_space.sample()  # FIXME : get action from agent? custom policy needed?
        value = 0.0
        print(action, value)
        observation, reward, done, info = env.step(action)
        store_tuple(game_id, timeslot, latest_observation, action, reward, observation)
        latest_observation = observation
        env.render(mode="console")
        # Where/how to use action/observation/reward for training the agent?
        # Can I see when a game is finished? If so, close that environment.
        #
        #
        #
    sleep(1)
    if done:
        env.close()
        break
