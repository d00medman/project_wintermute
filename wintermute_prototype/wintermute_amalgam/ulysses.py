# from navigation import qlearning, get_q_plan
from shrine_of_fiends_outskirts import ShrineOfFiendsEnv
import json
import time
import gym
import numpy as np

'''
Ulysses; the agent element of the Amalgam. At present, ulysses can interface with a Q learning environment.

For the prototype, the plan ulysses is able to derive leads agent to shrine
'''


class Ulysses:

    def __init__(self, start_location=[9, 8]):
        self.current_location = start_location
        self.start_location = start_location
        self.actions = {
            0: 'UP',
            1: 'DOWN',
            2: 'LEFT',
            3: 'RIGHT'
        }
        self.alpha = 0.4
        self.gamma = 0.999
        self.epsilon = 0.9
        self.episodes = 1000
        self.max_steps = 250
        # self.map = None
        self.env = None
        self.Q = None
        print('Ulyssess initiated')

    '''
    Learns best course of action through a map, increments plan by 4 to be executable in the nes environment, jsonifies the action plan and returns it
    for use in the communication nexus going back to the nes environment
    '''
    def stream_q_plan(self, visible_environment):
        self.q_learn_environment(visible_environment)
        q_plan = self.get_q_plan(self.Q, self.env)
        # are these layers of translation actually needed?
        # return json.dumps([int(str(a+4)) for a in q_plan]).encode('utf-8')

        return json.dumps([int(a) + 4 for a in q_plan]).encode('utf-8')

    '''
    Agent runs Q learning black box to create an output plan which it sends to the emulator to be enacted
    '''
    def q_learn_environment(self, visible_environment):
        print('Q learning action plan for passed environment')
        # self.map = map
        self.env = ShrineOfFiendsEnv(visible_environment, self.actions)
        self.Q = self.learn_q()

    def learn_q(self, render=False):
        n_states, n_actions = self.env.nS, self.env.nA

        # Q is array tracking main action, state value function
        Q = self.init_q(n_states, n_actions, type="ones")
        for episode in range(self.episodes):

            # state resets at start of each episode
            self.env.s = 158
            s = self.env.s

            a = self.epsilon_greedy(Q, n_actions, s) # A is an action selected under the ep-greedy policy
            # t is the current time step
            t = 0
            total_reward = 0
            done = False
            while t < self.max_steps:
                if render:
                    self.env.render()
                t += 1
                # s_ = next state, a_ = next action
                [(prob, s_, reward, done)] = self.env.P[s][a] #env.step(a) #gets a tuple containing next state, next reward, whether the state was terminal, and value named info of unknown use
                # Take step, then administer reward
                total_reward += reward
                # next action is the one whose next state has the highest utility
                a_ = np.argmax(Q[s_, :])
                if done:
                    Q[s, a] += self.alpha * (reward - Q[s, a])
                else:
                    next_q = Q[s_, a_]
                    Q[s, a] += self.alpha * (reward + (self.gamma * next_q) - Q[s, a])
                s, a = s_, a_
                if done:
                    if render:
                        print(f"This episode took {t} timesteps and reward: {total_reward}")
                    break
        print(f"Final Episode #{episode} complete. Q length: {len(Q)}")
        return Q

    def init_q(self, s, a, type="ones"):
        """
        @param s the number of states
        @param a the number of actions
        @param type random, ones or zeros for the initialization
        """
        if type == "ones":
            return np.ones((s, a))
        elif type == "random":
            return np.random.random((s, a))
        elif type == "zeros":
            return np.zeros((s, a))

    def epsilon_greedy(self, Q, n_actions, s, train=False):
        """
        @param Q Q values state x action -> value
        @param epsilon boldness in exploration
        @param s number of states
        @param train if true then no random actions selected
        """
        if train or np.random.rand() < self.epsilon:
            action = np.argmax(Q[s, :])
        else:
            action = np.random.randint(0, n_actions)
        return action

    '''
    Passed in a learned Q function for an environment, runs through environment to find route to reward
    '''
    def get_q_plan(self, Q, env):
        action_plan = []
        # epsilon = 0
        env.s = 158
        s = env.s

        n_actions = env.nA
        moves = 0
        while True:
            time.sleep(1)
            if moves == 0:
                print('initial state')
                env.render()
            moves += 1
            a = self.epsilon_greedy(Q, n_actions, s, train=True)
            s, reward, done, info = env.step(a)
            action_plan.append(a)
            if done:
                print(f'Returning action plan {action_plan}')
                if reward > 0:
                    print("Reached goal!")
                    env.render()
                    return action_plan
            if moves >= 20:
                print("too many moves, cancelling")
                env.render()
                break
        return action_plan
