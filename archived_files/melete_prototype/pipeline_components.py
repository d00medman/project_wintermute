import csv
import time
import pickle
import os
import wintermute.core.structure_state as pixel_grid_builder
import numpy as np
import random
from sklearn.model_selection import train_test_split
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import tensorflow as tf

garland_set = '../../../data_sets/garland_data_set.csv'
pravoka_set = '../../../data_sets/pravoka_data_set.csv'
# I think this class will probably become Thoth
class FileExtractor:

    # TODO: figure out how to handle file interaction within Wintermute
    def __init__(self, file_name=pravoka_set, full_screen=True):
        self.file_name = file_name
        self.csv_file = open(self.file_name)
        self.full_screen = full_screen
        self.csv_rows = None

    def get_csv_rows(self):
        return csv.reader(self.csv_file)

    def extract_pixel_data_from_file(self):
        print(f'starting extract_pixel_data_from_file. Full screen representation: {self.full_screen}')
        start_time = time.time()
        self.csv_rows = self.get_csv_rows()
        count = 0
        all_rows = []
        for row in self.csv_rows:
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

    # Probably worth looking into how to best pickle the output. Takes 40 seconds to get the entire output
    def get_train_and_test_sets(self):
        print(f'getting training and test set from {self.file_name}')
        start_time = time.time()
        data_points = self.extract_pixel_data_from_file()
        train_set, test_set = train_test_split(data_points)
        train_set = np.expand_dims(train_set, -1)
        test_set = np.expand_dims(test_set, -1)
        print(f'Divided total data set into training/test sets in time of {time.time() - start_time}')

        return train_set, test_set

    @staticmethod
    def pickle_set(data_set, file_name):
        pickle.dump(data_set, open(file_name, 'wb'))

    @staticmethod
    def unpickle_set(file_path):
        start_time = time.time()
        print(f'CWD in unpickle_set: {os.getcwd()}')
        train, test = pickle.load(open(file_path, 'rb'))
        print(f'{file_path}.p unpickled in {time.time() - start_time}')
        return train, test


def get_and_pickle_grid_data_set():
    x = FileExtractor(full_screen=False)
    train, test = x.get_train_and_test_sets()
    FileExtractor.pickle_set((train, test), '../../data_sets/pickles/grid_square_pickle.p')

if __name__ == '__main__':
    # get_dcec()

    train, test = FileExtractor.unpickle_set('../../data_sets/pickles/grid_square_pickle.p')
    # train, test = x.get_train_and_test_sets()
    # x.pickle_set((train, test), 'train_and_test')
    # train, test = x.unpickle_set('train_and_test')
    print(train)
