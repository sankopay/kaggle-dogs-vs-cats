#!/usr/bin/env python
from pylearn2.models import mlp
from pylearn2.costs.mlp.dropout import Dropout
from pylearn2.training_algorithms import sgd, learning_rule
from pylearn2.termination_criteria import EpochCounter
from pylearn2.datasets import DenseDesignMatrix
from pylearn2.train import Train
from pylearn2.train_extensions import best_params, window_flip
from pylearn2.space import VectorSpace
import pickle
import numpy as np
from sklearn.cross_validation import train_test_split


def to_one_hot(l):
    out = np.zeros((len(l), len(set(l))))
    for n, i in enumerate(l):
        out[n, i] = 1.
    return out

x = pickle.load(open('saved_x.pkl', 'rb'))
y = pickle.load(open('saved_y.pkl', 'rb'))
y = to_one_hot(y)
in_space = VectorSpace(dim=x.shape[1])
full = DenseDesignMatrix(X=x, y=y)

l1 = mlp.RectifiedLinear(layer_name='l1',
                         irange=.001,
                         dim=5000,
                         max_col_norm=1.)

l2 = mlp.RectifiedLinear(layer_name='l2',
                         irange=.001,
                         dim=5000,
                         max_col_norm=1.)

l3 = mlp.RectifiedLinear(layer_name='l3',
                         irange=.001,
                         dim=5000,
                         max_col_norm=1.)

output = mlp.HingeLoss(n_classes=2,
                       layer_name='y',
                       irange=.0001)

layers = [l1, l2, l3, output]

mdl = mlp.MLP(layers,
              input_space=in_space)

lr = .001
epochs = 100
trainer = sgd.SGD(learning_rate=lr,
                  batch_size=128,
                  learning_rule=learning_rule.Momentum(.5),
                  # Remember, default dropout is .5
                  cost=Dropout(input_include_probs={'l1': .8},
                               input_scales={'l1': 1.}),
                  termination_criterion=EpochCounter(90),
                  monitoring_dataset={'train': full})

watcher = best_params.MonitorBasedSaveBest(
    channel_name='train_y_misclass',
    save_path='saved_clf.pkl')

decay = sgd.LinearDecayOverEpoch(start=1,
                                 saturate=100,
                                 decay_factor=.05 * lr)

experiment = Train(dataset=full,
                   model=mdl,
                   algorithm=trainer,
                   extensions=[watcher,decay])

experiment.main_loop()
