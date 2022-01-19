#!/usr/bin/env python3
VERSION="20191208"
import sys
import array
import os
from argparse import ArgumentParser
from glob import glob
from shutil import copy
MThd = [0x4d, 0x54, 0x68, 0x64]

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

def mid2syx(mid):
    if mid[:4] != MThd:
        print ("Not a MIDI file {}".format(chr(mid[0])+chr(mid[1])+chr(mid[2])+chr(mid[3])))
        return []
    SYX = []
    syx = []
    i = 0
    n = 0
    while i < len(mid):
        n = 0
        if mid[i] in (0xf0, 0xf7):
            if mid[i] == 0xf0: 
                syx.append(0xf0)
            i += 1
            if mid[i]<128:
                n = mid[i]
                i += 1
            elif mid[i+1]<128:
                n = mid[i+1]
                n += (mid[i]&127)<<7
                i += 2
            elif mid[i+2]<128:
                n = mid[i+2]
                n += (mid[i+1]&127)<<7
                n += (mid[i]&127)<<14
                i += 3
            elif mid[i+3]<128:
                n = mid[i+3]
                n += (mid[i+2]&127)<<7
                n += (mid[i+1]&127)<<14
                n += (mid[i]&127)<<21
                i += 4
            syx += mid[i:i+n]
            if (syx[0] == 0xf0) and (syx[-1] == 0xf7):
                SYX += syx
                syx = []
            i += n
        else:
            i += 1
    return SYX

if __name__ == '__main__':
    parser = ArgumentParser(description = 'MIDI (.mid) to SysEx (.syx) file converter')
    parser.add_argument('-o', '--outfile', help = '*.syx')
    parser.add_argument('-v', '--version', action = 'version', version = VERSION)
    parser.add_argument('infile', nargs = '+', help = '*.mid|*.midi')
    args = parser.parse_args()
    for infiles in args.infile:
        for infile in glob(infiles):
            if args.outfile:
                outfile = args.outfile
            else:
                outfile = os.path.splitext(infile)[0] + '.syx'

            try:
                indat = array.array('B')

                with open(infile, "rb") as f:
                    indat.fromfile(f, os.path.getsize(infile))
                
                indat = list(indat)
                outdat = array.array('B')
                outdat.fromlist(mid2syx(indat))
                if len(outdat) != 0:
                    makebak(outfile)
                    with open(outfile, "wb") as f:
                        outdat.tofile(f)
                    print ("{} succesfully converted to {} !".format(infile, outfile))
            except:
                print ("Conversion from {} to {} failed!".format(infile, outfile))

    sys.exit(0)


