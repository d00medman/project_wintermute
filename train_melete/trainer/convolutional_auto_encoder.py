"""
Altered version of Guo et. al's code, which can be found here: https://github.com/XifengGuo/DCEC/blob/master/ConvAE.py

A convolutional autoencoder whose encoding layer will be used to generate Wintermute's DCEC model; meant to be used for
perception of game state.
"""

from tensorflow.keras.layers import Conv2D, Conv2DTranspose, Dense, Flatten, Reshape
from tensorflow.keras.models import Sequential
from time import time

print('Hit CAE model file')

grid_square_shape = (16, 16, 1)
whole_screen_shape = (224, 256, 1)


class ConvolutionalAutoEncoder:

    def __init__(self, input_shape=grid_square_shape, filters=(32, 64, 128, 3), display_summary=True):
        self.model = build_model(input_shape=input_shape, filters=filters, display_summary=display_summary)


def build_model(input_shape, filters, display_summary):
    start_time = time()
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
    # This layer to be used by DCEC. keras might actually just have embedding layers
    model.add(Dense(units=filters[3], name='embedding'))

    y_dimension_size = int(input_shape[0] / 8)
    x_dimension_size = int(input_shape[1] / 8)
    model.add(Dense(units=filters[2]*y_dimension_size*x_dimension_size, activation='relu'))
    # interestingly enough, the reshape layer built w/the assumption that dimensions are the same regardless
    model.add(Reshape((y_dimension_size, x_dimension_size, filters[2])))

    model.add(Conv2DTranspose(filters[1], 3, strides=2, padding=pad3, activation='relu', name='deconv3'))
    model.add(Conv2DTranspose(filters[0], 5, strides=2, padding='same', activation='relu', name='deconv2'))
    model.add(Conv2DTranspose(input_shape[2], 5, strides=2, padding='same', name='deconv1'))

    if display_summary:
        print(f'Model finished building after {time() - start_time}')
        model.summary()
    return model
