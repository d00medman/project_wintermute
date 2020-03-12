"""
NES environment.

Initializes remote API connection when program server running on localhost 9998

Started after communication nexus. When one of the two topics is fed to, that one will prompt another interaction
from the other. Both systems stop while waiting for the other.
"""

import sys
import nintaco
from kafka import KafkaProducer, KafkaConsumer
import json
import wintermute.common.topic_names as topics
from aiokafka import AIOKafkaConsumer
import asyncio


class NESEnvironment:

    def __init__(self, throttle_rate=1, frame_cutoff=64, stream_from=topics.am_to_em, stream_to=topics.em_to_am):
        print("run with python, not python3; make sure that python3 venv is not running or this boot will fail")
        # super(NESEnvironment, self).__init__(stream_from, stream_to)
        nintaco.initRemoteAPI("localhost", 9999)
        self.api = nintaco.getAPI()

        # Action taken when frame count == one second times throttle rate
        self.frame_cutoff = frame_cutoff
        self.frame_count = 0
        self.throttle_rate = throttle_rate

        self.stream_to = stream_to
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(stream_from, loop=self.loop)

        self.navigation_plan = None

        self.launch()

    '''
    Adds Nintaco remote API listeners then runs the remote API
    '''
    def launch(self):
        self.add_listeners()
        print('adds listeners')
        # loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.launch_async())

    async def launch_async(self):
        await self.consumer.start()
        await asyncio.gather(self.api.run_async(), self.listen_async())

    async def listen_async(self):

        try:
            async for message in self.consumer:
                self.write_pixels_to_stream()
                action = self.decode_and_normalize_message(message)
                self.api.writeGamepad(0, action, True)
                await asyncio.sleep(1)
        finally:
            await self.consumer.stop()


    '''
    Adds listeners for remote API interactions with Nintaco emulator
    '''
    def add_listeners(self):
        self.api.addFrameListener(self.renderFinished)
        # self.api.addActivateListener(self.apiEnabled)
        # self.api.addDeactivateListener(self.apiDisabled)
        # self.api.addStopListener(self.dispose)

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
    async def renderFinished(self):
        if self.frame_count % (self.frame_cutoff * self.throttle_rate) == 0:
            if self.stream_to == topics.em_to_am:
                print('sending pixels to amalgam')
                # self.write_pixels_to_stream()
                # action = self.get_action()
                # self.api.writeGamepad(0, action, True)
                await self.listen_async()

            elif self.stream_to == topics.em_to_ds or self.stream_to == topics.em_to_hs:
                print('api frame hit')
                # print(self.get_raw_pixels())
                # self.send_pixels_to_data_set()
            else:
                self.write_pixels_to_stream()

        self.frame_count += 1

    def get_action(self):
        for message in self.consumer:
            self.decode_and_normalize_message(message)
            self.consumer.close()


    def send_pixels_to_data_set(self):
        self.write_pixels_to_stream()

    def send_pixels_to_amalgam(self):
        if self.navigation_plan is None:
            print('listening')
            self.listen()
        elif len(self.navigation_plan) >= 1:
            output = "navigation plan detected. execute action %s, then trim navigation plan to execute next command on next operation %s..." % (
            self.navigation_plan[0], self.navigation_plan[1:])
            print(output)
            self.api.writeGamepad(0, self.navigation_plan[0], True)
            self.navigation_plan = self.navigation_plan[1:]

    '''
    Writes the result of self.get_raw_pixels in a message to the emulator_to_amalgam kafka topic
    '''
    def write_pixels_to_stream(self):
        self.producer.send(self.stream_to, json.dumps(self.get_raw_pixels()).encode('utf-8'))
        print('Sent message to nexus at frame count', self.frame_count)

    '''
    Definitley some screwiness here, can probably have a more efficient throttle going
    '''
    def listen(self):
        print('no navigation_plan detected. listening for action at frame: ', self.frame_count)
        for message in self.consumer:
            print('message in amalgam_to_emulator with value: ', message.value)
            if self.navigation_plan is None:
                # Temporary while testing efficacy of model
                # self.write_pixels_to_stream()
                if message.value.decode('utf-8') == 'kickstart':
                    print('requesting navigation plan')
                    self.write_pixels_to_stream()
                else:
                    self.navigation_plan = self.decode_and_normalize_message(message)
                    print('navigation plan saved: ', self.navigation_plan)

            break # break means we only interact w/first message
        print('after iteration over consumer block')

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
        return [int(i) for i in decoded_message.split(",")]


def stream_to_emulator():
    NESEnvironment()


def stream_to_dataset():
    NESEnvironment(stream_to=topics.em_to_ds)

def stream_to_harness():
    NESEnvironment(stream_to=topics.em_to_hs)


if __name__ == "__main__":
    stream_to_emulator()
