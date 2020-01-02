import numpy as np
import sys
from gym.envs.toy_text import discrete

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


'''
So is this really just an internal representation of some sort? My own mind body problem remains unanswered.

probably worth noting exactly what is inherited from the discrete env

discrete env -> gridworld -> final fantasy gridworld

big TODO: determine which code belongs in which of the two listed buckets.
'''


class ShrineOfFiendsEnv(discrete.DiscreteEnv):

    # defines render modes. unsure if actually used
    metadata = {'render.modes': ['human', 'ansi']}

    """
    Initialize gridworld environment representation for agent
    
    @param composite_grid a 13 x 15 matrix of scalar values representing the most common pixel color appearing on the 
           screen
    @param actions scalar values of actions the agent is capable of taking in the environment,
    @param shape a tuple formatted [y, x] which is used to construct the scalar state ID matrix
    """
    def __init__(self, composite_grid, actions, shape=[13, 15]):
        self.shape = np.array(shape)
        '''
        shape format = [y, x]
        
        shape of composite grid for Shrine of Fiends test:
        [
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
        '''
        self.composite_grid = composite_grid

        nS = np.prod(self.shape)
        nA = len(actions)

        MAX_Y = shape[0]
        MAX_X = shape[1]

        # Initialize transition probabilities and rewards
        P = {}
        '''
        
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
        grid = np.arange(nS).reshape(shape)
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
            P[s] = {a: [] for a in actions}

            '''
            Crux of splitting generic rules from general purpose gridworld construction here.
            
            Code is pretty badly entangled here. Almost certainly worth expanding into more verbose forms. These verbose
            forms can then be tagged for the general purpose representation or the FF specific one
            '''
            is_done = lambda y, x: self.composite_grid[y][x] == 16
            is_water_tile = lambda y, x: self.composite_grid[y][x] == 33

            reward = 1.0 if is_done(y, x) else -1.0

            # We're stuck in a terminal state
            if is_done(y, x):
                P[s][UP] = [(1.0, s, reward, True)]
                P[s][RIGHT] = [(1.0, s, reward, True)]
                P[s][DOWN] = [(1.0, s, reward, True)]
                P[s][LEFT] = [(1.0, s, reward, True)]
            # Not a terminal state
            else:
                ns_up = s if y == 0 or is_water_tile(y-1, x) else s - MAX_X
                ns_right = s if x == (MAX_X - 1) or is_water_tile(y, x+1) else s + 1
                ns_down = s if y == (MAX_Y - 1) or is_water_tile(y+1, x) else s + MAX_X
                ns_left = s if x == 0 or is_water_tile(y, x-1) else s - 1
                P[s][UP] = [(1.0, ns_up, reward, is_done(y, x))]
                P[s][RIGHT] = [(1.0, ns_right, reward, is_done(y, x))]
                P[s][DOWN] = [(1.0, ns_down, reward, is_done(y, x))]
                P[s][LEFT] = [(1.0, ns_left, reward, is_done(y, x))]

            it.iternext()

        # Initial state distribution is uniform
        isd = np.ones(nS) / nS

        # We expose the model of the environment for educational purposes
        # This should not be used in any model-free learning algorithm
        self.P = P

        # self.s is the scalar value of the agent start point on initialization
        self.s = 112

        super(ShrineOfFiendsEnv, self).__init__(nS, nA, P, isd)

    '''
    Prints a representation of the current environmental state
    
    @param mode: doesn't actually seem to be used, probably related to metadata field on top. unclear to me what ansi is
                 as a representation mode, or why I would want to represent the environment in ansi
    '''
    def render(self, mode='human'):
        outfile = sys.stdout

        for s in range(self.nS):
            position = np.unravel_index(s, self.shape)
            # Player character location
            if self.s == s:
                output = " @ "
            elif self.composite_grid[position[0]][position[1]] == 16:
                '''
                Reward point. For Shrine of Fiends test, we're going to hardcode this as the only 16 that showed up. This might not even be accurate, but it does enable testing in a vacuum
                This, along with the character state identifications, is one of the core sensory heuristics I need to work on
                '''
                output = " * "
            # # Water tiles. Impassible w/o boat
            elif self.composite_grid[position[0]][position[1]] == 33:
                output = " B "
            # # Forest or meadows. Might have random encounters. Squares are passable
            elif self.composite_grid[position[0]][position[1]] == 25 or self.composite_grid[position[0]][position[1]] == 26:
                output = " G "
            # Probably black, given the color's role in literally outlining the universe. these behave like green squares anyways
            elif self.composite_grid[position[0]][position[1]] == 15:
                output = " G "

            if position[1] == 0:
                output = output.lstrip()
            if position[1] == self.shape[1] - 1:
                output = output.rstrip()
                output += '\n'

            outfile.write(output)
        outfile.write('\n')
