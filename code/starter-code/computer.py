# --------------------------------- computer --------------------------------- #
# ------------------------------------- - ------------------------------------ #
# @author: Sebati Ilias 
# @author: Gomez  Herrera  Maria  Andrea  Liliana
# ------------------------------------- - ------------------------------------ #
# Description: This file is a server that using the REST api flask. 
#  It reprensets a computer which represent a flighcomputer. 
# ------------------------------------- - ------------------------------------ #
# ------------------------------------- - ------------------------------------ #

import numpy as np
import time
from flask import Flask, request
import sys
import json
import requests
from computers import *
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


def handler_signal(signum, frame):

    if myComputer == None:
        Computer.set_timer(rand.randint(100, 300))
        print("Computer has not started yet")
        return


    # the interrupt was trigerred to send heartbeat
    if myComputer.trusted_leader ==  myComputer.myComputerNumber:
        myComputer.start_sending_heartbeat()
        return

    myComputer.begin_new_election()


# init the signal handler
signal.signal(signal.SIGALRM, handler_signal)


# ------------------------------ init computers ------------------------------ #

@app.route("/" + str(myId) + "/initComputer")
def initComputer():
    global myComputer

    print("I init return")


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
    return "Ok"


@app.route('/' + myId + '/add_peer')
def add_peer():
    myComputer.flighComputer.add_peer(int(request.args.get('peer')))
    return "Ok"

# ------------------------------ leader election ----------------------------- #
@app.route('/' + myId + '/vote_request')
def vote_request():

    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))

    with lock:
        if myComputer.term < term:
            # We update reset the timeout
            myComputer.set_timeout_leader()
            myComputer.term = term
            myComputer.send_vote(fc)
                
            return "1"

        myComputer.send_not_vote(fc)
    return "1"


# Someone voted for me
@app.route('/' + myId + '/vote')
def vote():

    with lock:    
        # I no longer want to be leader
        if myComputer.state == State.follower:
            return "1"

        myComputer.receive_vote()
    return "1"

# Someone voted against me
@app.route('/' + myId + '/not_vote')
def not_vote():

    term = int(request.args.get('term'))
    with lock:
        # I no longer want to be leader
        if myComputer.state == State.follower:
            return "1"

        myComputer.refuse_vote(term)

    return "1"


@app.route('/' + myId + '/new_leader')
def new_leader():
    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))

    with lock:
        # He can be leader
        if myComputer.term <= term:
            myComputer.new_leader(term, fc)

    return "1"


@app.route('/' + myId + '/heartbeat')
def heartbeat():

    print('heartbeat')
    term = int(request.args.get('term'))
    fc = int(request.args.get("fc"))
    if fc == myComputer.trusted_leader:
        myComputer.received_heartbeat(term, fc)
    elif term > myComputer.term:
        myComputer.new_leader(term, fc)
    else:
        myComputer.begin_new_election()

    return "1"

# ------------------------------ decide on state ----------------------------- #


@app.route("/" + str(myId) + "/decide_on_state")
def decide_on_state():

    state = request.args.get('state')
    # I am the leader
    if myComputer.trusted_leader == myComputer.myComputerNumber:
        state = convert_string_dict(state)

        decided = myComputer.flighComputer.decide_on_state(state)
        return str(decided)
    
    # I am not the leader
    r = None
    # ask the leader about this
    fc = myComputer.trusted_leader
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_state",
                     params={"state": state}, timeout=TIMEOUT_VALUE*2)
    except Exception:
        # We start a new election trying to be leader
        myComputer.stop_timeout()
        myComputer.begin_new_election()
        
    if r is not None and  r.text == "True":
        return "True"
    return "False"


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

    # I am the leader
    if myComputer.trusted_leader == myComputer.myComputerNumber:
        action = convert_string_dict(action)
        decided = None
        try:
            decided = myComputer.flighComputer.decide_on_action(action)
        except  Exception:
            return 'False'
        
        
        return str(decided)
    
    # I am not the leader
    r = None
    # ask the leader about this
    fc = myComputer.trusted_leader
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/decide_on_action",
                     params={"action": action}, timeout=TIMEOUT_VALUE*2)
    except Exception:
        
        # We start a new election trying to be leader
        myComputer.stop_timeout()
        myComputer.begin_new_election()
        
    if r is not None and  r.text == "True":
        return "True"
    return "False"


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
    answer = None
    try:
        answer = myComputer.flighComputer.acceptable_action(action)
    except Exception:
        time.sleep(2)

    return str(answer)

# ----------------------------- sample on action ----------------------------- #


@app.route("/" + str(myId) + "/sample_next_action")
def sample_action():

    # I am leader 
    if myComputer.trusted_leader == myComputer.myComputerNumber:
        next_action =  None
        try:
            next_action = myComputer.flighComputer.sample_next_action()
        except Exception:
            return '0'


        if next_action == None:
            return 'None'

        return str(next_action)

    # ask the leader
    r = None

    fc = myComputer.trusted_leader
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/sample_next_action", timeout=TIMEOUT_VALUE*2)
    except Exception:
        # We start a new election trying to be leader
        myComputer.stop_timeout()
        myComputer.begin_new_election()

        return '0'


    if r is None:
        return '0'

    if r.text == "None":
        return "None"

    return r.text



@app.route("/" + str(myId) + "/deliver_action")
def deliver_action_myself():

    action = request.args.get('action')
    action = convert_string_dict(action)

    myComputer.flighComputer.deliver_action(action)

    return 'ok'


# myId starts at 1.
if __name__ == "__main__":
    app.run(port=4999+int(myId), debug=False)
