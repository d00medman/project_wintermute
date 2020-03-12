"""
Altered version of Guo et. al's code, which can be found here: https://github.com/XifengGuo/DCEC/blob/master/ConvAE.py

A convolutional autoencoder whose encoding layer will be used to generate Wintermutes DCEC model; meant to be used for
perception of game state.
"""

import os
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, Dense, Flatten, Reshape
from tensorflow.keras.models import Sequential
from time import time
# from keras.utils.vis_utils import plot_model
# import numpy as np
from archived_files.melete_prototype.pipeline_components import FileExtractor

grid_square_shape = (16, 16, 1)
whole_screen_shape = (224, 256, 1)

# filters represents input shape of layers
def ConvolutionalAutoEncoder(input_shape=grid_square_shape, filters=(32, 64, 128, 3), display_summary=False):
    # sequential, which makes sense as this is a series of layers
    model = Sequential()
    # Why 8? How were these numbers chosen? Almost certainly linked to
    if input_shape[0] % 8 == 0:
        pad3 = 'same'
    else:
        pad3 = 'valid'
    model.add(Conv2D(filters[0], 5, strides=2, padding='same', activation='relu', name='conv1', input_shape=input_shape))

    model.add(Conv2D(filters[1], 5, strides=2, padding='same', activation='relu', name='conv2'))

    model.add(Conv2D(filters[2], 3, strides=2, padding=pad3, activation='relu', name='conv3'))

    model.add(Flatten())
    # This layer to be used by DCEC
    model.add(Dense(units=filters[3], name='embedding'))

    y_dim = int(input_shape[0] / 8)
    x_dim = int(input_shape[1] / 8)
    model.add(Dense(units=filters[2]*y_dim*x_dim, activation='relu'))

    # interestingly enough, the reshape layer built w/the assumption that dimensions are the same regardless
    model.add(Reshape((y_dim, x_dim, filters[2])))
    model.add(Conv2DTranspose(filters[1], 3, strides=2, padding=pad3, activation='relu', name='deconv3'))

    model.add(Conv2DTranspose(filters[0], 5, strides=2, padding='same', activation='relu', name='deconv2'))

    model.add(Conv2DTranspose(input_shape[2], 5, strides=2, padding='same', name='deconv1'))

    if display_summary:
        print('summary in CAE constructor')
        model.summary()
    return model

if __name__ == "__main__":
    data_path = os.path.join(os.getcwd(), '../train_and_test.p')
    train, test = FileExtractor.unpickle_set('../train_and_test.p')
    # Build and compile model
    cae = ConvolutionalAutoEncoder(input_shape=whole_screen_shape, display_summary=True)
    cae.compile(optimizer='adam', loss='mse')
    # fit model
    start = time()
    cae.fit(train, test, batch_size=256, epochs=5)
    print(f'Model finished fitting after {time() - start}')