import requests
import json
import time
URL_IP = "http://127.0.0.1:"
STARTING_URL = 4999
TIMEOUT_VALUE = 300 / 1000 # 300 ms

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

def decide_on_state(fc, state):
    r = None
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_state",
                     params={"state": str(state)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        print("Computer "  + str(fc) + ' did not replied')


    if r is not None and  r.text == "True":
        return True
    return False


# ---------------------------- sample_next_action ---------------------------- #

def sample_next_action(fc):

    r = None

    try:
        r = requests.get(url=URL(fc) + str(fc) + "/sample_next_action", timeout=TIMEOUT_VALUE)
    except Exception as _:
        print("Computer "  + str(fc) + ' did not replied')

    if r is None:
        return None

    if r.text == "None":
        return None
    result = r.text
    result = result.replace("'", "\"")
    # Since False = 0 its ok
    result = result.replace("False", "0")
    result = result.replace("True", "1")

    result = json.loads(result)

    return result


# ----------------------------- decide_on_action ----------------------------- #

def decide_on_action(fc, action):
    r = None
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_action",
                     params={"action": str(action)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        print("Computer "  + str(fc) + ' did not replied')

    if r == None:
        return False 

    if r.text == "True":
        return True
    return False



# ask the leader of 'fc' fligh computer
def ask_leader(fc):
    r = None
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/who_is_leader", timeout=TIMEOUT_VALUE)
    except Exception as _:
        print("Computer "  + str(fc) + ' did not replied')
    
    if r == None:
        return -1
    
    return int(r.text)



# --------------------------- ask who is the leader -------------------------- #
def select_leader(number_computers):
    #  votedFor[i] = k if the computer i+1 is trusted to be the leader by k computers
    votedFor = [0] * number_computers
    
    for fc in range(1, number_computers + 1):
        trusted_leader = ask_leader(fc)
        if trusted_leader == -1:
            continue
        
        votedFor[trusted_leader-1] += 1
    

    for fc, votes in enumerate(votedFor):
        # If we have a strict majority then votes is the leader
        if votes >= floor(number_computers / 2) + 1:
            return fc + 1
    
    return 1







