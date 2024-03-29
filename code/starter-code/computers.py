import numpy as np
import time
import sys
import json
import requests

URL_IP = "http://127.0.0.1:"
STARTING_URL = 4999
TIMEOUT_VALUE = 300/1000   # ms


def URL(fc):
    return URL_IP + str(STARTING_URL + fc) + "/"

import api.Computer

# ------------------------------ decide on state ----------------------------- #


def query_acceptable_state(fc, state):

    r = None

    try:
        r = requests.get(url=URL(fc) + str(fc) + "/acceptable_state",
                         params={"state": str(state)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        return False

    if r.text == "True":
        return True
    return False


def deliver_state_others(fc, state):
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/deliver_state",
                         params={"state": str(state)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        pass

# ----------------------------- decide on action ----------------------------- #

def query_acceptable_action(fc, action):

    try:
        r = requests.get(url=URL(fc) + str(fc) + "/acceptable_action",
                         params={"action": str(action)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        return False

    if r.text == "True":
        return True
    return False


def deliver_action_others(fc, action):
    try:
        r = requests.get(url=URL(fc) + str(fc) + "/deliver_action",
                         params={"action": str(action)}, timeout=TIMEOUT_VALUE)
    except Exception as _:
        return False


class FlightComputer:

    def __init__(self, state):
        self.state = state
        self.current_stage_index = 0
        self.peers = []
        self.completed = True
        self.stage_handlers = [
            self._handle_stage_1,
            self._handle_stage_2,
            self._handle_stage_3,
            self._handle_stage_4,
            self._handle_stage_5,
            self._handle_stage_6,
            self._handle_stage_7,
            self._handle_stage_8,
            self._handle_stage_9]
        self.stage_handler = self.stage_handlers[self.current_stage_index]

    def add_peer(self, peer):
        self.peers.append(peer)

    def _handle_stage_1(self):
        action = {"pitch": 90, "throttle": 1.0, "heading": 90,
                  "stage": False, "next_state": False}
        if self.state["altitude"] >= 1000:
            action["pitch"] = 80
            action["next_stage"] = True

        return action

    def _handle_stage_2(self):
        action = {"pitch": 80, "throttle": 1.0, "heading": 90,
                  "stage": False, "next_state": False}
        # Eject SRB's before the gravity turn
        if self.state["fuel_srb"] <= 1250:
            action["stage"] = True
            action["next_stage"] = True

        return action

    def _handle_stage_3(self):
        action = {"pitch": 80, "throttle": 1.0, "heading": 90,
                  "stage": False, "next_state": False}
        # Eject 2nd SRB + Initial Gravity turn
        if self.state["fuel_srb"] <= 10:
            action["stage"] = True
            action["pitch"] = 60.0
            action["next_stage"] = True

        return action

    def _handle_stage_4(self):
        action = {"pitch": 80, "throttle": 1.0, "heading": 90,
                  "stage": False, "next_state": False}
        # Turn
        if self.state["altitude"] >= 25000:
            action["pitch"] = 0
            action["throttle"] = 0.75
            action["next_stage"] = True

        return action

    def _handle_stage_5(self):
        action = {"pitch": 0, "throttle": 0.75, "heading": 90,
                  "stage": False, "next_state": False}
        # Cut throttle when apoapsis is 100km
        if self.state["apoapsis"] >= 100000:
            action["throttle"] = 0.0
            action["next_stage"] = True

        return action

    def _handle_stage_6(self):
        action = {"pitch": 0, "throttle": 0.0, "heading": 90,
                  "stage": False, "next_state": False}
        # Drop stage
        if self.state["altitude"] >= 80000:
            action["stage"] = True
            action["next_stage"] = True

        return action

    def _handle_stage_7(self):
        action = {"pitch": 0, "throttle": 0.0, "heading": 90,
                  "stage": False, "next_state": False}
        # Poor man's circularisation
        if self.state["altitude"] >= 100000:
            action["throttle"] = 1.0
            action["next_stage"] = True

        return action

    def _handle_stage_8(self):
        action = {"pitch": 0, "throttle": 1.0, "heading": 90,
                  "stage": False, "next_state": False}
        if self.state["periapsis"] >= 90000:
            action["throttle"] = 0.0
            action["next_stage"] = True

        return action

    def _handle_stage_9(self):
        self.completed = True

    def sample_next_action(self):
        return self.stage_handler()

    def decide_on_state(self, state):
        acceptations = [query_acceptable_state(p, state) for p in self.peers]
        decided = (sum(acceptations) + 1) / (len(self.peers)+1) > 0.5

        if decided:
            for p in self.peers:
                deliver_state_others(p, state)
            self.deliver_state(state)

        return decided

    def decide_on_action(self, action):
        acceptations = [query_acceptable_action(p, action) for p in self.peers]
        decided = (sum(acceptations) + 1) / (len(self.peers) + 1) > 0.5

        if decided:
            for p in self.peers:
                deliver_action_others(p, action)
            self.deliver_action(action)

        return decided

    # make that the leader does not modify the state
    def acceptable_state(self, state):
        return True

    def acceptable_action(self, action):
        our_action = self.sample_next_action()

        accept = True
        for k in our_action.keys():
            if our_action[k] != action[k]:
                accept = False

        return accept

    def deliver_action(self, action):
        if "next_stage" in action and action["next_stage"]:
            self.current_stage_index += 1
            self.stage_handler = self.stage_handlers[self.current_stage_index]

    def deliver_state(self, state):
        self.state = state


class FullThrottleFlightComputer(FlightComputer):

    def __init__(self, state):
        super(FullThrottleFlightComputer, self).__init__(state)

    def sample_next_action(self):
        action = super(FullThrottleFlightComputer, self).sample_next_action()
        action["throttle"] = 1.0

        return action


class RandomThrottleFlightComputer(FlightComputer):

    def __init__(self, state):
        super(RandomThrottleFlightComputer, self).__init__(state)

    def sample_next_action(self):
        action = super(RandomThrottleFlightComputer, self).sample_next_action()
        action["throttle"] = np.random.uniform()

        return action


class SlowFlightComputer(FlightComputer):

    def __init__(self, state):
        super(SlowFlightComputer, self).__init__(state)

    def sample_next_action(self):
        action = super(SlowFlightComputer, self).sample_next_action()
        time.sleep(np.random.uniform() * 10) # Seconds

        return action


class CrashingFlightComputer(FlightComputer):

    def __init__(self, state):
        super(CrashingFlightComputer, self).__init__(state)

    def sample_next_action(self):
        action = super(CrashingFlightComputer, self).sample_next_action()
        # 1% probability of a crash
        if np.random.uniform() <= 0.01:
            raise Exception("Flight computer crashed")

        return action



def allocate_random_flight_computer(state):
    computers = [
        FullThrottleFlightComputer,
        RandomThrottleFlightComputer,
        SlowFlightComputer,
        CrashingFlightComputer,
    ]

    return computers[np.random.randint(0, len(computers))](state)