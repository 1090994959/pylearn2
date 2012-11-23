#!/bin/env python
"""
usage:

diff_monitor.py model_1.pkl model_2.pkl

Prints any difference in which set of channels were monitored,
then prints any difference in the length of the records, then
prints the first record entry at which each channel differs and
by how much.

Does not report timing differences, since these will essentially
never match.

"""
__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"


import sys
from pylearn2.utils import serial
import numpy as np

# Load the records
_, model_0_path, model_1_path = sys.argv

model_0, model_1 = [serial.load(path) for path in [model_0_path, model_1_path]]

monitor_0, monitor_1 = [model.monitor for model in [model_0, model_1]]

channels_0, channels_1 = [monitor.channels for monitor in [monitor_0, monitor_1]]

# Print the difference in which channels were monitored
intersect = []
for channel in channels_0:
    if channel not in channels_1:
        print channel+' is in model 0 but not model 1'
    else:
        intersect.append(channel)
for channel in channels_1:
    if channel not in channels_0:
        print channel+' is in model 1 but not model 0'

# Print the difference in length between the records


# Print numerical differences between the channels
record = 0
clean = intersect
while True:
    bad_channel = []
    for channel in clean:
        channel_0 = channels_0[channel]
        channel_1 = channels_1[channel]

        # Quit scanning channels that we've read all of
        if record == channel_0.length:
            bad_channel.append(channel)
            continue

        if not (channel_0.batch_record[record] ==
                channel_1.batch_record[record]):
            print channel+'.batch_record differs at record entry',record
            print '\t',channel_0.batch_record[record], 'vs', channel_1.batch_record[record]
            bad_channel.append(channel)
            continue

        if not (channel_0.example_record[record] ==
                channel_1.example_record[record]):
            print channel+'.example_record differs at record entry',record
            print '\t',channel_0.example_record[record], 'vs', channel_1.example_record[record]
            bad_channel.append(channel)
            continue

        if not (channel_0.epoch_record[record] ==
                channel_1.epoch_record[record]):
            print channel+'.epoch_record differs at record entry',record
            print '\t',channel_0.epoch_record[record], 'vs', channel_1.epoch_record[record]
            bad_channel.append(channel)
            continue

        if not np.allclose(channel_0.val_record[record],
                channel_1.val_record[record]):
            print channel+'.val_record differs at record entry',record
            print '\t',channel_0.val_record[record], 'vs', channel_1.val_record[record]
            bad_channel.append(channel)
            continue

    for channel in bad_channel:
        del clean[clean.index(channel)]
    record += 1

