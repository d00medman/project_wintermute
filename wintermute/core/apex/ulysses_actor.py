from wintermute.core.apex.emulator_environment import EmulatorEnvironment
import random


class UlyssesActor:

    def __init__(self, actor_id, time_steps=300, local_buffer_size=25):
        self.env = EmulatorEnvironment()
        # policy used to select actions, a neural net
        self.policy = None
        self.actor_id = actor_id

        self.time_steps = time_steps
        self.step_count = 0

        '''
        Going to start with the local buffer as a dict. It appears to me that this buffer serves the purpose of 
        accumulating data for the purpose of constructing a transition
        '''
        self.local_buffer = {}
        self.local_buffer_size = local_buffer_size
        '''
        I think the difference between the local buffer and the local queue is what confuses me => transition size. are
        transitions a to b, or are they generally larger in size?
        '''
        self.local_queue = []

        '''
        Going to have this threaded and operating in the background. 
        '''
        self.local_learner = None

    def act(self):
        for i in range(self.time_steps):
            # Picking totally at random until I start to build the actual
            action = self._random_action_select()
            print(f'Action selected: {action}')
            observation, reward, done, info = self.env.step(action)
            self.step_count += 1

    def get_transition_tuple_key(self):
        return f'{self.actor_id}_{self.step_count}'

    @staticmethod
    def _random_action_select():
        return random.randint(0, 7)

