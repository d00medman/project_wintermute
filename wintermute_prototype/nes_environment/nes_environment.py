'''
NES environment.

Initializes remote API connection when program server running on localhost 9998

Started after communication nexus. When one of the two topics is fed to, that one will prompt another interaction
from the other. Both systems stop while waiting for the other.

Next step is to handle actual inputs
'''

import nintaco
from kafka import KafkaProducer, KafkaConsumer
import json

class NESEnvironment():

    def __init__(self, throttle_rate=1, frame_cutoff=64):
        print("run with python, not python3; make sure that python3 venv is not running or this boot will fail")
        nintaco.initRemoteAPI("localhost", 9998)
        self.api = nintaco.getAPI()

        # Action taken when frame count == one second times throttle rate
        self.frame_cutoff = frame_cutoff # todo: make generic and mutable
        self.frame_count = 0
        self.throttle_rate = throttle_rate

        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.consumer = KafkaConsumer('amalgam_to_emulator')

        self.navigation_plan = None

        self.launch()

    '''
    Adds Nintaco remote API listeners then runs the remote API
    '''
    def launch(self):
        self.add_listeners()
        print 'adds listeners'
        self.api.run()

    '''
    Adds listeners for remote API interactions with Nintaco emulator
    '''
    def add_listeners(self):
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
        if self.frame_count % (self.frame_cutoff * self.throttle_rate) == 0:
            if self.navigation_plan == None:
                self.listen()
            elif len(self.navigation_plan) >= 1:
                output = "navigation plan detected. execute action %s, then trim navigation plan to execute next command on next operation %s..." % (self.navigation_plan[0], self.navigation_plan[1:])
                print(output)
                self.api.writeGamepad(0, self.navigation_plan[0], True)
                self.navigation_plan = self.navigation_plan[1:]

        self.frame_count += 1

    '''
    Writes the result of self.get_raw_pixels in a message to the emulator_to_amalgam kafka topic
    '''
    def send_pixels_to_amalgam(self):
        result = self.producer.send('emulator_to_amalgam', json.dumps(self.get_raw_pixels()))
        print('Sent message to nexus at frame count', self.frame_count)

    '''
    Definitley some screwiness here, can probably have a more efficient throttle going
    '''
    def listen(self):
        print('no navigation_plan detected. listening for action at frame: ', self.frame_count)
        for message in self.consumer:
            print('message in amalgam_to_emulator with value: ', message.value)
            if self.navigation_plan == None:
                if message.value.decode('utf-8') == 'kickstart':
                    print 'requesting navigation plan'
                    self.send_pixels_to_amalgam()
                else:
                    self.navigation_plan = self.decode_and_normalize_message(message)
                    print('navigation plan saved: ', self.navigation_plan)

            print('sending message to emulator_to_amalgam')
            result = self.producer.send('emulator_to_amalgam', json.dumps(self.get_raw_pixels()))

            break # break means we only interact w/first message
        print 'after iteration over consumer block'

    '''
    creates a one dimension array with 61440 entries, then uses this to get the pixels on screen from the remote API
    '''
    def get_raw_pixels(self):
        pixels = [0] * (256*240)
        self.api.getPixels(pixels)
        return pixels

    '''
    Returns a list of integers from a passed message
    
    @param message: a json string recovered from kafka; this method transforms the string into an integer array
    '''
    def decode_and_normalize_message(self, message):
        decoded_message = message.value.decode('utf-8').replace(']','').replace('[','')
        # print('decoded message type: ', [type(i) for i in decoded_message.split(",")])
        # print('decoded message: ', [i for i in decoded_message.split(",")])
        return [int(i) for i in decoded_message.split(",")]

if __name__ == "__main__":
    NESEnvironment()
