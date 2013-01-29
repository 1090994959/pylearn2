"""
The functionality in this module is very similar to that in
pylearn2.linear.conv2d. The difference is that this module is
based on Alex Krizhevsky's cuda-convnet convolution, while
pylearn2.linear.conv2d is based on theano's 2D convolution.
This module therefore uses the axis format ('c', 0, 1, 'b')
as its native format, while the other uses ('b', 'c', 0, 1).
This module also requires the use of GPU, while the other
supports CPU.
"""
__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"


import theano.tensor as T
from pylearn2.utils import sharedX
import numpy as np
from theano.tensor.nnet.conv import conv2d
from pylearn2.linear.linear_transform import LinearTransform
import functools
import theano
from pylearn2.sandbox.cuda_convnet.filter_acts import FilterActs

class Conv2D(LinearTransform):
    """
    A pylearn2 linear operator based on 2D convolution,
    implemented using Alex Krizvhevsky's cuda-convnet library.

    """

    def __init__(self,
            filters,
            input_axes = ('c', 0, 1, 'b'),
            batch_size=None,
            output_axes = ('c', 0, 1, 'b'),
        subsample = (1, 1), border_mode = 'valid',
        filters_shape = None, message = ''):

        if subsample != (1, 1):
            raise NotImplementedError()

        if border_mode != 'valid':
            raise NotImplementedError()

        if filters_shape != None:
            raise NotImplementedError()

        if message != '':
            raise NotImplementedError()

        if batch_size != None:
            raise NotImplementedError()

        self.input_space = input_axes
        self.output_axes = output_axes

        self._filters = sharedX(filters)

    @functools.wraps(LinearTransform.get_params)
    def get_params(self):
        return [self._filters]

    @functools.wraps(LinearTransform.get_weights_topo)
    def get_weights_topo(self, borrow=False):
        inp, rows, cols, outp = range(4)
        raw = self._filters.get_value(borrow=borrow)
        return np.transpose(raw, (outp, rows, cols, inp))

    def lmul(self, x):
        """
        dot(x, A)
        aka, do convolution with input image x

        """

        # x must be formatted as channel, topo dim 0, topo dim 1, batch_index
        # for use with FilterActs
        assert x.ndim == 4
        x_axes = self.input_axes
        assert len(x_axes) == 4

        op_axes = ('c', 0, 1, 'b')

        if tuple(x_axes) != op_axes:
            x = x.dimshuffle(*[x_axes.index(axis) for axis in op_axes])

        rval = FilterActs()(x, self._filters)

        # Format the output based on the output space
        rval_axes = self.output_axes
        assert len(rval_axes) == 4

        if tuple(rval_axes) != op_axes:
            rval = rval.dimshuffle(*[op_axes.index(axis) for axis in rval_axes])

        return rval

    def lmul_T(self, x):
        raise NotImplementedError("This method is not yet modified since copy-pasting from pylearn2.linear.conv2d")
        """ override the original Conv2D lmul_T to make it work
        with pylearn format of topological data using dimshuffles """
        assert x.dtype == self._filters.dtype

        op_axes = ('b', 'c', 0, 1)
        axes = self.output_axes
        if tuple(axes) != op_axes:
            x = x.dimshuffle(
                    axes.index('b'),
                    axes.index('c'),
                    axes.index(0),
                    axes.index(1))

        # dot(x, A.T)
        dummy_v = T.tensor4()
        dummy_v.name = 'dummy_v'

        # Since we made this variable, we need to put a tag on it
        if theano.config.compute_test_value == 'raise':
            dummy_v.tag.test_value = np.zeros((x.tag.test_value.shape[0],
                self.input_space.num_channels,
                self.input_space.shape[0],
                self.input_space.shape[1]),
                dtype = dummy_v.dtype)

        z_hs = conv2d(dummy_v, self._filters,
                image_shape=self._img_shape,
                filter_shape=self._filters_shape,
                subsample=self._subsample,
                border_mode=self._border_mode,
                )

        rval, xdummy = z_hs.owner.op.grad((dummy_v, self._filters), (x,))


        # Format the output based on the input space
        axes = self.input_space.axes
        assert len(axes) == 4

        if tuple(axes) != op_axes:
            rval = rval.dimshuffle(
                    op_axes.index(axes[0]),
                    op_axes.index(axes[1]),
                    op_axes.index(axes[2]),
                    op_axes.index(axes[3]))

        return rval

    def lmul_sq_T(self, x):
        raise NotImplementedError("This method is not yet modified since copy-pasting from pylearn2.linear.conv2d")
        """ Kind of a stupid hacky method used to support convolutional score matching.
        Ought to find a way to make _filters symbolic rather than shared.
        """
        assert x.dtype == self._filters.dtype

        op_axes = ('b', 'c', 0, 1)
        axes = self.output_axes
        if tuple(axes) != op_axes:
            x = x.dimshuffle(
                    axes.index('b'),
                    axes.index('c'),
                    axes.index(0),
                    axes.index(1))

        # dot(x, sq(A).T)
        dummy_v = T.tensor4()
        sqfilt = T.square(self._filters)
        z_hs = conv2d(dummy_v, sqfilt,
                image_shape=self._img_shape,
                filter_shape=self._filters_shape,
                subsample=self._subsample,
                border_mode=self._border_mode,
                )
        rval, xdummy = z_hs.owner.op.grad((dummy_v, sqfilt), (x,))

        # Format the output based on the input space
        axes = self.input_space.axes
        assert len(axes) == 4

        if tuple(axes) != op_axes:
            rval = rval.dimshuffle(
                    op_axes.index(axes[0]),
                    op_axes.index(axes[1]),
                    op_axes.index(axes[2]),
                    op_axes.index(axes[3]))

        return rval

    def set_batch_size(self, batch_size):
        pass


