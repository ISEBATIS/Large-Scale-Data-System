import requests
import json
import time
import random as rand

URL_IP = "http://127.0.0.1:"
STARTING_URL = 4999
TIMEOUT_VALUE = 1 # 1 ms

def URL(fc):
    return URL_IP + str(STARTING_URL + fc) + "/"


def convert_string_dict(string):
    acceptable_string = string.replace("'", "\"")
    s = json.loads(acceptable_string)


# ------------------------------ init computers ------------------------------ #

# typeComputer is a string either: 'random' if the computer is a random one or 'normal' if the computer is normal
def init_computer(state, currentId, typeComputer):
    
    r = requests.get(url=URL(currentId) + str(currentId) +
                     str("/initComputer"), params={'state': str(state),
                                                   'type': str(typeComputer)})
    return currentId


def add_peer(fc, peer):

    r = requests.get(url=URL(fc) + str(fc) + "/add_peer",
                     params={"peer": str(peer)})


# ------------------------------ decide on state ----------------------------- #

def decide_on_state(state, number_computers):
    r = None 
    # select a fligh computer randomly
    fc = rand.randint(1, number_computers)
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_state",
                     params={"state": str(state)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        pass

    if r is not None and  r.text == "True":
        return True
    return False


# ---------------------------- sample_next_action ---------------------------- #

def sample_next_action(number_computers):

    r = None
    # select a fligh computer randomly
    fc = rand.randint(1, number_computers)
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/sample_next_action", timeout=TIMEOUT_VALUE)
    except Exception as _:
        pass

    if r is None or r.text == '0':
        return 0 # the computer just did not answered

    if r.text == "None":
        return None
        
    # make it a dictionnary
    result = r.text
    result = result.replace("'", "\"")
    # Since False = 0 its ok
    result = result.replace("False", "0")
    result = result.replace("True", "1")

    result = json.loads(result)

    return result


# ----------------------------- decide_on_action ----------------------------- #

def decide_on_action(action, number_computers):
    # The consensus did not converged at this timestep
    if action == 0:
        return False
    r = None
    fc = rand.randint(1, number_computers)
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_action",
                     params={"action": str(action)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        pass

    if r == None:
        return False 

    if r.text == "True":
        return True
    return False






