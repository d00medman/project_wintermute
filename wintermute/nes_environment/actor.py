import gym
from gym import error, spaces
import numpy as np
import tensorflow as tf
import wintermute.nes_environment.nintaco as nintaco
import random
import asyncio
from collections import namedtuple

StepTuple = namedtuple('Step', ['state', 'action', 'reward', 'discount'])

action_ref = {
            0: "A",
            1: "B",
            2: "SELECT",
            3: "START",
            4: "UP",
            5: "DOWN",
            6: "LEFT",
            7: "RIGHT"
        }



class Actor:

    def __init__(self, throttle_rate=1, frame_cutoff=64, port_number=9999, auto_launch=True):
        nintaco.initRemoteAPI("localhost", port_number)
        self.api = nintaco.getAPI()

        # Action taken when frame count == one second times throttle rate
        self.frame_cutoff = frame_cutoff
        self.frame_count = 0
        self.throttle_rate = throttle_rate

        self._action_set = {
            "A": 0,
            "B": 1,
            "SELECT": 2,
            "START": 3,
            "UP": 4,
            "DOWN": 5,
            "LEFT": 6,
            "RIGHT": 7
        }
        # self.action_space = spaces.Discrete(len(self._action_set))
        # self.observation_space = spaces.Box(low=0, high=64, shape=(224, 256, 1), dtype=np.uint8)

        # Initially, a dueling DQN; eventually, build out to be R2D@
        self.policy = None

        self.current_state = None
        self.local_buffer = []

        if auto_launch:
            self.add_listeners()
            self.launch()

    '''
    Adds Nintaco remote API listeners then runs the remote API
    '''

    def launch(self):
        print('launching API')
        self.api.run()

    '''
    Adds listeners for remote API interactions with Nintaco emulator
    '''

    def add_listeners(self):
        print('adds listeners')
        self.api.addFrameListener(self.renderFinished)
        self.api.addActivateListener(self.apiEnabled)
        self.api.addDeactivateListener(self.apiDisabled)
        self.api.addStopListener(self.dispose)

    '''
    Fired when remote API is initially enabled
    '''

    def apiEnabled(self):
        print("API enabled")

    '''
    Fired when remote API is disabled
    '''

    def apiDisabled(self):
        print("API disabled")

    '''
    Fired when the API is stopped. Unclear what difference between disabled and stopped is
    '''

    def dispose(self):
        print("API stopped")

    '''
    Fires once per frame.

    Only takes action at time point set by constructor. This defaults to once per second

    If there is no navigation plan set, runs the listen method

    If there is a navigation plan set, pop and execute the first action of the navigation plan 
    '''

    def renderFinished(self):
        # pixels = self.get_raw_pixels()
        if self.frame_count % (self.frame_cutoff * self.throttle_rate) == 0:
            self.step(self.select_action())
            # print(f'pixels: {self.get_raw_pixels()}')
            # action()
            # self.current_pixels = self.get_raw_pixels()
        #     self.should_act = False
        #     print(self.get_raw_pixels())
        #     # if self.stream_to == topics.em_to_am:
        #         # print('sending pixels to amalgam')
        #         # self.send_pixels_to_amalgam()
        #     # elif self.stream_to == topics.em_to_ds or self.stream_to == topics.em_to_hs:
        #     #     print('api frame hit')
        #         # print(self.get_raw_pixels())
        #         # self.send_pixels_to_data_set()
        #
        self.frame_count += 1

    def get_raw_pixels(self):
        pixels = [0] * (256 * 240)
        self.api.getPixels(pixels)
        return pixels

    def get_observation(self):
        return self.get_raw_pixels()

    def take_action(self, action):
        self.api.writeGamepad(0, action, True)

    def select_action(self):
        if self.policy is None:
            return random.randint(0, 7)
        else:
            '''
            Feed current_state to policy and return action selected
            '''
            pass

    def pause(self, pause):
        self.api.setPaused(pause)

    # Gym required methods
    def step(self, action):
        print(f'Taking action: {action_ref.get(action)}')
        # select action by querying policy
        self.take_action(self.select_action())

        # We want the action to be fully taken before the new observation is returned
        yield from asyncio.sleep(1)
        next_observation = self.get_observation()
        print(f'Returned observation; first pixel square: {next_observation[:16 * 16]}')
        reward, done = self.assess_next_state()
        # done = None
        info = None

        '''
        based on the hyperparameters, we'd then batch the data. If we are at the right point, I imagine we'd send it to
        the replay server (standalone web app communicated with via HTTP requests)?
        '''

        return next_observation, reward, done, info

    def assess_next_state(self):
        reward = None
        done = None
        return reward, done

    def reset(self):
        # TODO: determine how to programatically reset to initial state
        observation = self.api.get_raw_pixels()
        return observation

    def close(self):
        # TODO: Implement this
        pass

    def render(self, mode='human'):
        # TODO: How to handle rendering, given that rendering determined on boot
        pass

    def seed(self, seed=None):
        # TODO: What is seeding? is it needed?
        return


if __name__ == '__main__':
    wrapper = GameEnvironment(throttle_rate=3)
