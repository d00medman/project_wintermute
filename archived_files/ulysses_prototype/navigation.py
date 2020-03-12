'''
Base file from: https://gist.github.com/TimeTraveller-San/9e56f9d09be7d50b795ef2f83be2ba72#file-qlearning-py, all commentary in green except this his
Heavy inspiration from:
https://github.com/Neo-47/Reinforcement-Learning-Algorithms/blob/master/Dynamic%20Programming/gridworld.py
https://github.com/openai/gym/blob/master/gym/envs/toy_text/cliffwalking.py
'''
import gym
import numpy as np
import time
from shrine_of_fiends_outskirts import ShrineOfFiendsEnv


'''
TODO: fold these into Ulysses
'''

"""
Qlearning is an off policy learning python implementation.
This is a python implementation of the qlearning algorithm in the Sutton and
Barto's book on RL. It's called SARSA because - (state, action, reward, state,
action). The only difference between SARSA and Qlearning is that SARSA takes the
next action based on the current policy while qlearning takes the action with
maximum utility of next state.
Using the simplest gym environment for brevity: https://gym.openai.com/envs/FrozenLake-v0/
"""

def init_q(s, a, type="ones"):
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


def epsilon_greedy(Q, epsilon, n_actions, s, train=False):
    """
    @param Q Q values state x action -> value
    @param epsilon boldness in exploration
    @param s number of states
    @param train if true then no random actions selected
    """
    if train or np.random.rand() < epsilon:
        action = np.argmax(Q[s, :])
    else:
        action = np.random.randint(0, n_actions)
    return action

def qlearning(alpha, gamma, epsilon, episodes, max_steps, env, render = False, test=False, composite_grid=map):
    """
    @param alpha learning rate
    @param gamma decay factor
    @param epsilon boldness in exploration
    @param max_steps for max step in each episode
    @param n_tests number of test episodes
    """
    # env = ShrineOfFiendsEnv
    n_states, n_actions = env.nS, env.nA

    # Q is array tracking main action, state value function
    Q = init_q(n_states, n_actions, type="ones")
    timestep_reward = []
    for episode in range(episodes):

        env.s = 158
        s = env.s # state resets at start of each episode

        a = epsilon_greedy(Q, epsilon, n_actions, s) # A is an action selected under the ep-greedy policy
        t = 0 # t is time steps
        total_reward = 0
        done = False
        while t < max_steps:
            if render:
                env.render()
            t += 1
            # s_ = next state, a_ = next action
            [(prob, s_, reward, done)] = env.P[s][a] #env.step(a) #gets a tuple containing next state, next reward, whether the state was terminal, and value named info of unknown use
            # Take step, then administer reward
            total_reward += reward
            # next action is the one whose next state has the highest utility
            a_ = np.argmax(Q[s_, :])
            if done:
                Q[s, a] += alpha * ( reward  - Q[s, a] )
            else:
                next_q = Q[s_, a_]
                Q[s, a] += alpha * ( reward + (gamma * next_q) - Q[s, a] )
            s, a = s_, a_
            if done:
                if render:
                    print(f"This episode took {t} timesteps and reward: {total_reward}")
                timestep_reward.append(total_reward)
                break
    print(f"Final Episode #{episode} complete. Q length: {len(Q)}")
    return Q



def get_q_plan(Q, env):
    action_plan = []
    epsilon = 0
    env.s = 158
    s = env.s

    print
    n_actions = env.nA
    moves = 0
    while True:
        time.sleep(1)
        if (moves == 0):
            print('initial state')
            env.render()
        moves+=1
        a = epsilon_greedy(Q, epsilon, n_actions, s, train=True)
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


'''
Unwilling to delete this method while nature of time unclear
'''
def test_agent(Q, env, n_tests, n_actions, delay=1):
    for test in range(n_tests):
        print(f"Test #{test}")
        s = env.reset()
        done = False
        epsilon = 0
        while True:
            time.sleep(delay)
            env.render()
            a = epsilon_greedy(Q, epsilon, n_actions, s, train=True)
            print(f"Chose action {a} for state {s}")
            s, reward, done, info = env.step(a)
            if done:
                if reward > 0:
                    print("Reached goal!")
                else:
                    print("Shit! dead x_x")
                time.sleep(3)
                break
