import numpy as np
import time
from flask import Flask, request
import sys
import json
import requests
from computers import *



def convert_string_dict(string):
    acceptable_string = string.replace("'", "\"")
    
    return json.loads(acceptable_string)


# python3 computers.py 1 // it means this is the computer 1
if len(sys.argv) <= 1:
    print("You should give a computer number as argument")
    exit(1)
app = Flask(__name__)

myId = sys.argv[1]
myComputer = None


""" Url from 5000 for the first computer to 4999 + n for the nth"""

URL = "http://127.0.0.1:" + str(4999 + int(myId)) + "/"



# ------------------------------ init computers ------------------------------ #

@app.route("/" + str(myId) + "/initComputer")
def initComputer():
    global myComputer

    state = request.args.get('state')
    state = convert_string_dict(state)

    myComputer = FlightComputer(state)
    return "Ok"


@app.route('/' + myId + '/add_peer')
def app_peer():
    global myComputer
    myComputer.add_peer(int(request.args.get('peer')))
    return "Ok"



# ------------------------------ decide on state ----------------------------- #


@app.route("/" + str(myId) + "/decide_on_state")
def decide_on_state():

    state = request.args.get('state')
    state = convert_string_dict(state)
    decided = myComputer.decide_on_state(state)


    return str(decided)


@app.route("/" + str(myId) + "/acceptable_state")
def acceptable_state():
    state = request.args.get('state')
    state = convert_string_dict(state)
    return str(myComputer.acceptable_state(state))

@app.route("/" + str(myId) + "/deliver_state")
def deliver_state_myself():

    state = request.args.get('state')
    state = convert_string_dict(state)

    myComputer.deliver_state(state)

    return 'ok'



# ----------------------------- decide on action ----------------------------- #

@app.route("/" + str(myId) + "/decide_on_action")
def decide_on_action():
    action = request.args.get('action')
    action = convert_string_dict(action)
    decided = myComputer.decide_on_action(action)
    # print("HEHEHEH")
    # print(decided)
    # exit()
    return str(decided)

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
    
    


@app.route("/" + str(myId) + "/acceptable_action")
def acceptable_action():
    action = request.args.get('action')
    action = convert_string_dict(action)
    convert_0_bool(action)

    answer = myComputer.acceptable_action(action)
    # print('acceptable answer')
    # print(answer)

    return str(answer)

# ----------------------------- sample on action ----------------------------- #

@app.route("/" + str(myId) + "/sample_next_action")
def sample_action():
    if myComputer.sample_next_action() == None:
        return None
    return str(myComputer.sample_next_action())


@app.route("/" + str(myId) + "/deliver_action")
def deliver_action_myself():
    # print("I am delivering")
    action = request.args.get('action')
    # print("I still deliver")
    action = convert_string_dict(action)
    # print("I am still deliver")

    myComputer.deliver_action(action)
    # time.sleep(20)
    return 'ok'






# myId starts at 1.
app.run(port=4999+int(myId))
