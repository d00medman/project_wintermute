"""
Code in this file was used to build a "black box" trainable algorithm. Was more concerned here with the I/O process
needed to get data into a model which could be compiled and fit
"""
from archived_files.melete_prototype.pipeline_components import FileExtractor
# Suppress warnings
import warnings
import time
from datetime import datetime
from pathlib import Path
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models

    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)
# import numpy as np

# TODO: encapsulate in class


def build_model():
    # Sequential model is a stack of layers
    model = models.Sequential()
    '''
    channels = output channels

    first argument is filters. tutorial has 32. Unsure of why or how many to choose, so picking. controls number of output channels?

    second argument is kernel_sizxe. Specifies size of 2d convolutional window. What is a convolutional window? I am inputting the entire screen as a kernel size. Is this a good idea?
    if the kernel is just a bunch of filters, I'm not sure a filter encoumpassing the whole screen works necessarily

    input_shape argument because this is the first layer and this is apparently needed. Should be noted that this is of the same size as the kernels (at least as I currently have them set up)
    '''
    model.add(layers.Conv2D(32, 16, strides=8, activation='relu', input_shape=(224, 256, 1)))
    '''
    not even remotely certain of how this works, but for sure need to beef up knowledge on what exactly is being passed here
    '''
    model.add(layers.MaxPooling2D((2, 2)))

    '''
    after this comes the densely connected layer. totally uncertain of what this will look like. appears to be another keras feature
    hmm picking 16x16 convolutional filter 
    '''
    model.add(layers.Flatten())
    model.add(layers.Dense(32, activation='relu'))
    '''
    last layer, only really needs to ID battle screen, navigation screen and menu screens
    '''
    model.add(layers.Dense(3, activation='softmax'))

    model.summary()

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train_model(file_name='melete.h5'):
    print(f'starting to train model to output to {file_name}')
    start_time = time.time()
    logdir = '/home/ajmollohan/project_wintermute/data_sets/graph_logs' + datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)

    training_set, testing_set, training_labels, testing_labels = FileExtractor().get_train_and_test_sets_with_labels()
    model = build_model()
    model.fit(
        training_set,
        training_labels,
        epochs=10,
        validation_data=(testing_set, testing_labels),
        callbacks=[tensorboard_callback]
    )

    model.save(file_name)
    print(f'model trained and saved in {time.time() - start_time}')


def get_trained_model():
    # TODO: figure out how to handle file interaction within Wintermute
    full_path = '/home/ajmollohan/project_wintermute/wintermute/core/melete/trained_model.h5'
    print(Path.cwd())
    # part_path = '/melete/trained_model.h5'
    model = tf.keras.models.load_model(full_path)
    print('loaded trained model')
    model.summary()
    return model


if __name__ == '__main__':
    train_model()
    # get_trained_model()
#     start_time = time.time()
#     train_model()
#     print(f'model trained and saved in {time.time() - start_time}')
