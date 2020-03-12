"""
Altered version of Guo et. al's code, which can be found here: https://github.com/XifengGuo/DCEC/blob/master/ConvAE.py

The main model class of the DCEC model
"""
# Suppress warnings
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from tensorflow.keras.models import Model
    from tensorflow import keras
from time import time
import numpy as np
from sklearn.cluster import KMeans
# from . import metrics
from .convolutional_auto_encoder import ConvolutionalAutoEncoder
import csv
import os
from .clustering_layer import ClusteringLayer


class DeepConvolutionalEmbeddedClustering(object):

    def __init__(self, input_shape, n_clusters, filters, is_prototype, alpha=1.0):

        super(DeepConvolutionalEmbeddedClustering, self).__init__()

        # Set hyperparameters
        self.n_clusters = n_clusters
        self.input_shape = input_shape
        self.alpha = alpha
        self.y_pred = []
        self.is_prototype = is_prototype

        self.intermittent_save_dir = './results/temp'

        '''
        build the model
        
        A visual representation would help to clarify the shape this model took
        '''
        self.cae = ConvolutionalAutoEncoder(input_shape, filters).model
        hidden = self.cae.get_layer(name='embedding').output
        self.encoder = Model(inputs=self.cae.input, outputs=hidden)
        # todo: determine how syntac passing in `hidden` works
        clustering_layer = ClusteringLayer(self.n_clusters, name='clustering')(hidden)
        self.model = Model(inputs=self.cae.input, outputs=[clustering_layer, self.cae.output])
        if self.is_prototype:
            keras.utils.plot_model(self.model, 'dcec.png', show_shapes=True)


    def pretrain(self, x, batch_size=256, epochs=200, save_file_name='pretrain_cae_model.h5'):
        print('---Pretraining CAE---')
        self.cae.compile(optimizer='adam', loss='mse')
        # todo: implement logging
        # from tensorflow.keras.callbacks import CSVLogger
        # csv_logger = CSVLogger(args.save_dir + '/pretrain_log.csv')

        # begin training
        t0 = time()
        self.cae.fit(x, x, batch_size=batch_size, epochs=epochs)

        print('Pre-training time: ', time() - t0)
        self.cae.save(save_file_name)
        print(f'Pretrained weights are saved to {save_file_name}')
        self.pretrained = True


    def load_weights(self, weights_path):
        self.model.load_weights(weights_path)

    def extract_feature(self, x):  # extract features from before clustering layer
        return self.encoder.predict(x)

    def predict(self, x):
        q, _ = self.model.predict(x, verbose=0)
        return q.argmax(1)

    @staticmethod
    def target_distribution(q):
        # todo: illustrate how the data is transformed by this
        weight = q ** 2 / q.sum(0)
        return (weight.T / weight.sum(1)).T

    '''
    kld = Kullback-Leibler divergence
    mse = mean square error
    '''
    def compile(self, loss=['kld', 'mse'], loss_weights=[1, 1], optimizer='adam'):
        self.model.compile(loss=loss, loss_weights=loss_weights, optimizer=optimizer)

    '''
    Fits the model to training data passed in
    '''
    def fit(self,
            x,
            y=None,
            batch_size=256,
            maxiter=2e4,
            tol=1e-3,
            update_interval=140,
            save_file_name='dcec_model_final.h5'
            ):

        if self.cae is None:
            raise Exception('DCEC must have a CAE. One must be pretrained or loaded')

        print('Update interval', update_interval)
        '''
        can probably replace this with a rapid_prototype variable on the class level
        '''
        if self.is_prototype:
            save_interval = x.shape[0] / batch_size * 5
            print(f'Save interval: {save_interval}')

        # Step 1: pretrain if necessary
        # t0 = time()
        # if not self.pretrained and cae_weights is None:
        #     print('pretraining CAE using default hyper-parameters: optimizer=\'adam\' | epochs=200')
        #     self.pretrain(x, batch_size, save_dir=save_dir)
        #     self.pretrained = True
        # elif cae_weights is not None:
        #     self.cae.load_weights(cae_weights)
        #     print('cae_weights is loaded successfully.')

        # Step 2: initialize cluster centers using k-means
        t1 = time()
        print('Initializing cluster centers with k-means.')
        kmeans = KMeans(n_clusters=self.n_clusters, n_init=20)
        # self is the current y_pred(iction?), y_pred_last holds previous y_pred value
        self.y_pred = kmeans.fit_predict(self.encoder.predict(x))
        y_pred_last = np.copy(self.y_pred)
        # using the cluster centers as weights for models in the model's clustering layer
        self.model.get_layer(name='clustering').set_weights([kmeans.cluster_centers_])
        print(f'finished initializing cluster centers in {time() - t1}')

        # Step 3: deep clustering
        # todo: implement logging
        if not self.is_prototype:
            if not os.path.exists(self.intermittent_save_dir):
                os.makedirs(self.intermittent_save_dir)
            logfile = open(self.intermittent_save_dir + '/dcec_log.csv', 'w')
            logwriter = csv.DictWriter(logfile, fieldnames=['iter', 'acc', 'nmi', 'ari', 'L', 'Lc', 'Lr'])
            logwriter.writeheader()

        loss = [0, 0, 0]
        index = 0
        loop_time = time()
        for ite in range(int(maxiter)):
            it_time = time()
            if ite % update_interval == 0:
                # how exactly this prediction works is completely unknown
                q, _ = self.model.predict(x, verbose=0)
                p = self.target_distribution(q)  # update the auxiliary target distribution p

                # evaluate the clustering performance
                '''
                Get a prediction
                '''
                self.y_pred = q.argmax(1)

                # todo: implement metrics (and decide how to deal with Guo et al's metrics
                if y is not None and not self.is_prototype:
                    acc = np.round(metrics.acc(y, self.y_pred), 5)
                    nmi = np.round(metrics.nmi(y, self.y_pred), 5)
                    ari = np.round(metrics.ari(y, self.y_pred), 5)
                    loss = np.round(loss, 5)
                    logdict = dict(iter=ite, acc=acc, nmi=nmi, ari=ari, L=loss[0], Lc=loss[1], Lr=loss[2])
                    logwriter.writerow(logdict)
                    print('Iter', ite, ': Acc', acc, ', nmi', nmi, ', ari', ari, '; loss=', loss)

                '''
                check stop criterion
                
                could for sure use a stronger understanding of bow the stop criteria works. what exactly is the 
                tolerance threshold a measure of?
                
                When fitting against data set using local machine, found that it took well under the 20K ceiling to
                have the tolerance threshold end fitting. My memory says 500, but I don't trust this memory.
                
                Also points to my lack of a logging strategy.
                '''
                delta_label = np.sum(self.y_pred != y_pred_last).astype(np.float32) / self.y_pred.shape[0]
                y_pred_last = np.copy(self.y_pred)
                if ite > 0 and delta_label < tol:
                    print(f'delta_label {delta_label} < tol {tol}')
                    print('Reached tolerance threshold. Stopping training.')
                    logfile.close()
                    break

            '''
            if the next index times the batch size is larger than the shape of the first x

            Alters manner in which x & y params for train_on_batch are selected
            '''
            if (index + 1) * batch_size > x.shape[0]:
                loss = self.model.train_on_batch(x=x[index * batch_size::],
                                                 y=[p[index * batch_size::], x[index * batch_size::]])
                index = 0
            else:
                loss = self.model.train_on_batch(x=x[index * batch_size:(index + 1) * batch_size],
                                                 y=[p[index * batch_size:(index + 1) * batch_size],
                                                    x[index * batch_size:(index + 1) * batch_size]
                                                    ])
                index += 1

            # TODO: logging & strategy for saving model
            if not self.is_prototype and ite % save_interval == 0:
                # save DCEC model checkpoints
                print('saving model to:', self.intermittent_save_dir + '/dcec_model_' + str(ite) + '.h5')
                self.model.save_weights(self.intermittent_save_dir + '/dcec_model_' + str(ite) + '.h5')

            print(f'Iteration {ite} complete in time of {time() - it_time}, total loop time{time() - loop_time}')
            ite += 1

        # save the trained model
        logfile.close()
        print(f'saving model to: {save_file_name}')
        self.model.save(save_file_name)
        print(f'Clustering time: {time() - t1}')
        print(f'Total time: {time() - t1}')


if __name__ == '__main__':
    dcec = DeepConvolutionalEmbeddedClustering(input_shape=(224, 256, 1), n_clusters=5, filters=[32, 64, 128, 5], is_prototype=True)
    # dcec.pretrain()