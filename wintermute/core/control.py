"""
Athena, primary control system for project Wintermute.
"""

import json
import csv
import sys
import wintermute.core.structure_state as pixel_grid_builder
from wintermute.core.ulysses import Ulysses
from wintermute.core.melete.convolutional_layers import get_trained_model
from wintermute.core.melete.dcec.deep_convolutional_embedded_clustering import load_dcec
from wintermute.common.kafka_nexus import KafkaNexus
import numpy as np
import wintermute.common.topic_names as topics
import random


class Athena(KafkaNexus):

    def __init__(self, stream_from=topics.em_to_am, stream_to=topics.am_to_em):
        super().__init__(stream_from, stream_to)

        self.agent = Ulysses()
        self.melete = load_dcec()
        self.cycles = 0

        print('Athena online; awaiting messages from environment')
        self.listen()

    '''
    Runs continuously upon instantiation of class
    '''
    def listen(self):
        print(f'listening for messages from emulator on stream: {self.stream_from}')
        for message in self.consumer:
            self.cycles += 1
            print(f'message {self.cycles} of {sys.getsizeof(message) / 1000} KB received')

            pixel_list = self.decode_and_normalize_message(message)
            if self.stream_from == topics.em_to_am or self.stream_from == topics.em_to_hs:
                action = str(random.randint(0, 7))
                print(f'sending action {action} to {self.stream_to}')
                self.producer.send(self.stream_to, action.encode('utf-8'))
                self.asses_screen_state(pixel_list)
                self.learn_env_and_output(pixel_list)

            elif self.stream_from == topics.em_to_hs:
                # self.write_data_to_file(pixel_list)
                self.asses_screen_state(pixel_list)

    def asses_screen_state(self, pixel_list):
        if self.melete is None:
            print('Melete inactive, assessment of screen state impossible')
            return

        whole_screen_state = pixel_grid_builder.get_pixel_row_representation(pixel_list)
        format_for_nn = np.reshape(whole_screen_state, (1, 224, 256, 1))
        output = self.melete.predict(format_for_nn)
        print(f'Melete output for whole screen state: {output}')
        # payload = json.dumps("kickstart").encode('utf-8')
        # self.producer.send(self.stream_to, payload)

    def write_data_to_file(self, pixel_list):
        payload = pixel_list
        # json.dumps(pixel_list).encode('utf-8') # Don't think this is needed, but taking data down is kind of a pain
        # TODO: figure out how to handle file interaction within Wintermute
        output_file_path = '../../data_sets/prototype_data_set.csv'
        if self.cycles % 5 == 0:
            print(f'writing {payload} writing to file on cycle {self.cycles}')
        with open(output_file_path, 'at') as csv_file:
            output_writer = csv.writer(csv_file, delimiter=',')
            res = output_writer.writerow(payload)
            print(f'output result: {res}')

    def learn_env_and_output(self, pixel_list):
        pixel_grid = pixel_grid_builder.create_pixel_grid(pixel_list)
        reduced_grid = pixel_grid_builder.reduce_grid(pixel_grid)
        payload = self.stream_q_plan(reduced_grid)
        self.producer.send(self.stream_to, payload)
        print(f'sent message with cycle value {self.cycles} to emulator with an action plan for execution')

    def stream_q_plan(self, visible_environment):
        self.agent.q_learn_environment(visible_environment)
        q_plan = self.agent.get_q_plan()
        return json.dumps([int(a) + 4 for a in q_plan]).encode('utf-8')


def standard_stream_setup():
    Athena()


# TODO: move emulator to data set to independent Thoth setup
def stream_from_emulator_to_data_set():
    Athena(stream_from=topics.em_to_ds)

def stream_from_emulator_to_harness():
    Athena(stream_from=topics.em_to_hs)


if __name__ == "__main__":
    standard_stream_setup()
