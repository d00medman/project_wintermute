import json
from wintermute.common.kafka_nexus import KafkaNexus
import wintermute.common.topic_names as topics
import csv
import time
import pickle
import os
import wintermute.core.structure_state as pixel_grid_builder
import numpy as np
import random
from sklearn.model_selection import train_test_split
# possibly don't need TF in this file, but want to keep this code in for the time being
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import tensorflow as tf

# todo: fucking filesystem wrangling
garland_ds_file_name = 'garland_data_set.csv'
garland_set = '../../../data_sets/garland_data_set.csv'
pravoka_set = '../../../data_sets/pravoka_data_set.csv'

'''
Scribe class is essentially a kafka consumer which writes to a data set
'''
class Scribe(KafkaNexus):

    def __init__(self, file_path, file_name):
        super().__init__(topics.em_to_ds, None)
        self.file_path = file_path + file_name
        self.write_count = 0

    # TODO: find way to count messages on topic without having a continuously running consumer
    def count_messages_on_topic(self):
        count = 0

    def read_messages_from_topic(self, use_raw=True):
        print(f'Writing messages from {self.stream_from} to {self.file_path}')
        for message in self.consumer:
            pixel_list = self.decode_and_normalize_message(message)
            if use_raw:
                self.write_data_to_file(pixel_list)

    def write_data_to_file(self, data):
        with open(self.file_path, 'at') as csv_file:
            output_writer = csv.writer(csv_file, delimiter=',')
            output_writer.writerow(data)
            self.write_count += 1

            print(f'wrote {self.write_count} rows to file {self.file_path}')

    def present_file_data(self):
        csv_file = open(self.file_path)
        rows = csv.reader(csv_file)
        count = 0
        for row in rows:
            count += 1
            if count % 100 == 0:
                print(row)
        print(f'file {self.file_path} has {count} data points contained')

'''
File extractor class built with use case being to get all data from a csv, then split this data into a train and test
set. This class also had some static methods for pickling data
'''
class FileExtractor:

    def __init__(self, file_name, full_screen=True):
        self.file_name = file_name
        self.csv_file = open(self.file_name)
        self.full_screen = full_screen
        # self.csv_rows = None

    # def get_csv_rows(self):
    #     return csv.reader(self.csv_file)

    def extract_pixel_data_from_file(self):
        # todo: encapuslate timekeeping
        print(f'starting extract_pixel_data_from_file. Full screen representation: {self.full_screen}')
        start_time = time.time()
        # self.csv_rows = self.get_csv_rows()
        count = 0
        all_rows = []
        for row in csv.reader(self.csv_file):
            count += 1
            if self.full_screen:
                screen_representation = pixel_grid_builder.get_pixel_row_representation(row)
                if len(screen_representation) <= 224:
                    # Convert to float and normalize as a very small number, as Neural nets use these.
                    all_rows.append(screen_representation.astype('float32') / 64.0)
            else:
                pixel_grid = pixel_grid_builder.create_pixel_grid(row)
                frame = np.zeros(pixel_grid.shape[:2])
                it = np.nditer(frame, flags=['multi_index'])
                while not it.finished:
                    y, x = it.multi_index
                    all_rows.append(pixel_grid[y-1, x-1].astype('float32') / 64.0)
                    it.iternext()
        print(f'checked total of {count} rows; found {len(all_rows)} usable data points in time of {time.time() - start_time}')
        return all_rows

    '''
    Train/test split methods. Almost certainly should be in own class
    '''
    def get_train_and_test_sets_with_labels(self):
        print(f'getting training and test set with labels from {self.file_name}')
        start_time = time.time()
        data_points = self.extract_pixel_data_from_file()

        labels = [random.randint(0, 2) for i in range(len(data_points))]
        train_set, test_set, train_labels, test_labels = train_test_split(data_points, labels)

        train_set = np.expand_dims(train_set, -1)
        test_set = np.expand_dims(test_set, -1)
        train_labels = np.expand_dims(train_labels, -1)
        test_labels = np.expand_dims(test_labels, -1)
        print(f'Divided total data set into training/test data and labels in time of {time.time() - start_time}')
        return train_set, test_set, np.array(train_labels), np.array(test_labels)

    def get_train_and_test_sets(self):
        print(f'getting training and test set from {self.file_name}')
        start_time = time.time()
        data_points = self.extract_pixel_data_from_file()
        train_set, test_set = train_test_split(data_points)
        train_set = np.expand_dims(train_set, -1)
        test_set = np.expand_dims(test_set, -1)
        print(f'Divided total data set into training/test sets in time of {time.time() - start_time}')

        return train_set, test_set


'''
pickling methods.
'''
def pickle_set(data_set, file_name):
    pickle.dump(data_set, open(file_name, 'wb'))


def unpickle_set(file_path):
    start_time = time.time()
    print(f'CWD in unpickle_set: {os.getcwd()}')
    train, test = pickle.load(open(file_path, 'rb'))
    print(f'{file_path}.p unpickled in {time.time() - start_time}')
    return train, test


def get_and_pickle_grid_data_set():
    x = FileExtractor(full_screen=False)
    train, test = x.get_train_and_test_sets()
    pickle_set((train, test), '../../../data_sets/pickles/grid_square_pickle.p')

'''
can create a class, Charon, which moves files to and from the cloud
'''