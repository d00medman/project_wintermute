import gym
import random
import requests
from wintermute.nes_environment.nintaco_api_wrapper import LOCAL_SERVER_URL


class EmulatorEnvironment(gym.Env):

    def __init__(self):
        self.api_url = LOCAL_SERVER_URL

    def step(self, action):
        r = requests.get(self.api_url + f'step/{action}')
        observation = r.text
        # send request with action to act endpoint

        # await response
        # parse observation from response
        # derive reward and "done" from from observation
        # produce info dict (not clear what will be needed here)
        reward = None
        done = None
        info = None
        return observation, reward, done, info

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    @staticmethod
    def _random_action_select():
        return random.randint(0, 7)


if __name__ == '__main__':
    env = EmulatorEnvironment()
    for _ in range(20):
        a = env._random_action_select()
        print(f'Action selected: {a}')
        env.step(a)
