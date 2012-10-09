"""
A theano / pylearn2 wrapper for cuda-convnet's convFilterActs function.
"""
__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"

"""
This module may contain code copied directly or modified from cuda-convnet.
The copyright and licensing notice for this code is reproduced below:


/*
 * Copyright (c) 2011, Alex Krizhevsky (akrizhevsky@gmail.com)
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

"""

from theano.sandbox.cuda import GpuOp
from theano.sandbox.cuda import CudaNdarrayType
from theano.gof import Apply
from pylearn2.sandbox.cuda_convnet.shared_code import get_NVMatrix_code
from pylearn2.sandbox.cuda_convnet.shared_code import get_filter_acts_code

class FilterActs(GpuOp):
    """
    2D convolution implemented on GPU.

    This is intended to be a very low-level, performance oriented op.

    It will not try to fix the input for you. That would slow it down.
    The input must be in the right format. If not, it raises an exception.

    Currently, this op must be inserted manually, not by optimizations.


    images:          (channels, rows, cols, batch_size)
    filters:         (input channels, filter rows, filter cols, output channels)
                     rows must be the same as cols

    output:         (output channels, output rows, output cols, batch size)

    Note: all of these convolution routines are optimized for the case when
    the number of images (i.e. the minibatch size) is a multiple of 128.
    Other batch sizes will work, but Alex made no attempt whatsoever
    to make them work fast.
    """

    def __init__(self):
        self.pad = 0 # TODO: support other amounts of padding

    def make_node(self, images, filters):

        if not isinstance(images.type, CudaNdarrayType):
            raise TypeError("FilterActs: expected images.type to be CudaNdarrayType, "
                    "got "+str(images.type))

        if not isinstance(filters.type, CudaNdarrayType):
            raise TypeError("FilterActs: expected filters.type to be CudaNdarrayType, "
                    "got "+str(filters.type))


        channels_broadcastable = filters.type.broadcastable[3]
        batch_broadcastable = images.type.broadcastable[3]
        # Computing whether the rows and columns are broadcastable requires doing
        # arithmetic on quantities that are known only at runtime, like the specific
        # shape of the image and kernel
        rows_broadcastable = False
        cols_broadcastable = False

        targets_broadcastable = (channels_broadcastable, rows_broadcastable,
                cols_broadcastable, batch_broadcastable)
        targets_type = CudaNdarrayType(broadcastable=targets_broadcastable)
        targets = targets_type()

        return Apply(self, [images, filters], [targets])

    def c_support_code(self):

        rval = get_NVMatrix_code()
        rval += get_filter_acts_code()

    def c_code(self, node, name, inputs, outputs, sub):

        images, filters = inputs
        targets, = outputs
        fail = sub['fail']

        # convFilterActs will multiply targets by scaleTargets
        # then add scaleOutput * (the convolution value)
        # We could make use of this to implement an inplace
        # addconv op but for this op we just want to compute
        # the convolution so we set them to 0 and 1 respectively
        # Note: there is another version of convFilterActs that
        # does not take these arguments, but it is just a wrapper
        # around the version that does take them, so we save
        # a function call by using the version that we use.
        basic_setup = """
        #define scaleTargets 0
        #define scaleOutput 1
        """

        # The amount of braces that must be closed at the end
        num_braces = 0

        setup_nv_images = """
        if (%(images)s->nd != 4)
        {
            PyErr_Format(PyExc_ValueError,
                "required nd=4, got nd=%%i, %(images)s->nd);
            %(fail)s;
        }

        { //setup_nv_images brace 1
        const int * images_dims = CudaNdarray_HOST_DIMS(images);
        const int img_channels = images_dims[0];
        const int imgSizeY = images_dims[1];
        const int imgSizeX = images_dims[2];
        const int batch_size = images_dims[3];

        """
        num_braces += 1


        raise NotImplementedError("""
        TODO:
        1) set up nv_images.
        2) set up nv_filters.
            check that rows == cols
            "(numFiltersColors, filterPixels, numFilters)"
        3) set up nv_targets
        """)

        # note: imgSizeX is not specified here, it is computed internally
        # (in _filterActsSparse) by the lines:
        # int imgPixels = images.getNumRows() / numImgColors;
        # int imgSizeX = imgPixels / imgSizeY;
        #
        # note: numFilters is not specified here. it is determined by
        # nv_filters.getNumCols()
        #
        # note: the size of the filters is determined by dividing
        # nv_filters.getNumRows() by numFilterColors
        #
        do_convolution = """
        convFilterActs(nv_images, nv_filters, nv_targets,
                       imgSizeY, numModulesY, numModulesX,
                       paddingStart, moduleStride, numImgColors,
                       numGroups, scaleTargets, scaleOutput);
        """

        braces = '}' * num_braces

        rval = basic_setup + \
                setup_nv_images + \
                do_convolution + \
                braces

        return rval

