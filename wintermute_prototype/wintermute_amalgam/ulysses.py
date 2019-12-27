from navigation import qlearning, get_q_plan
from shrine_of_fiends_outskirts import ShrineOfFiendsEnv
import json
import time

'''
Ulysses; the agent element of the Amalgam. At present, ulysses can interface with a Q learning environment.

For the prototype, the plan ulysses is able to derive leads agent to shrine
'''

class Ulysses():
    def __init__(self, start_location=[9,8]):
        self.current_location = start_location
        self.start_location = start_location
        self.actions = {
            0:'UP',
            1:'DOWN',
            2:'LEFT',
            3:'RIGHT'
        }
        self.alpha = 0.4
        self.gamma = 0.999
        self.epsilon = 0.9
        self.episodes = 1000
        self.max_steps = 250
        print('Ulyssess initiated')

    '''
    Agent runs Q learning black box to create an output plan which it sends to the emulator to be enacted
    '''
    def q_learn_environment(self, map):
        print('Q learning action plan for passed environment')
        self.map = map
        self.env = ShrineOfFiendsEnv(map, self.actions)
        self.Q = qlearning(
            self.alpha,
            self.gamma,
            self.epsilon,
            self.episodes,
            self.max_steps,
            self.env,
            test = True)

    '''
    Learns best course of action through a map, increments plan by 4 to be executable in the nes environment, jsonifies the action plan and returns it
    for use in the communication nexus going back to the nes environment
    '''
    def stream_q_plan(self, map):
        self.q_learn_environment(map)
        q_plan = get_q_plan(self.Q, self.env)
        return json.dumps([int(str(a+4)) for a in q_plan]).encode('utf-8')
