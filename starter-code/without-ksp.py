import argparse
import math
import pickle
import numpy as np
import time
import requests
from apiLauncher import *
from computers import *
import json




# Load the pickle files
actions = pickle.load(open("data/actions.pickle", "rb"))
states = pickle.load(open("data/states.pickle", "rb"))
timestep = 0
currentId = 0
currentEpoch = 0

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--correct-fraction", type=float, default=1.0,
                    help="Fraction of correct flight computers (default 1.0).")
parser.add_argument("--flight-computers", type=int, default=2,
                    help="Number of flight computers (default: 1).")
arguments, _ = parser.parse_known_args()



def readout_state():
    return states[timestep]


def convert_0_bool(action):
    if action['stage'] == 0:
        action['stage'] = False
    else :
        action['stage'] = True
    
    if action['next_state'] == 0:
        action['next_state'] = False
    else :
        action['next_state'] = True
    
    # print(action)

def execute_action(action):
    convert_0_bool(action)
    print(action)
    print(actions[timestep])
    for k in action.keys():
        assert(action[k] == actions[timestep][k])


def allocate_flight_computers(arguments):
    global currentId

    flight_computers = []
    n_fc = arguments.flight_computers  # number flight computers
    n_correct_fc = math.ceil(arguments.correct_fraction * n_fc)
    n_incorrect_fc = n_fc - n_correct_fc
    state = readout_state()
    for _ in range(n_correct_fc):
        currentId += 1
        flight_computers.append(init_computer(state, currentId))

    # for _ in range(n_incorrect_fc):
            # currentId += 1
    #     flight_computers.append(allocate_random_flight_computer(state)) # TODO: Make for random_flight
    # Add the peers for the consensus protocol
    for fc in flight_computers:
        for peer in flight_computers:
            if fc != peer:
              add_peer(fc ,peer)

    return flight_computers


# Connect with Kerbal Space Program
flight_computers = allocate_flight_computers(arguments)


def select_leader():
    global currentEpoch

    leader_index = currentEpoch

    currentEpoch += 1

    if currentEpoch == len(flight_computers):
        currentEpoch = 0

    # leader_index = np.random.randint(0, len(flight_computers))

    return flight_computers[leader_index]


def next_action(state):
    leader = select_leader()
    state_decided = decide_on_state(leader, state)  # asks leader's state ?
    # print(state_decided)
    if not state_decided:
        return None
    action = sample_next_action(leader)
    action_decided = decide_on_action(leader, action)
    # exit()
    if action_decided:
        return action

    return None


complete = False
try:
    while not complete:
        timestep += 1
        state = readout_state()
        leader = select_leader()
        print(leader)
        state_decided = decide_on_state(leader, state)
        if not state_decided:
            # print("N'importe quoi")
            continue
        action = sample_next_action(leader)
        if action is None:
            complete = True
            continue

        if decide_on_action(leader, action):
            execute_action(action)
        else:
            timestep -= 1

except Exception as e:
    print(e)

if complete:
    print("Success!")
else:
    print("Fail!")
