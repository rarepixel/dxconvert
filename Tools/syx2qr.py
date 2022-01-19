#!/usr/bin/env python3
import os, sys
from datetime import datetime
from base64 import b64encode
from array import array
from argparse import ArgumentParser
from glob import glob
from shutil import copy

if sys.hexversion > 0x03000000:
    PY3 = True
else:
    PY3 = False
    range = xrange

try:
    import qrcode
except ImportError:
    print ("Requires python module: qrcode")
    sys.exit(1)

try:
    import webbrowser
    SHOW = True
except ImportError:
    print ("Warning: Display of QR code requires python module: webbrowser")
    SHOW = False

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

def infile2syx(infile):
    syx = array('B')
    size = os.path.getsize(infile)
    with open(infile, 'rb') as f:
        syx.fromfile(f, size)
    return syx

def syx2txt(syx, infile):
    ch = syx[2]
    if syx[:8].tolist() == [0xF0, 0x43, ch, 0x7F, 0x1C, 0x00, 0x04, 0x03]:
        model = 'cs'
    elif syx[:8].tolist() == [0xF0, 0x43, ch, 0x7F, 0x1C, 0x00, 0x04, 0x05]:
        model = 'dx'
    elif syx[:8].tolist() == [0xF0, 0x43, ch, 0x7F, 0x1C, 0x00, 0x04, 0x04]:
        model = 'cp'
    elif syx[:8].tolist() == [0xF0, 0x43, ch, 0x7F, 0x1C, 0x00, 0x04, 0x06]:
        model = 'yc'
    else:
        print ("Unsupported sysex {}")
        sys.exit(1)

    if model=='dx':
        voicename = ''
        for i in range(0x18, 0x18+10):
            voicename += chr(syx[i])
    else:
        voicename = os.path.basename(infile)
        voicename = os.path.splitext(infile)[0]
    voicename = voicename.strip()

    s = 'reface web site:\n'
    s += 'http://www.yamaha.com/reface/\n\n'
    s += '{\n'
    s += '  "mdl" : "{}",\n'.format(model)
    s += '  "oct" : 0,\n'
    if PY3:
        s += '  "data" : "{}",\n'.format(str(b64encode(syx))[3:])
    else:
        s += '  "data" : "{}",\n'.format(b64encode(syx))

    cdate = datetime.today() - datetime(1970,1,1)
    cdate = int(cdate.total_seconds())
    s += '  "cDate" : {},\n'.format(cdate)
    s += '  "vce" : "{}",\n'.format(voicename)
    s += '  "phrase" : "QuarterNote",\n'
    if model == 'cs':
        s += '  "pImg" : "01_reface_default_cs"\n'
    elif model == 'dx':
        s += '  "pImg" : "02_reface_default_dx"\n'
    elif model == 'yc':
        s += '  "pImg" : "03_reface_default_ys"\n'
    elif model == 'cp':
        s += '  "pImg" : "04_reface_default_cp"\n'
    s += '}\n'
    return s

def syx2qr(infile, outfile):
    makebak(outfile)
    syx = infile2syx(infile)
    txt = syx2txt(syx, infile)
    if os.path.splitext(outfile)[1] == ".txt":
        with open(outfile, 'w') as f:
            f.write(txt)
    else:
        qr = qrcode.make(txt)
        qr.save(outfile)
    print("QR image saved as:\n{}".format(outfile))

def view(outfile):
    webbrowser.open(outfile)

if __name__ == "__main__":
    parser = ArgumentParser(description = "SYX to QR converter for Yamaha Reface")
    parser.add_argument('-o', '--outfile', help="*.png|*.txt")
    if SHOW:
        parser.add_argument('-s', '--show', action='store_true', default=False, help="show generated QR code")
    parser.add_argument('-v', '--version', action='version', version = "20170723")
    parser.add_argument('infile', nargs="+", help="*.syx")
    args = parser.parse_args()
    
    for infiles in args.infile:
        for infile in glob(infiles):
            if args.outfile:
                outfile = args.outfile
            else:
                outfile = os.path.splitext(infile)[0] + ".png"

            try:
                syx2qr(infile, outfile)
            except:
                print ("Error: conversion from {} to {} failed".format(infile, outfile))

            if args.show and SHOW:
                view(outfile)

    sys.exit(0)

