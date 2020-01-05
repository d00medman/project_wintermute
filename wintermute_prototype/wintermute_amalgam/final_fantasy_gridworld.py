from gridworld import GridWorld

class FinalFantasyGridWorld(GridWorld):

    def __init__(self, game_state_matrix):

        self.game_state = game_state_matrix

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