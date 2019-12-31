'''
Calling this directory wintermute amalgam at present. While de-amalgamizing the agent and environment of wintermute is the main goal
for the prototype at present, the house for this to happen must be put in order first.

At present, the lines between agent and environment are muddled in code. That being said, there are some key linkages to be made here.

Present technical frontiers:
Able to encode the pixel data string and send to kafka topic

Able to turn the pixel data screen into a compressed representation

able to q-learn a compressed representation

able to create and output an action plan to solve the compressed representation

unable to execute the action plan, as attempts to queue plan to message were unsuccessful
'''

from kafka import KafkaProducer, KafkaConsumer
import json
import state_construction_algorithm as pixel_grid_builder
import sys
import ulysses


class CommunicationNexus:

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.consumer = KafkaConsumer('emulator_to_amalgam')
        self.agent = ulysses.Ulysses()
        self.cycles = 0
        self.listen()

    '''
    Runs continuously upon instantiation of class
    '''
    def listen(self):
        print('listening for messages from emulator')
        for message in self.consumer:
            self.cycles += 1
            print(f'message {self.cycles} of {sys.getsizeof(message) / 1000} KB received')
            # Going to leave these separate for the time being, keeps things clear
            pixel_grid = pixel_grid_builder.create_pixel_grid(self.decode_and_normalize_message(message))
            reduced_grid = pixel_grid_builder.reduce_grid(pixel_grid)
            streaming_action_plan = self.agent.stream_q_plan(reduced_grid)

            result = self.producer.send('amalgam_to_emulator', streaming_action_plan)
            print(f'sent message with cycle value {self.cycles} to emulator with an action plan for execution')

    '''
    This method also used in nes environment. Would likely be well served to move this (and kafka conusmer in general) into shared, independent system.

    Big block here remains poor understanding of how imports work in python (and how these differences manifest between python and python3)
    '''
    def decode_and_normalize_message(self, message):
        decoded_message = message.value.decode('utf-8').replace(']', '').replace('[', '')
        return [int(i) for i in decoded_message.split(",")]


if __name__ == "__main__":
    CommunicationNexus()
