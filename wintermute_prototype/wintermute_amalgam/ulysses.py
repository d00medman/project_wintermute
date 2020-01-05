from shrine_of_fiends_outskirts import ShrineOfFiendsEnv
import json
import numpy as np
from gridworld import GridWorld

'''
Annotation of methods for agent complete. Need to brainstorm what directions improvement is needed in
'''


class Ulysses:
    """
    Initialize agent and hyperparameters

    Initializes Q and environment as none; sets these upon invocation of q_learn_environment

    @param alpha: learning rate
    @param gamma: discount rate
    @param epsilon: greed
    @param episodes_for_training: how many episodes to run in the training of Q
    @max_steps_per_episode: How many steps are taken in each of said episodes
    """
    def __init__(self, alpha=0.4, gamma=0.999, epsilon=0.9, episodes_for_training=1000, max_steps_per_episode=250):
        # TODO: determine how to make action scalar values match those that are needed by the emulator
        self.actions = {
            'UP': 0,
            'DOWN': 1,
            'LEFT': 2,
            'RIGHT': 3
        }
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episodes = episodes_for_training
        self.max_steps = max_steps_per_episode
        self.env = None
        self.Q = None
        print('Ulysses initiated')

    '''
    invokes q_learn_environment, the derives a plan of actions (q_plan) via get_q_plan.
    
    Adds 4 to the scalar action values of the returned Q plan and encodes this new value in utf 8 to be streamed to 
    kafka
    
    Frankly might make more sense to have the latter done in the communication nexus, as the json transformation is only
    relevant in said context
    
    @param visible_environment a matrix of scalar values representing the game environment. 
    '''

    def stream_q_plan(self, visible_environment):
        self.q_learn_environment(visible_environment)

        q_plan = self.get_q_plan(self.Q, self.env)
        return json.dumps([int(a) + 4 for a in q_plan]).encode('utf-8')

    '''
    initializes the env (the visible_environment for which Ulysses seeks a solution), then learns q via learn_q
    
    @param visible_environment a matrix of scalar values representing the game environment. 
    '''

    def q_learn_environment(self, visible_environment):
        print('Q learning action plan for passed environment')
        self.env = ShrineOfFiendsEnv(visible_environment, self.actions)
        self.Q = self.learn_q()

    '''
    The meat of the Q learning algorithm
    
    For sure needs better documentation and illustration of contours of data flow (similar to what was done in the env)
    
    @param render: a flag denoting whether the agent should output his internal representation of the environment at 
                   certain points
    '''
    def learn_q(self, render=False):
        n_states, n_actions = self.env.nS, self.env.nA

        # Q is array tracking main action, state value function
        Q = self.init_q(n_states, n_actions, type="ones")
        for episode in range(self.episodes):

            # state resets at start of each episode
            self.env.s = 112
            s = self.env.s

            # a is an action selected under the epsilon-greedy policy
            a = self.epsilon_greedy_action_selection(Q, n_actions, s)
            # t is the current time step
            t = 0
            total_reward = 0
            while t < self.max_steps:
                if render:
                    self.env.render()
                t += 1
                '''
                gets a tuple containing probability, the numeric next state (s_), the reward at s_ next reward and 
                whether the state was terminal
                '''
                [(prob, s_, reward, done)] = self.env.step(a) #self.env.P[s][a]  # env.step(a)
                # Take step, then administer reward
                total_reward += reward
                # next action (a_) is the one whose next state has the highest utility
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

    '''
    initializes the state value function, Q to a numpy matrix with a shape determined by a tuple containing
    the number of actions and number of states. Scalar values for this matrix determined by type variable
    
    @param num_states the number of states
    @param num_actions the number of actions
    @param type Sets scalar values for matrix entries
    '''

    def init_q(self, num_states, num_actions, type="ones"):
        if type == "ones":
            return np.ones((num_states, num_actions))
        elif type == "random":
            return np.random.random((num_states, num_actions))
        elif type == "zeros":
            return np.zeros((num_states, num_actions))

    '''
    Selects an action.
    
    If the train parameter is set to true, or a random number lower than the epsilon hyperparameter is rolled, select
    the action with the highest Q value for the given state
    
    Otherwise, if the train param is off and epsilon is higher than the rolled number, select a random action
    
    Would for sure like to change this so the actions selected are 4-7, rather than selecting 0-3 and adding 4
    when sending the message 
    
    @param Q: state value tuple array
    @param n_actions: scalar values representing actions available to agent
    @param s: a scalar state for which we are selecting an action
    @param train: flag which, when set ensures that action is selected on basis of argmax Q for s
    '''

    def epsilon_greedy_action_selection(self, Q, n_actions, s, train=False):
        if train or np.random.rand() < self.epsilon:
            action = np.argmax(Q[s, :])
        else:
            action = np.random.randint(0, n_actions)
        return action

    '''
    Passed in a learned Q function for an environment, runs through environment to find route to reward. Returns a list,
    action_plan of all scalar action values needed to attain reward
    
    @param Q: A learned Q array
    @param env: the environment representation on which Q was learned
    '''
    def get_q_plan(self, Q, env):
        # TODO: figure out guardrail plan and generalize to rest of system
        # if self.Q is None or self.env is None:
        #     return []
        action_plan = []

        # Same code for state resetting. TODO: encapsulate and properly affix this
        env.s = 112
        s = env.s

        n_actions = env.nA
        moves = 0
        while True:
            # time.sleep(1)
            if moves == 0:
                print('initial state')
                env.render()
            moves += 1
            a = self.epsilon_greedy_action_selection(Q, n_actions, s, train=True)
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
If this script is run from the command line, learn Q via a hardcoded representation of the shrine of fiends state

primarily for purposes od debugging
'''
if __name__ == '__main__':
    vis_env = [
        [26, 26, 26, 26, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33],
        [26, 26, 15, 15, 26, 26, 26, 26, 33, 33, 33, 33, 33, 33, 33],
        [26, 26, 16, 15, 26, 26, 26, 26, 26, 26, 26, 33, 33, 33, 33],
        [25, 25, 25, 25, 25, 25, 25, 25, 15, 26, 26, 26, 33, 33, 33],
        [15, 25, 25, 25, 25, 25, 25, 25, 25, 15, 26, 33, 33, 33, 33],
        [26, 15, 15, 15, 25, 25, 25, 25, 15, 26, 33, 33, 33, 33, 33],
        [33, 26, 15, 26, 15, 25, 25, 15, 15, 26, 33, 33, 33, 33, 33],
        [33, 33, 33, 33, 26, 15, 25, 25, 15, 26, 33, 33, 33, 33, 33],
        [33, 33, 33, 33, 33, 26, 15, 25, 25, 15, 33, 33, 33, 33, 33],
        [33, 33, 33, 33, 33, 33, 26, 15, 15, 15, 33, 33, 33, 33, 33],
        [33, 33, 33, 33, 33, 33, 26, 26, 26, 26, 33, 33, 33, 33, 33],
        [33, 33, 33, 33, 33, 33, 26, 26, 26, 26, 26, 33, 33, 33, 33],
        [33, 33, 33, 33, 33, 26, 26, 26, 26, 26, 26, 33, 33, 33, 33]
    ]
    Ulysses().q_learn_environment(vis_env)
