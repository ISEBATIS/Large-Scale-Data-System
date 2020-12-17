import requests
import json
import time
URL_IP = "http://127.0.0.1:"
STARTING_URL = 4999


def URL(fc):
    return URL_IP + str(STARTING_URL + fc) + "/" 

def convert_string_dict(string):
    # print(string)
    acceptable_string = string.replace("'", "\"")
    # print(acceptable_string)
    s = json.loads(acceptable_string)
    # print(s)


# ------------------------------ init computers ------------------------------ #


def init_computer(state, currentId):
    r = requests.get(url=URL(currentId) + str(currentId) +
                     str("/initComputer"), params={'state': str(state)})

    return currentId


def add_peer(fc, peer):

    r = requests.get(url=URL(fc) + str(fc) + "/add_peer", params={"peer": str(peer)})


# ------------------------------ decide on state ----------------------------- #

def decide_on_state(fc, state):

    r = requests.get(url=URL(fc) + str(fc) + "/decide_on_state",
                     params={"state": str(state)})

    if r.text == "True":
        return True
    return False


# ---------------------------- sample_next_action ---------------------------- #

def sample_next_action(fc):

    r = requests.get(url=URL(fc) + str(fc) + "/sample_next_action")
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
    r = requests.get(url=URL(fc) + str(fc) + "/decide_on_action",
                     params={"action": str(action)})
                     
    if r.text == "True":
        return True
    return False
