#!/usr/bin/env python3

# DX7IIFD .Ixx fileformat
# Offset    Size    Data
# 0x0000    1       0xAA
# 0x0001    3720    [0x00, 0x00, 0xff, 0xff] * 930
# 0x0e89    2       0x00, 0x00
# 0x0e8b    85      SYSTEM(0-19) + SYSTEM(37) + SYSTEM(38-101)
# 0x0ee0    256     MCT User 1
# 0x0fe0    256     MCT User 2
# 0x10e0    1632    PMEM p01-p32
# 0x1740    288     AMEM(26-34) v01-v32
# 0x1860    288     AMEM(26-34) v33-v64
# 0x1980    832     AMEM(0-25) v01-v32
# 0x1cc0    832     AMEM(0-25) v33-v64
# 0x2000    4096    VMEM v01-v32
# 0x3000    4096    VMEM v33-v64
# ==============================
# 0x4000    16384   Total

import sys, os
from array import array
from glob import glob
from argparse import ArgumentParser
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

def unihead(s):
    unihead = []
    for i in s:
        unihead.append(ord(i))
    return unihead

def checksum(dat):
    csum = sum(dat) % 128
    csum = (128 - csum) % 128
    return csum

def makesyx(vmemA, vmemB, amemA, amemB, pmem):
    syx = [0xF0, 0x43, 0x10, 0x19, 0x4d, 0x00, 0xf7]
    syx += [0xF0, 0x43, 0x00, 0x06, 0x08, 0x60]
    syx += amemA
    syx += [checksum(amemA), 0xf7]
    syx += [0xF0, 0x43, 0x00, 0x09, 0x20, 0x00]
    syx += vmemA
    syx += [checksum(vmemA), 0xf7]

    syx += [0xF0, 0x43, 0x10, 0x19, 0x4d, 0x01, 0xF7]
    syx += [0xF0, 0x43, 0x00, 0x06, 0x08, 0x60]
    syx += amemB
    syx += [checksum(amemB), 0xf7]
    syx += [0xF0, 0x43, 0x00, 0x09, 0x20, 0x00]
    syx += vmemB
    syx += [checksum(vmemB), 0xf7]

    PMEMHEAD = unihead('LM  8973PM')
    syx += [0xf0, 0x43, 0x00, 0x7e, 0x0c, 0x6a]
    syx += PMEMHEAD + pmem
    syx += [checksum(PMEMHEAD + pmem), 0xf7]
    return syx

def fd2syx(INFILE, OUTFILE):
    fd = array('B')

    with open(INFILE, 'rb') as f:
        fd.fromfile(f, 16384)
    fd = fd.tolist()

    vmemA = fd[0x2000:0x3000]
    vmemB = fd[0x3000:0x4000]

    amemA = []
    for i in range(32):
        fd[0x1980+26*i] = 0 #Scaling Mode = Normal
        amemA += fd[0x1980+26*i:0x1980+26*(i+1)]
        amemA += fd[0x1740+9*i:0x1740+9*(i+1)]

    amemB = []
    for i in range(32):
        fd[0x1cc0+26*i] = 0 #Scaling Mode = Normal
        amemB += fd[0x1cc0+26*i:0x1cc0+26*(i+1)]
        amemB += fd[0x1860+9*i:0x1860+9*(i+1)]

    pmem = fd[0x10e0:0x1740]
    syst = fd[0xe8b:0xee0]
    mct1 = fd[0xee0:0xfe0]
    mct2 = fd[0xfe0:0x10e0]

    syx = array('B', makesyx(vmemA, vmemB, amemA, amemB, pmem))
    makebak(OUTFILE)
    with open(OUTFILE, 'wb') as f:
        syx.tofile(f)

if __name__ == '__main__':
    parser = ArgumentParser(description = 'DX7IIFD disk (*.Ixx) to SysEx (*.syx) file converter for Voices + Performances')
    parser.add_argument('-o', '--outfile', help = '*.syx')
    parser.add_argument('-v', '--version', action = 'version', version = '20160323')
    parser.add_argument('infile', nargs = '+', help = '(*.I??)')
    args = parser.parse_args()
    for infiles in args.infile:
        for infile in glob(infiles):
            if args.outfile:
                outfile = args.outfile
            else:
                outfile = os.path.splitext(infile)[0] + '.syx'

            if (os.path.getsize(infile) == 16384) and (infile[-4:-2].lower()) == '.i':
                try:
                    fd2syx(infile, outfile)
                    print ("Converted from {} to {} !".format(infile, outfile))
                except:
                    print ("Conversion from {} to {} failed".format(infile, outfile))

            else:
                print ("Only *.ixx files with size = 16384 bytes are accepted.")
    sys.exit()


