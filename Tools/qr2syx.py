#!/usr/bin/env python3
import os, sys
from subprocess import call
from base64 import b64decode
from argparse import ArgumentParser
from shutil import copy
from glob import glob

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

def qr2txt(qrfile, txtfile, decoder='zbarimg'):
    with open(txtfile, 'w') as f:
        call([decoder , qrfile], stdout = f)
    return os.path.getsize(txtfile)
    
def txt2syx(txtfile, syxfile):
    with open(txtfile, 'r') as f:
        txt = f.readlines()

    for s in txt:
        if s.strip().startswith('"data"'):
            datas = s.split(":")[1].strip('", ')
            break
    try:
        data = b64decode(datas)
    except:
        print("QR Decoding failed.")
        sys.exit(1)
    
    with open(outfile, 'wb') as f:
        f.write(data)
    print("{} bytes of SysEx data written to:\n{}".format(os.path.getsize(outfile), outfile))

def qr2syx(infile, outfile):
    makebak(outfile)
    if os.path.splitext(infile)[1] == ".txt":
        txtfile = infile
    else:
        txtfile = os.path.splitext(outfile)[0] + ".txt"
        try:
            if qr2txt(infile, txtfile, 'zbarimg') < 100:
                qr2txt(infile, txtfile, 'zxing')
        except:
            print("Error: zxbarimg or zxing not found?") 
    if txtfile != outfile:
        if os.path.splitext(outfile)[1] == ".txt":
            copy(txtfile, outfile)
        else:
            txt2syx(txtfile, outfile)

if __name__ == '__main__':
    parser = ArgumentParser(description = "QR to SYX converter for Yamaha Reface")
    parser.add_argument('-o', '--outfile', help="*.syx|*.txt")
    parser.add_argument('-v', '--version', action='version', version = "20160323")
    parser.add_argument('infile', nargs="+", help="*.jpg|*.jpeg|*.png|*.txt")
    args = parser.parse_args()

    for infiles in args.infile:
        for infile in glob(infiles):
            if args.outfile:
                outfile = args.outfile
            else:
                outfile = os.path.splitext(infile)[0] + ".syx"

            try:
                qr2syx(infile, outfile)
            except:
                print("Error: Conversion from {} to {} failed".format(infile, outfile))
    sys.exit(0)

