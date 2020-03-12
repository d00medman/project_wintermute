from gridworld import GridWorld
import numpy as np
import sys

default_actions = {
    'UP': 0,
    'DOWN': 1,
    'LEFT': 2,
    'RIGHT': 3
}

default_shape = [13, 15]


class FinalFantasyGridWorld(GridWorld):

    def __init__(self, game_state_matrix, actions=default_actions):

        self.game_state = np.asarray(game_state_matrix)

        super().__init__(shape=self.game_state.shape, actions=actions)

    def get_next_state_scalar(self, action, s, y, x):
        # print('use local class scalar assessment')
        if action == 'UP':
            return s if y == 0 or not self.is_square_passable(y - 1, x) else s - self.max_x
        elif action == 'DOWN':
            return s if y == (self.max_y - 1) or not self.is_square_passable(y + 1, x) else s + self.max_x
        elif action == 'RIGHT':
            return s if x == (self.max_x - 1) or not self.is_square_passable(y, x + 1) else s + 1
        elif action == 'LEFT':
            return s if x == 0 or not self.is_square_passable(y, x - 1) else s - 1
        else:
            print('non_default action, currently unable to handle; setting next state to current state')
            return s

    '''
    Terminal state checking a little screwy for sure. Needs params for both. Might be worth having all params bundled?
    Imagine that terminality checking will be expanded eventually
    '''
    def is_state_terminal(self, state_scalar, y, x):
        # print('use local terminal state')
        return self.game_state[y][x] == 16

    '''
    This is a bolt. Not sure when it will be relevant in the future, but certainly worth noting
    '''
    def is_square_passable(self, y, x):
        # 33 indicates water tiles which cannot be passed
        return self.game_state[y][x] != 33

    def render(self, mode='human'):
        outfile = sys.stdout

        # output = ''
        for s in range(self.nS):
            position = np.unravel_index(s, self.shape)
            # Player character location
            if self.s == s:
                output = " @ "
            elif self.game_state[position[0]][position[1]] == 16:
                '''
                Reward point. For Shrine of Fiends test, we're going to hardcode this as the only 16 that showed up. This might not even be accurate, but it does enable testing in a vacuum
                This, along with the character state identifications, is one of the core sensory heuristics I need to work on
                '''
                output = " * "
            # # Water tiles. Impassible w/o boat
            elif self.game_state[position[0]][position[1]] == 33:
                output = " B "
            # # Forest or meadows. Might have random encounters. Squares are passable
            elif self.game_state[position[0]][position[1]] == 25 or self.game_state[position[0]][position[1]] == 26:
                output = " G "
            # Probably black, given the color's role in literally outlining the universe. these behave like green squares anyways
            elif self.game_state[position[0]][position[1]] == 15:
                output = " G "

            if position[1] == 0:
                output = output.lstrip()
            if position[1] == self.shape[1] - 1:
                output = output.rstrip()
                output += '\n'

            outfile.write(output)
        outfile.write('\n')

    '''
    So needs to basically be the normal gridworld

    needs additional state representation matrix

    needs environment rules - how to manifest these? reduce probability? solution
    currently implemented appears to 

    needs specific terminal state

    needs specific render function

    how to change the criteria by which squares are assessed but not change the overarching algorithm for getting the 
    transition tuples?
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
    env = FinalFantasyGridWorld(vis_env)
    env.render()
    print(env.P)