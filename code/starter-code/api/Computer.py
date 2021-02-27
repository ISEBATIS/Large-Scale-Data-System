import api.ComputerApi
from math import floor
import random as rand
from enum import Enum
import requests
import signal
import threading


MINIMAL_TIMEOUT = 0.0001  # used to not wait the response of the server


URL_IP = "http://127.0.0.1:"
STARTING_URL = 4999  # More the starting port
TIMEOUT_VALUE = 300/1000   # ms

# Lock for not beginning a new election while i got a message
lock = threading.Lock()


def URL(fc):
    return URL_IP + str(STARTING_URL + fc) + "/"


class State(Enum):
    leader = 2
    candidate = 1
    follower = 0


# Computer = Node
class Computer:
    def __init__(self, flighComputer, myComputerNumber):
        self.flighComputer = flighComputer
        self.myComputerNumber = myComputerNumber    # can see it as IP address
        # state can be follower, candidate, or leader
        self.state = State.follower
        # similar to the period in raft
        self.term = 0
        # used for the leader election
        # number of computers that voted for me
        self.votes_for_me = 0
        self.votes_against_me = 0

        self.trusted_leader = None

        # set timeout leader
        Computer.set_timeout_leader()


    def begin_new_election(self):
        
        with lock:
            # become a candidate and try to be leader
            self.state = State.candidate

            self.term += 1

            # init the vote counter
            self.votes_against_me = 0
            self.votes_for_me = 1
            # Vote for myself
            # self.receive_vote()

            # time to broadcast the messages
            Computer.set_timer(300)

            # ask cluster' s votes
            self.broadcast_vote_request()

    # We received a vote for us
    def receive_vote(self):
        self.votes_for_me += 1

        # I have a strict majority
        if self.votes_for_me >= floor((len(self.flighComputer.peers) + 1) / 2) + 1:
            print("I won " + str(self.term))
            self.i_won_election()

        # reset the timeout
        Computer.set_timeout_leader()

    # A server gave the vote to someone else
    def refuse_vote(self, term):
        self.votes_against_me += 1

        # Update my term if i was late
        if term > self.term:
            self.term == term

        # I lose the election
        if self.votes_against_me >= floor((len(self.flighComputer.peers) + 1) / 2) + 1:
            self.state = State.follower

        # reset the timeout
        Computer.set_timeout_leader()

    @staticmethod
    def set_timeout_leader():
        # First find the duration randomly of the timeout
        duration = rand.randint(200, 500)  # in ms
        # based on the number of election exp() number of election that we lost

        Computer.set_timer(duration)

    # set a timer in the duration. The duration is in ms
    @staticmethod
    def set_timer(duration):
        signal.setitimer(signal.ITIMER_REAL, duration/1000, 0)
    
    @staticmethod
    def set_timeout_heartbeat():
        signal.setitimer(signal.ITIMER_REAL, 50/1000, 0)


    # self won the elections
    def i_won_election(self):

        self.state = State.leader
        self.start_sending_ack()
        self.start_sending_heartbeat()

        self.trusted_leader = self.myComputerNumber

        # stop the timeout
        self.stop_timeout()

    def broadcast_vote_request(self):
        for fc in self.flighComputer.peers:
            # ask them their vote
            self.query_vote_request(fc)

    def query_vote_request(self, fc):
        # send a request for vote to a given computer
        try:
            requests.get(url=URL(fc) + str(fc) + "/vote_request",
                         params={"term": str(self.term),
                                 "fc": str(
                             self.myComputerNumber)},
                         timeout=MINIMAL_TIMEOUT)
        except Exception:
            pass

    # I am the leader
    def start_sending_ack(self):
        for fc in self.flighComputer.peers:
            try:
                self.requests.get(url=URL(fc) + str(fc) + "/new_leader",
                                  params={"term": str(self.term),
                                          "fc": str(self.myComputerNumber)},
                                  timeout=MINIMAL_TIMEOUT)
            except Exception:
                pass

    def new_leader(self, term, fc):
        self.state = State.follower
        self.trusted_leader = fc
        self.term = term
        Computer.set_timeout_leader()

    def start_sending_heartbeat(self):
        for fc in self.flighComputer.peers:
            try:
                requests.get(url=URL(fc) + str(fc) + "/heartbeat",
                             params={"term": str(self.term),
                                     "fc": str(self.myComputerNumber)},
                             timeout=MINIMAL_TIMEOUT)
            except Exception:
                pass
            
        Computer.set_timeout_heartbeat()


    def received_heartbeat(self, term, fc):

        self.trusted_leader = fc
        self.term = term

        Computer.set_timeout_leader()

    def stop_timeout(self):
        Computer.set_timer(0)

    def send_vote(self, fc):
        try:
            requests.get(url=URL(fc) + str(fc) + "/vote",
                         timeout=MINIMAL_TIMEOUT)
        except Exception:
            pass

        self.trusted_leader = fc

    def send_not_vote(self, fc):
        try:
            requests.get(url=URL(fc) + str(fc) + "/not_vote",
                         params={"term": str(self.term)},
                         timeout=MINIMAL_TIMEOUT)
        except Exception:
            pass
