"""
Script to perform periodic data acquisition with the PS5000a and save the results to csv files.

By: Alex Omid-Zohoor 
"""
from __future__ import division
from __future__ import absolute_import
#from __future__ import print_function
from __future__ import unicode_literals

import time
from picoscope import ps5000a
import pylab as plt
import numpy as np
import json
import sys
import os
import csv

#globals
PARAMETER_FILE_PATH = './picoscopeCapture.json'
OUTPUT_PATH = '.'
OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
OUTPUT_WAVEFORMS_FILE_EXTENSION = '.csv'

def str2bool(inputString):
    if inputString.lower() == 'true':
        return True
    elif inputString.lower() == 'false':
        return False
    else:
        raise Exception('Error. All boolean parameters must either be \'True\' or \'False\'')

if __name__ == "__main__":
    print(__doc__)

    if len(sys.argv) == 2:
        PARAMETER_FILE_PATH = sys.argv[1]
    elif len(sys.argv) == 3:
        PARAMETER_FILE_PATH = sys.argv[1]
        OUTPUT_PATH = sys.argv[2]

    #parse parameter file
    with open(PARAMETER_FILE_PATH) as f:
        parameterMap = json.load(f)

    acquireChannelA = str2bool(parameterMap['channelAcquisition']['channelA'])
    acquireChannelB = str2bool(parameterMap['channelAcquisition']['channelB'])
    acquireChannelC = str2bool(parameterMap['channelAcquisition']['channelC'])
    acquireChannelD = str2bool(parameterMap['channelAcquisition']['channelD'])

    adcResolution = parameterMap['acquisitionSettings']['adcResolution']
    samplingInterval = float(parameterMap['acquisitionSettings']['samplingInterval'])
    duration = float(parameterMap['acquisitionSettings']['duration'])

    numCycles = float(parameterMap['cycleSettings']['numCycles'])
    cycleDuration = float(parameterMap['cycleSettings']['cycleDuration'])

    triggerSource = parameterMap['triggerSettings']['trgSrc']
    triggerThresholdVoltage = float(parameterMap['triggerSettings']['threshold_V'])
    triggerDirection = parameterMap['triggerSettings']['direction']
    triggerDelay = int(parameterMap['triggerSettings']['delay'])
    triggerTimeoutMs = int(parameterMap['triggerSettings']['timeout_ms'])
    triggerEnabled = str2bool(parameterMap['triggerSettings']['enabled'])

    channelACoupling = parameterMap['channelA']['coupling']
    channelAVRange = float(parameterMap['channelA']['VRange'])
    channelAVOffset = float(parameterMap['channelA']['VOffset'])
    channelAEnabled = str2bool(parameterMap['channelA']['enabled'])
    channelABWLimited = str2bool(parameterMap['channelA']['BWLimited'])
    channelAProbeAttenuation = float(parameterMap['channelA']['probeAttenuation'])

    channelBCoupling = parameterMap['channelB']['coupling']
    channelBVRange = float(parameterMap['channelB']['VRange'])
    channelBVOffset = float(parameterMap['channelB']['VOffset'])
    channelBEnabled = str2bool(parameterMap['channelB']['enabled'])
    channelBBWLimited = str2bool(parameterMap['channelB']['BWLimited'])
    channelBProbeAttenuation = float(parameterMap['channelB']['probeAttenuation'])

    channelCCoupling = parameterMap['channelC']['coupling']
    channelCVRange = float(parameterMap['channelC']['VRange'])
    channelCVOffset = float(parameterMap['channelC']['VOffset'])
    channelCEnabled = str2bool(parameterMap['channelC']['enabled'])
    channelCBWLimited = str2bool(parameterMap['channelC']['BWLimited'])
    channelCProbeAttenuation = float(parameterMap['channelC']['probeAttenuation'])

    channelDCoupling = parameterMap['channelD']['coupling']
    channelDVRange = float(parameterMap['channelD']['VRange'])
    channelDVOffset = float(parameterMap['channelD']['VOffset'])
    channelDEnabled = str2bool(parameterMap['channelD']['enabled'])
    channelDBWLimited = str2bool(parameterMap['channelD']['BWLimited'])
    channelDProbeAttenuation = float(parameterMap['channelD']['probeAttenuation'])

    #connect to picoscope
    print 'Attempting to open Picoscope 5000a...\n'
    ps = ps5000a.PS5000a()

    print 'Found the following picoscope:\n'
    print ps.getAllUnitInfo() + '\n'

    #configure picoscope for data acquisition
    (actualSamplingInterval, nSamples, maxSamples) = ps.setSamplingInterval(samplingInterval, duration)
    print 'Sampling interval = %f ns' % (actualSamplingInterval * 1E9)
    print 'Taking  samples = %d' % nSamples
    print 'Maximum samples = %d\n' % maxSamples

    #configure channels for data acquisition
    if acquireChannelA:
        channelARange = ps.setChannel('A', channelACoupling, channelAVRange, channelAVOffset, channelAEnabled, channelABWLimited, channelAProbeAttenuation)
        print 'Chosen channel A range = %d' % channelARange
    if acquireChannelB:
        channelBRange = ps.setChannel('B', channelBCoupling, channelBVRange, channelBVOffset, channelBEnabled, channelBBWLimited, channelBProbeAttenuation)
        print 'Chosen channel B range = %d' % channelBRange
    if acquireChannelC:
        channelCRange = ps.setChannel('C', channelCCoupling, channelCVRange, channelCVOffset, channelCEnabled, channelCBWLimited, channelCProbeAttenuation)
        print 'Chosen channel C range = %d' % channelCRange
    if acquireChannelD:
        channelDRange = ps.setChannel('D', channelDCoupling, channelDVRange, channelDVOffset, channelDEnabled, channelDBWLimited, channelDProbeAttenuation)
        print 'Chosen channel D range = %d' % channelDRange

    print '\n'

    #set trigger
    ps.setSimpleTrigger(triggerSource, triggerThresholdVoltage, triggerDirection, triggerTimeoutMs, triggerEnabled)

    #create unique timestamped filename
    timestr = time.strftime('%Y%m%d-%H%M%S')
    #create directory to save csv files with all channel waveforms
    outputDir = os.path.join(OUTPUT_PATH, timestr + '-picoscope-capture')
    os.mkdir(outputDir)

    cycle = 1

    #loop through data acquisition cycles
    while cycle <= numCycles:

        print 'Cycle %d:\n' % cycle

        ps.runBlock()
        ps.waitReady()
        if acquireChannelA:
            dataA = ps.getDataV('A', nSamples, returnOverflow=False)
        else:
            dataA = np.zeros(nSamples)
        if acquireChannelB:
            dataB = ps.getDataV('B', nSamples, returnOverflow=False)
        else:
            dataB = np.zeros(nSamples)
        if acquireChannelC:
            dataC = ps.getDataV('C', nSamples, returnOverflow=False)
        else:
            dataC = np.zeros(nSamples)
        if acquireChannelD:
            dataD = ps.getDataV('D', nSamples, returnOverflow=False)
        else:
            dataD = np.zeros(nSamples)

        dataTimeAxis = np.arange(nSamples) * actualSamplingInterval
        ps.stop()

        waveformsFilename = os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + '-cycle-' + str(cycle) + OUTPUT_WAVEFORMS_FILE_EXTENSION)
        fout = open(waveformsFilename, 'wb')
        writer = csv.writer(fout)
        writer.writerow(['TIME (S)', 'CHANNEL A (V)', 'CHANNEL B (V)', 'CHANNEL C (V)', 'CHANNEL D (V)'])
        for row in range(nSamples):
            rowList = [dataTimeAxis[row], dataA[row], dataB[row], dataC[row], dataD[row]]
            writer.writerow(rowList)
        fout.close()
        
        #wait before starting the next cycle. This is not the most precise way to do this, but it should be sufficient. 
        #for more precisely spaced cycles, one should write a custom script. 
        time.sleep(cycleDuration-duration)
        cycle += 1
    ps.close()
