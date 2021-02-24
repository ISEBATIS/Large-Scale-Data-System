import numpy as np
import time
from flask import Flask, request
import sys
import json
import requests
from computers import *

import api.leader_election
import api.ComputerApi
from api.Computer import *

# * disable th next 3 lines to have the code to be print in the terminal of the server (GET ...)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


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


# ------------------------------ init computers ------------------------------ #

@app.route("/" + str(myId) + "/initComputer")
def initComputer():
    global myComputer

    state = request.args.get('state')
    state = convert_string_dict(state)
    typeComputer = request.args.get('type')

    flightComputer = None
    if typeComputer == 'random':
        flightComputer = allocate_random_flight_computer(state)
    else:
        flightComputer = FlightComputer(state)

    # I create the computer that will manage the consensus
    myComputer = Computer(flightComputer, myId)
    myComputer.init_signal()
    print(myComputer)
    exit()
    return "Ok"


@app.route('/' + myId + '/add_peer')
def add_peer():
    global myComputer
    myComputer.flighComputer.add_peer(int(request.args.get('peer')))
    return "Ok"

# ------------------------------ leader election ----------------------------- #
@app.route('/' + myId + '/vote_request')
def vote_request():

    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))

    if myComputer.term < term:
        # We update reset the timeout
        myComputer.set_timeout_leader()
        myComputer.term = term
        myComputer.send_vote(fc)
        return

    myComputer.send_not_vote(fc)


# Someone voted for me
@app.route('/' + myId + '/vote')
def vote():
    # I no longer want to be leader
    if myComputer.state == State.follower:
        return

    myComputer.receive_vote()

# Someone voted against me
@app.route('/' + myId + '/not_vote')
def not_vote():
    # I no longer want to be leader
    if myComputer.state == State.follower:
        return

    myComputer.refuse_vote()


@app.route('/' + myId + '/new_leader')
def new_leader():
    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))

    # He can be leader
    if myComputer.term <= term:
        myComputer.new_leader(term, fc)


@app.route('/' + myId + '/heartbeat')
def heartbeat():
    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))

    if fc == myComputer.trusted_leader or term > myComputer.term:
        myComputer.received_heartbeat(term, fc)


# ------------------------------ decide on state ----------------------------- #


@app.route("/" + str(myId) + "/decide_on_state")
def decide_on_state():

    state = request.args.get('state')
    state = convert_string_dict(state)
    decided = myComputer.flighComputer.decide_on_state(state)

    return str(decided)


@app.route("/" + str(myId) + "/acceptable_state")
def acceptable_state():
    state = request.args.get('state')
    state = convert_string_dict(state)
    return str(myComputer.flighComputer.acceptable_state(state))


@app.route("/" + str(myId) + "/deliver_state")
def deliver_state_myself():

    state = request.args.get('state')
    state = convert_string_dict(state)

    myComputer.flighComputer.deliver_state(state)

    return 'ok'


# ----------------------------- decide on action ----------------------------- #

@app.route("/" + str(myId) + "/decide_on_action")
def decide_on_action():
    action = request.args.get('action')
    action = convert_string_dict(action)
    decided = myComputer.flighComputer.decide_on_action(action)

    return str(decided)


def convert_0_bool(action):
    if action['stage'] == 0:
        action['stage'] = False
    else:
        action['stage'] = True

    if action['next_state'] == 0:
        action['next_state'] = False
    else:
        action['next_state'] = True


@app.route("/" + str(myId) + "/acceptable_action")
def acceptable_action():
    action = request.args.get('action')
    action = convert_string_dict(action)
    convert_0_bool(action)

    answer = myComputer.flighComputer.acceptable_action(action)

    return str(answer)

# ----------------------------- sample on action ----------------------------- #


@app.route("/" + str(myId) + "/sample_next_action")
def sample_action():
    if myComputer.flighComputer.sample_next_action() == None:
        return 'None'
    return str(myComputer.flighComputer.sample_next_action())


@app.route("/" + str(myId) + "/deliver_action")
def deliver_action_myself():
    action = request.args.get('action')
    action = convert_string_dict(action)

    myComputer.flighComputer.deliver_action(action)

    return 'ok'


# ------------------------------ respond to client ----------------------------- #
@app.route("/" + str(myId) + "/who_is_leader")
def my_leader():
    return myComputer.trusted_leader

# myId starts at 1.
app.run(port=4999+int(myId), debug=False)
print("Voiture")
