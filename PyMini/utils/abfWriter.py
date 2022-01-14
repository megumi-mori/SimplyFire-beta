import struct
import numpy as np
import pyabf
from PyMini.Backend import analyzer2


def writeABF1(ys, filename, sampleRateHz, units=['pA'], labels=['label1']):
    """
    Create an ABF1 file from scratch and write it to disk.
    Files created with this function are compatible with MiniAnalysis.
    Data is expected to be a 3D numpy array [channels, sweep, datapoint].
    """
    print(type(ys))

    assert isinstance(ys, np.ndarray)

    # constants for ABF1 files
    BLOCKSIZE = 512
    HEADER_BLOCKS = 4

    # determine dimensions of data
    channelCount = ys.shape[0]
    sweepCount = ys.shape[1]
    sweepPointCount = ys.shape[2]
    dataPointCount = sweepPointCount*sweepCount

    # predict how large our file must be and create a byte array of that size
    bytesPerPoint = 2
    dataBlocks = int(channelCount*dataPointCount * bytesPerPoint / BLOCKSIZE) + 1
    data = bytearray((dataBlocks + HEADER_BLOCKS) * BLOCKSIZE)

    # populate only the useful header data values
    struct.pack_into('4s', data, 0, b'ABF ')  # fFileSignature
    struct.pack_into('f', data, 4, 1.3)  # fFileVersionNumber
    struct.pack_into('h', data, 8, 5)  # nOperationMode (5 is episodic)
    struct.pack_into('i', data, 10, dataPointCount)  # lActualAcqLength
    struct.pack_into('i', data, 16, sweepCount)  # lActualEpisodes
    struct.pack_into('i', data, 40, HEADER_BLOCKS)  # lDataSectionPtr
    struct.pack_into('h', data, 100, 0)  # nDataFormat is 1 for float32
    struct.pack_into('h', data, 120, channelCount)  # nADCNumChannels
    struct.pack_into('f', data, 122, 1e6 / sampleRateHz)  # fADCSampleInterval
    struct.pack_into('i', data, 138, sweepPointCount)  # lNumSamplesPerEpisode

    # These ADC adjustments are used for integer conversion. It's a good idea
    # to populate these with non-zero values even when using float32 notation
    # to avoid divide-by-zero errors when loading ABFs.

    fSignalGain = 1  # always 1
    fADCProgrammableGain = 1  # always 1
    lADCResolution = 2**15  # 16-bit signed = +/- 32768

    # determine the peak data deviation from zero
    maxVal = np.max(np.abs(ys))

    # set the scaling factor to be the biggest allowable to accommodate the data
    fInstrumentScaleFactor = 100
    for i in range(10):
        fInstrumentScaleFactor /= 10
        fADCRange = 10
        valueScale = lADCResolution / fADCRange * fInstrumentScaleFactor
        maxDeviationFromZero = 32767 / valueScale
        if (maxDeviationFromZero >= maxVal):
            break

    # prepare units as a space-padded 8-byte string
    unitString = ['pA']*16
    unitString[:len(units)] = units
    for i in range(len(unitString)):
        while len(unitString[i]) < 8:
            unitString[i] += " "

    labelString = [' ']*16
    labelString[:len(labels)] = labels
    for i in range(len(labelString)):
        while len(labelString[i]) < 10:
            labelString[i] += " "

    # store the scale data in the header
    struct.pack_into('i', data, 252, lADCResolution)
    struct.pack_into('f', data, 244, fADCRange)
    for i in range(16):
        struct.pack_into('f', data, 922+i*4, fInstrumentScaleFactor)
        struct.pack_into('f', data, 1050+i*4, fSignalGain)
        struct.pack_into('f', data, 730+i*4, fADCProgrammableGain)
        struct.pack_into('8s', data, 602+i*8, unitString[i].encode())
        struct.pack_into('10s', data, 442+i*10, labelString[i].encode())
        struct.pack_into('h', data, 410+i*2, i)

    # fill data portion with scaled data from signal
    dataByteOffset = BLOCKSIZE * HEADER_BLOCKS
    ys_interleaved = np.empty((channelCount*sweepCount*sweepPointCount), dtype=ys.dtype)
    ys = np.reshape(ys, (channelCount, 1, sweepCount*sweepPointCount))
    # ys_interleaved = np.reshape(ys, (channelCount*sweepCount*sweepPointCount))
    # for i in range(channelCount):
    #     ys_interleaved[i::channelCount] = ys[i]
    ys_interleaved[0::2]=np.reshape(ys[0], (sweepCount*sweepPointCount))
    ys_interleaved[1::2] = np.reshape(ys[1], (sweepCount*sweepPointCount))

    print(ys.shape)
    print(ys_interleaved.shape)

    for i, value in enumerate(ys_interleaved):
        valueByteOffset = i*bytesPerPoint
        bytePosition = dataByteOffset + valueByteOffset
        struct.pack_into('h', data, bytePosition, int(value*valueScale))
    # for sweepNumber, sweepSignal in enumerate(ys_interleaved):
    #     sweepByteOffset = sweepNumber * sweepPointCount * bytesPerPoint
    #     for valueNumber, value in enumerate(sweepSignal):
    #         valueByteOffset = valueNumber * bytesPerPoint
    #         bytePosition = dataByteOffset + sweepByteOffset + valueByteOffset
    #         struct.pack_into('h', data, bytePosition, int(value*valueScale))

    # save the byte array to disk
    with open(filename, 'wb') as f:
        f.write(data)
    return

if __name__=='__main__':

    # sampling_rate = 10000
    # test_data=np.arange(0,10,1/sampling_rate)
    # test_data = np.reshape(test_data, (1,len(test_data)))
    # filename = 'write_test1.abf'
    read_filename = "20112011-EJC test.abf"
    recording = analyzer2.Recording(read_filename)
    write_filename = 'write_test2.abf'
    writeABF1(recording.get_y_matrix(mode='overlay'),write_filename, sampleRateHz=recording.sampling_rate,units=recording.channel_units, labels=recording.channel_labels)

    # filename = "19911002-2.abf"
    data = pyabf.abf.ABF(write_filename)
    print(data._dataGain)
    print(data._dataOffset)
    print(data.data)
