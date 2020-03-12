"""
Utility functions.

Functions for file handling on the cloud

Functions for consolidating and organizing command line arguments
"""

import os
import subprocess
import pickle
import argparse
import collections

staging_gcs_bucket = 'gs://wintermute_perception_staging'
HyperParameters = collections.namedtuple(
    'HyperParameters',
    'maxiter tolerance clusters epochs filters update_interval batch_size',
)

PathComponents = collections.namedtuple(
    'PathComponents',
    'cloud_bucket data_set dcec_output_file cae_file_name'
)


# GCS interaction methods
def download_files_from_gcs(gcs_bucket, data_set):
    move_files_in_gcs(gcs_bucket, os.getcwd(), data_set, 'Train and Test data set')
    train, test = pickle.load(open(data_set, 'rb'))
    return train, test


def move_files_in_gcs(move_from_dir, move_to_dir, file_name, description):
    move_from_path = os.path.join(move_from_dir, file_name)
    move_to_path = os.path.join(move_to_dir, file_name)
    print(f'Moving {description} from {move_from_path} to {move_to_path}')
    subprocess.check_call(['gsutil', 'cp', move_from_path, move_to_path])


# Arg parsing methods
def get_args():
    parser = argparse.ArgumentParser()
    # Control flow
    parser.add_argument(
        '--algorithm',
        default='dcec',
        type=str,
        help='Are we training a DCEC or a CAE?',
        choices=['cae', 'dcec']
    )
    parser.add_argument(
        '--type',
        type=str,
        default='f',
        choices=['f', 'g'],
        help='Should this be trained using whole screen representations (f) or grid square representations (g)?'
    )
    parser.add_argument(
        '--pretrain',
        default=True,
        type=bool,
        help='When training a DCEC model, do we want to pretrain the CAE'
    )
    parser.add_argument(
        '--prototyping',
        default=True,
        type=bool,
        help='Is this to test the training process end to end or are we trying to stable train a model?'
    )
    '''
    Hyperparameters.

    maybe use named tuple to reduce complexity here?
    '''
    parser.add_argument(
        '--maxiter',
        default=20000,
        type=int,
        help='DCEC hyperparameter: maximum number of iterations which DCEC will run on'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.0001,
        help='DCEC hyperparameter: when loss dips below this, DCEC training concludes'
    )
    parser.add_argument(
        '--clusters',
        type=int,
        default=2,
        help='DCEC hyperparameter: How many clusters should DCEC separate?'
    )
    parser.add_argument(
        '--update-interval',
        default=140,
        type=int,
        help='DCEC hyperparameter: How often the cluster centers get updated (not positive though)'
    )
    parser.add_argument(
        '--epochs',
        default=200,
        type=int,
        help='CAE hyperparameter: how many epochs to train the CAE on'
    )
    parser.add_argument(
        '--batch-size',
        default=256,
        type=int,
        help='CAE hyperparameter: Batch size for gradient descent (still not positive)'
    )

    # logging - fairly certain this is GCP output
    parser.add_argument(
        '--verbosity',
        choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN'],
        default='INFO'
    )
    '''
    File system params. These were the source of considerable headache in my last push.

    Can probably toss them in a named tuple?

    squeamish about default values. Present risk of overwriting relevant extant models
    '''
    parser.add_argument(
        '--cloud-bucket',
        type=str,
        default='gs://wintermute_perception_staging',
        help='gcs bucket which we will get data from and save results to'
    )
    parser.add_argument(
        '--data-set',
        type=str,
        default='train_and_test.p',
        help='train and test data to be imported'
    )
    parser.add_argument(
        '--dcec-output-file',
        type=str,
        default='cloud_trained_dcec.h5',
        help='The name of the file which will be output after training a DCEC model'
    )
    parser.add_argument(
        '--cae-file-name',
        type=str,
        default='cloud_trained_cae.h5',
        help='If pretraining, the name of the trained CAE file which will be saved; else, an already learned CAE model'
    )

    args, _ = parser.parse_known_args()
    print(f'Following arguments were recieved from the command line: {args}')
    return args


def package_args(args):
    hyper_parameters = HyperParameters(
        maxiter=args.maxiter,
        tolerance=args.tolerance,
        epochs=args.epochs,
        clusters=args.clusters,
        filters=[32, 64, 128, args.clusters],
        update_interval=args.update_interval,
        batch_size=args.batch_size
    )

    scope_prefix = 'f_' if args.type == 'f' else 'g_'
    path_components = PathComponents(
        cae_file_name=scope_prefix + args.cae_file_name,
        cloud_bucket=args.cloud_bucket,
        data_set=args.data_set,
        dcec_output_file=scope_prefix + args.dcec_output_file
    )
    return hyper_parameters, path_components


if __name__ == '__main__':
    move_files_in_gcs(os.getcwd(), staging_gcs_bucket, 'grid_square_pickle.p', 'Grid square pickle data file')