def make_random_conv2D(irange, input_space, output_space,
        kernel_shape, batch_size, \
        subsample = (1,1), border_mode = 'valid', message = "", rng = None):
    raise NotImplementedError("Not yet modified after copy-paste from "
            "pylearn2.linear.conv2d")
    """ Creates a Conv2D with random kernels """

    if rng is None:
        rng = np.random.RandomState([2012,11,6,9])

    W = sharedX( rng.uniform(-irange,irange,( output_space.num_channels, input_space.num_channels, \
            kernel_shape[0], kernel_shape[1])))

    return Conv2D(filters = W,
        batch_size = batch_size,
        input_space = input_space,
        output_axes = output_space.axes,
        subsample = subsample, border_mode = border_mode,
        filters_shape = W.get_value(borrow=True).shape, message = message)


def make_sparse_random_conv2D(num_nonzero, input_space, output_space,
        kernel_shape, batch_size, \
        subsample = (1,1), border_mode = 'valid', message = "", rng=None):
    raise NotImplementedError("Not yet modified after copy-paste from "
            "pylearn2.linear.conv2d")
    """ Creates a Conv2D with random kernels, where the randomly initialized
    values are sparse"""

    if rng is None:
        rng = np.random.RandomState([2012, 11, 6])

    W = np.zeros(( output_space.num_channels, input_space.num_channels, \
            kernel_shape[0], kernel_shape[1]))

    def random_coord():
        return [ rng.randint(dim) for dim in W.shape ]

    for i in xrange(num_nonzero):
        o, ch, r, c = random_coord()
        while W[o, ch, r, c] != 0:
            o, ch, r, c = random_coord()
        W[o, ch, r, c] = rng.randn()


    W = sharedX( W)

    return Conv2D(filters = W,
        batch_size = batch_size,
        input_space = input_space,
        output_axes = output_space.axes,
        subsample = subsample, border_mode = border_mode,
        filters_shape = W.get_value(borrow=True).shape, message = message)
