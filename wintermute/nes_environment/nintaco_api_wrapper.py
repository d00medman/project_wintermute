import nintaco
import threading
import time
should_observe = False
current_obs = None
should_act = False
action = None

class NES:

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
        global current_obs
        global should_act
        current_obs = self.get_observation()
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
            self.timestep()


        self.frame_count += 1

    def timestep(self):
        global should_observe
        global current_obs
        global should_act
        global action
        if should_observe:
            current_obs = self.get_observation()
            should_observe = False

        if should_act:
            self.take_action(action)
            action = None
            should_act = False

    def get_raw_pixels(self):
        pixels = [0] * (256 * 240)
        self.api.getPixels(pixels)
        return pixels

    def get_observation(self):
        return self.get_raw_pixels()

    def take_action(self, action):
        self.api.writeGamepad(0, action, True)

emulator_thread = threading.Thread(target=NES, name='emulator_thread')
emulator_thread.start()

from flask import Flask
app = Flask(__name__)

@app.route('/observe')
def observe():
    global should_observe
    global current_obs
    should_observe = True
    time.sleep(.25)
    return str(current_obs)

@app.route('/act/<a>')
def act(a):
    global should_act
    global action
    action = int(a)
    should_act = True
    time.sleep(.25)
    return 'execute'
