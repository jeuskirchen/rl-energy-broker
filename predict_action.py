# entry point to test broker
import numpy as np
import dotenv
from data import game
from util import execution
from models.agent import Agent
from time import sleep
from data.prediction import load_predictions, store_predictions, prediction_exists
import gym


# load config
dotenv.load_dotenv(dotenv.find_dotenv())

# initialize global vars
agent = Agent()
should_run = True
mode = "training" # "inference"


def take_action(game_id: str, timeslot: int) -> None:

    print(f"take_action(game_id={game_id}, timeslot={timeslot})")
    # df_agent_outputs: (mean_alpha, std_alpha, mean_beta, std_beta, value, prob_next_iteration)
    if mode == "training":
        # During training time, randomly sample an action (alpha and beta) using the means and standard deviations
        sampled_alpha = np.random.normal(mean_alpha, std_alpha) # percentual deviation of EWIIS3 MUBP from active conzmption tariff
        sampled_beta = np.random.normal(mean_beta, std_beta) # (continuous) periodic payment factor
        action = np.array([sampled_alpha, sampled_beta])
    elif mode == "inference":
        # During inference time, take the means rather than randomly sampling from the distributions
        action = np.array([mean_alpha, mean_beta])
    store_predictions(df_agent_outputs, "agent_outputs")

    obs, reward, done, info = env.step(action)

    # keep track of reward? etc.
    #
    #
    #


envs = {} # dictionary of environments; each game has its own environment

while True:
    print(f"RUNNING GAMES {game.running_ids()}")
    for game_id in game.running_ids():
        if game_id not in envs.keys():
            envs[game_id] = ???
            envs[game_id].reset()
        # TODO : add wait group and check for termination condition(s)
        timeslot = game.latest_timeslot(game_id)
        df_agent_outputs = agent.get_outputs()
        store_predictions(df_agent_outputs, "agent_outputs")

        if not agent_outputs_exist(game_id, timeslot, "agent_outputs"):
            execution.run_async(take_action, game_id, timeslot)
    sleep(1)

for env in envs.values():
    env.close()
