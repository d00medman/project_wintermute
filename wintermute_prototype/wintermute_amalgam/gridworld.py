import numpy as np
import sys
from gym.envs.toy_text import discrete

default_actions = {
    'UP': 0,
    'DOWN': 1,
    'LEFT': 2,
    'RIGHT': 3
}

default_shape = [13, 15]


class GridWorld(discrete.DiscreteEnv):
    # defines render modes. unsure if actually used. Going to keep in place for time being
    metadata = {'render.modes': ['human', 'ansi']}

    """
    Generic gridworld, a problem frequently used to illustrate algorithms by Sutton and Barto

    @param actions scalar values of actions the agent is capable of taking in the environment,
    @param shape a tuple formatted [y, x] which is used to construct the scalar state ID matrix
    """

    def __init__(self, actions=default_actions, shape=default_shape, terminal_state=47, initial_state=112):
        self.shape = np.array(shape)

        nS = np.prod(self.shape)
        nA = len(actions)
        self.terminal_state = terminal_state
        self.max_y = self.shape[0]
        self.max_x = self.shape[1]

        P = self.generate_transition_tuples(actions, nS)

        '''
        [0.00512821 0.00512821 ... 0.00512821] 195 times
        
        Same value repeated.
        From where is this value derived? Not even sure how to phrase question of its relation with the divisor
        What is it used for? suppose that will show up in discrete 
        '''
        # Initial state distribution is uniform
        isd = np.ones(nS) / nS

        # We expose the model of the environment for educational purposes
        # This should not be used in any model-free learning algorithm
        self.P = P

        # self.s is the scalar value of the agent start point on initialization
        # Still dealing with a jump, unsure of why

        super(GridWorld, self).__init__(nS, nA, P, isd)
        '''
        Able to firmly plant the initial location by creating the discrete env first, then overriding the value it 
        placed at S
        '''
        self.s = initial_state

    def generate_transition_tuples(self, actions, nS):
        # Initialize transition probabilities and rewards
        P = {}
        '''
        Grid when built with default shape

        [
                  x=0  x=1 x=2 x=3 x=4 x=5 x=6 x=7 x=8 x=9 10  11  12  13  14 
         y = 0   [  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14], 
         y = 1   [ 15  16  17  18  19  20  21  22  23  24  25  26  27  28  29], 
         y = 2   [ 30  31  32  33  34  35  36  37  38  39  40  41  42  43  44], 
         y = 3   [ 45  46  47  48  49  50  51  52  53  54  55  56  57  58  59], 
         y = 4   [ 60  61  62  63  64  65  66  67  68  69  70  71  72  73  74], 
         y = 5   [ 75  76  77  78  79  80  81  82  83  84  85  86  87  88  89], 
         y = 6   [ 90  91  92  93  94  95  96  97  98  99 100 101 102 103 104], 
         y = 7   [105 106 107 108 109 110 111 112 113 114 115 116 117 118 119], 
         y = 8   [120 121 122 123 124 125 126 127 128 129 130 131 132 133 134], 
         y = 9   [135 136 137 138 139 140 141 142 143 144 145 146 147 148 149], 
         y = 10  [150 151 152 153 154 155 156 157 158 159 160 161 162 163 164], 
         y = 11  [165 166 167 168 169 170 171 172 173 174 175 176 177 178 179], 
         y = 12  [180 181 182 183 184 185 186 187 188 189 190 191 192 193 194]
        ]

        112 [7, 7] as starting point? Need general solution for start state

        two distinct representations of state: 
        - composite grid containing most common pixel scalar value
        - grid contains scalar state s = (y * 15) + x

        I am close to 100% certain that these two representations can be merged
        Or, that the first one can be a generic gridworld (which can be submitted to the gym), then I can
        create an extension which overlays the rules of the FF worldmap
        '''
        grid = np.arange(nS).reshape(self.shape)
        '''
        Iterator definition: https://docs.scipy.org/doc/numpy/reference/generated/numpy.nditer.html

        multi_index causes a multi-index, or a tuple of indices with one per iteration dimension, to be tracked.
        '''
        it = np.nditer(grid, flags=['multi_index'])

        '''
        Run over the iterator using the scalar state ids (s) as well as the composite indices that correspond with the 
        composite grid (x, y) 
        '''
        while not it.finished:
            s = it.iterindex
            y, x = it.multi_index

            '''
            structure of tuples contained in the sub-dictionaries in p
            [(probability, next scalar state (s_), reward at s_, terminality of state)]

            p = {
                0:{
                    0:[(1.0, 0, -1.0, False)],
                    1:[(1.0, 15, -1.0, False)],
                    2:[(1.0, 0, -1.0, False)],
                    3:[(1.0, 1, -1.0, False)]
                },
                1:{
                    0:[(1.0, 1, -1.0, False)],
                    1:[(1.0, 16, -1.0, False)],
                    2:[(1.0, 0, -1.0, False)],
                    3:[(1.0, 2, -1.0, False)]
                },
                ...
                193:{
                    0:[(1.0, 193, -1.0, False)],
                    1:[(1.0, 193, -1.0, False)],
                    2:[(1.0, 193, -1.0, False)],
                    3:[(1.0, 193, -1.0, False)]
                }
                194:{
                    0:[(1.0, 194, -1.0, False)],
                    1:[(1.0, 194, -1.0, False)],
                    2:[(1.0, 194, -1.0, False)],
                    3:[(1.0, 194, -1.0, False)]
                }
            }
            '''
            P[s] = {actions.get(action): [] for action in actions}

            is_done = self.is_state_terminal(s)

            reward = 1.0 if is_done else -1.0

            for action in actions:
                action_scalar = actions.get(action)
                if is_done:
                    P[s][action_scalar] = [(1.0, s, reward, True)]
                else:
                    if action == 'UP':
                        next_state_scalar = s if y == 0 else s - self.max_x
                    elif action == 'DOWN':
                        next_state_scalar = s if y == (self.max_y - 1) else s + self.max_x
                    elif action == 'RIGHT':
                        next_state_scalar = s if x == (self.max_x - 1) else s + 1
                    elif action == 'LEFT':
                        next_state_scalar = s if x == 0 else s - 1
                    else:
                        print('non_default action, currently unable to handle; setting next state to current state')
                        next_state_scalar = s

                    P[s][action_scalar] = [(1.0, next_state_scalar, reward, is_done)]

            it.iternext()
        return P

    def is_state_terminal(self, state_scalar):
        return state_scalar == self.terminal_state

    '''
    Prints a representation of the current environmental state

    @param mode: doesn't actually seem to be used, probably related to metadata field on top. unclear to me what ansi is
                 as a representation mode, or why I would want to represent the environment in ansi
    '''

    def render(self, mode='human'):
        outfile = sys.stdout

        for s in range(self.nS):
            position = np.unravel_index(s, self.shape)
            # Agent location
            if self.s == s:
                output = " @ "
            # Goal state
            elif s == 47:
                output = " * "
            else:
                output = " 0 "

            if position[1] == 0:
                output = output.lstrip()
            if position[1] == self.shape[1] - 1:
                output = output.rstrip()
                output += '\n'

            outfile.write(output)
        outfile.write('\n')


if __name__ == '__main__':
    GridWorld().render()
