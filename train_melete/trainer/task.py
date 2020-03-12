"""
contains the application logic that manages the training job.
"""

from .convolutional_auto_encoder import ConvolutionalAutoEncoder, whole_screen_shape
from . import util
from .deep_convolutional_embedded_clustering import DeepConvolutionalEmbeddedClustering
from time import time
import os


def train_dcec(
        hyper_parameters,
        path_components,
        prototype,
        pretrain=True
        ):
    gcs_bucket = path_components.cloud_bucket
    data_set = path_components.data_set
    cae_file_name = path_components.cae_file_name
    dcec_output_file = path_components.dcec_output_file

    # Download train and test data
    train, test = util.download_files_from_gcs(gcs_bucket, data_set)
    # Create model
    dcec = DeepConvolutionalEmbeddedClustering(
        input_shape=train.shape[1:],
        n_clusters=hyper_parameters.clusters,
        filters=hyper_parameters.filters,
        is_prototype=prototype
    )
    dcec.model.summary()
    dcec.compile()
    working_directory = os.getcwd()

    if pretrain:
        dcec.pretrain(
            train,
            save_file_name=cae_file_name,
            epochs=hyper_parameters.epochs
        )
        util.move_files_in_gcs(working_directory, gcs_bucket, cae_file_name, 'Pretrained CAE model')
    else:
        # Import saved CAE
        local_cae_path = os.path.join(working_directory, cae_file_name)
        util.move_files_in_gcs(gcs_bucket, working_directory, cae_file_name, 'saved CAE model')
        dcec.cae.load_weights(local_cae_path)

    # Fit the DCEC model
    dcec.fit(
        train,
        maxiter=hyper_parameters.maxiter,
        update_interval=hyper_parameters.update_interval,
        tol=hyper_parameters.tolerance,
        save_file_name=dcec_output_file,
    )
    # Mover finished model to permanent storage
    util.move_files_in_gcs(working_directory, gcs_bucket, dcec_output_file, 'Trained DCEC model')


def train_cae(epochs, cae_output_file, gcs_bucket, data_set):
    # Download Data
    train, test = util.download_files_from_gcs(gcs_bucket, data_set)
    # Build and compile model
    cae = ConvolutionalAutoEncoder(input_shape=whole_screen_shape, display_summary=True)
    cae.model.compile(optimizer='adam', loss='mse')
    # fit model
    start = time()
    cae.model.fit(train, test, batch_size=256, epochs=epochs)
    print(f'Model finished fitting after {time() - start}')
    # save finished model
    cae.model.save(cae_output_file)
    util.move_files_in_gcs(os.getcwd(), gcs_bucket, cae_output_file, 'Trained CAE model')


def main():
    print('task running')
    args = util.get_args()
    hyper_parameters, path_components = util.package_args(util.get_args())

    if args.algorithm == 'cae':
        print('training CAE in isolation')
        train_cae(args.epochs, path_components.cae_file_name, args.gcs_bucket, args.data_set)

    if args.algorithm == 'dcec':
        print('training dcec model with pretrained CAE')
        train_dcec(
            hyper_parameters,
            path_components,
            prototype=args.prototyping,
            pretrain=args.pretrain
        )


if __name__ == '__main__':
    main()
