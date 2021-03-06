# -*- coding: utf-8 -*-
#/usr/bin/python2
'''
By kyubyong park. kbpark.linguist@gmail.com. 
https://www.github.com/kyubyong/deepvoice3
'''

from __future__ import print_function

import os

from scipy.io.wavfile import write

from hyperparams import Hyperparams as hp
import numpy as np
import tensorflow as tf
from train import Graph
from utils import spectrogram2wav
from data_load import load_test_data

def synthesize():
    # Load graph
    g = Graph(is_training=False); print("Graph loaded")
    x = load_test_data

    with g.graph.as_default():
        sv = tf.train.Supervisor()
        with sv.managed_session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            # Restore parameters
            sv.saver.restore(sess, tf.train.latest_checkpoint(hp.logdir))
            print("Restored!")
             
            # Get model
            mname = open(hp.logdir + '/checkpoint', 'r').read().split('"')[1] # model name

            # Inference
            mels = np.zeros((hp.batch_size, hp.T_y//hp.r, hp.n_mels*hp.r), np.float32)
            for j in range(hp.T_x):
                _mels = sess.run(g.mels, {g.x: x, g.y: mels})
                mels[:, j, :] = _mels[:, j, :]
            mags = sess.run(g.mags, {g.mels: mels})

    # Generate wav files
    if not os.path.exists(hp.sampledir): os.makedirs(hp.sampledir)
    for i, mag in enumerate(mags):
        # generate wav files
        mag = mag*hp.mag_std + hp.mag_mean # denormalize
        audio = spectrogram2wav(mag)
        write(hp.sampledir + "/{}_{}.wav".format(mname, i), hp.sr, audio)
                                          
if __name__ == '__main__':
    synthesize()
    print("Done")
    
    
