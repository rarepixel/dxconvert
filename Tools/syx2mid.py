#!/usr/bin/env python3
VERSION = "20191212"
import sys
import array
import os
from argparse import ArgumentParser
from glob import glob
from shutil import copy
try:
    range = xrange
except NameError:
    pass

def makebak(fn):
    bakname = fn
    n = 0
    while os.path.exists(bakname):
        n += 1
        bakname = fn + '.' + str(n)
    if (fn != bakname):
        print ('Warning: {} already exists and will be overwritten'.format(fn))
        print ('A backup of the original file will be saved as {}'.format(bakname))
        copy(fn, bakname)

def syx2mid(syx, bpm=120.0, interval=10, res=96, chunksize=0, trackname="SysEx Data"):
    #####  HEADER CHUNK #####
    # format 0, 1 track, res ticks/quarter
    mid = [0x4d, 0x54, 0x68, 0x64, 0, 0, 0, 6, 0, 0, 0, 1, (res>>8) & 0xff , res & 0xff]
    ##### TRACK CHUNK #####
    mid += [0x4d, 0x54, 0x72, 0x6b]
    mid += [0, 0, 0, 0] # tracklength=mid[18:22]
    
    ##### TRACK events #####
    # text meta event "SysEx Data"
    mid += [0x00, 0xff, 0x01, 10]
    for k in "SysEx Data":
        mid.append(ord(k))

    # trackname meta event
    mid += [0x00, 0xff, 0x03, len(trackname)]
    for k in trackname:
        mid.append(ord(k))

    # tempo meta event
    mid += [0x00, 0xff, 0x51, 0x03]
    tempo = int(round(60000000./bpm))
    mid.append((tempo >> 16) & 0xff)
    mid.append((tempo >> 8) & 0xff)
    mid.append(tempo & 0xff)

    #time signature meta event
    mid += [0x00, 0xff, 0x58, 0x04] #signature meta event
    mid += [0x04, 0x02, 0x18, 0x08] #4/4, 24 clocks per beat, beat=8/32=1/4 

    # SysEx events
    mid.append(0) # delta time before first sysex event
    for i in range(len(syx)):
        if syx[i] == 0xf0:
            count = 0
            syxevent = []
            i += 1
            while syx[i] != 0xf7:
                syxevent.append(syx[i])
                i += 1
                count += 1
            mid += [0xf0] + varlen(count + 1) + syxevent + [0xf7]
            mid += varlen(ticks((interval + 0.32 * count), bpm, res)) # delta time before next event + interval

    # End of Track meta event
    mid += [0xff, 0x2f, 0x00]
    
    trlen = len(mid[22:])
    mid[18] = (trlen&0xff000000)>>24
    mid[19] = (trlen&0xff0000)>>16
    mid[20] = (trlen&0xff00)>>8
    mid[21] = trlen&0xff

    return mid

def varlen(i):
    vl = []
    if i < 128:
        vl.append(i)
    elif i < 16384:
        vl.append(128 + ((i>>7)&127))
        vl.append(i&127)
    elif i < 2097152:
        vl.append(128 + ((i>>14)&127))
        vl.append(128 + ((i>>7)&127))
        vl.append(i&127)
    else:
        vl.append(128 + ((i>>21)&127))
        vl.append(128 + ((i>>14)&127))
        vl.append(128 + ((i>>7)&127))
        vl.append(i&127)
    return vl

def ticks(ms, bpm, res):
    return int(round(ms * bpm * res / 60000))

if __name__ == '__main__':
    parser = ArgumentParser(description = 'SysEx (.syx) to MIDI (.mid) file converter')
    parser.add_argument('-b', '--bpm', type = float, help = 'BPM metronome tempo (120)', default = 120)
    #parser.add_argument('-c', '--chunksize', type = int, help = 'insert time interval after every CHUNKSIZE bytes', default=0) 
    parser.add_argument('-i', '--interval', type = int, help = 'additional milliseconds between sysex chunks and blocks (10)', default = 10)
    parser.add_argument('-o', '--outfile', help = '*.mid')
    parser.add_argument('-t', '--trackname', help = "trackname", default="Sysex Data")
    parser.add_argument('-r', '--resolution', type = int, help = 'PPQN resolution (96)', default = 96)
    parser.add_argument('-v', '--version', action = 'version', version = VERSION)
    parser.add_argument('infile', nargs = '+', help = '*.syx')
    args = parser.parse_args()
    bpm = args.bpm
    chunksize = 0
    #chunksize = args.chunksize
    interval = args.interval
    res = args.resolution
    trackname = args.trackname
    
    for infiles in args.infile:
        for infile in glob(infiles):
            if args.outfile:
                outfile = args.outfile
            else:
                outfile = os.path.splitext(infile)[0] + '.mid'

            try:
                indat = array.array('B')

                with open(infile, "rb") as f:
                    indat.fromfile(f, os.path.getsize(infile))

                outdat = array.array('B')
                outdat.fromlist(syx2mid(indat, bpm, interval, res, chunksize, trackname))

                makebak(outfile)
                with open(outfile, "wb") as f:
                    outdat.tofile(f)
    
                print ("{} succesfully converted to {} !".format(infile, outfile))
            except:
                print ("Conversion from {} to {} failed!".format(infile, outfile))
    sys.exit(0)


