#!/usr/bin/env python3

"""
txconvert.py

(c)2020 Martin Tarenskeen <m.tarenskeenATkpnmailDOTnl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

__license__ = 'GPL v3'

import sys
import os
from argparse import ArgumentParser
from glob import glob
from DXconvert import TXC
from DXconvert import dxcommon
try:
    import rtmidi
    ENABLE_MIDI = True
    del rtmidi
except:
    ENABLE_MIDI = False

PROGRAMNAME = TXC.PROGRAMNAME
PROGRAMVERSION = dxcommon.PROGRAMVERSION
PROGRAMDATE = dxcommon.PROGRAMDATE

############# CLI ###################

def cli_main(argv=sys.argv):
    progname = os.path.basename(argv[0])

    parser = ArgumentParser(
            description = '{}\nVersion: {} ({})'.format(PROGRAMNAME, PROGRAMVERSION, PROGRAMDATE), )
    parser.add_argument('-b', '--brightness', default=0, type=int, help='Adjust global brightness (+/-)')  
    parser.add_argument('-bc', '--breathcontrol', action='store_false', default=True, help='Do NOT use BreathControl')
    parser.add_argument('-bc2at', '--bc2at', action='store_true', default=False, help='Copy BreathControl data to Aftertouch')
    parser.add_argument('-c', '--channel', default=0, type=int, help='Midi channel (1~16)in SysEx header')
    parser.add_argument('-C', '--check', action='store_true', default=False, help='Check SysEx checksum before import') 
    parser.add_argument('-f', '--find', metavar='STRING', help='Search for STRING in patchnames')
    if ENABLE_MIDI:
        parser.add_argument('-mi', '--mid_in', help='select midiport MID_IN to receive data FROM synth when selecting a .req file')
        parser.add_argument('-mo', '--mid_out', help='select midiport MID_OUT to send data TO synth when choosing "MIDI" as outfile')
        parser.add_argument('-m', '--mid', help='use this option as a shortcut for "--mid_in MID_IN --mid_out MID_OUT", if MID_IN and MID_OUT have the same name MID')
    parser.add_argument('-n', '--nosplit', action='store_true', default=False, help="Don't split: save data in one file")
    parser.add_argument('-nd', '--nodupes', action='store_true', default=False, help='Remove duplicates')
    parser.add_argument('-nd2', '--nodupes2', action='store_true', default=False, help='Remove duplicates, also with different names')
    parser.add_argument('-ns', '--nosilence', action='store_true', default=False, help='Remove patches that produce no sound')
    parser.add_argument('-o', '--offset', default='0', help="Ignore first/last (+/-) OFFSET bytes in input file(s)")
    parser.add_argument('-r', '--random', action='store_true', default=False, help="easy randomizer") 
    parser.add_argument('-sp', '--split', action='store_true', default=False, help="Save each patch in a separate file")
    parser.add_argument('-s', '--select', metavar='RANGE', help='Select patch RANGE to save')
    parser.add_argument('-S', '--sort', action='store_true', default=False, help='Sort patches by name, not case-sensitive')
    parser.add_argument('-S2', '--sort2', action='store_true', default=False, help='Sort patches by name, case-sensitive')
    parser.add_argument('--copy', nargs=2, metavar=('X', 'Y'), help='Copy patch nr X to nr Y')
    parser.add_argument('--swap', nargs=2, metavar=('X', 'Y'), help='Swap patch nr X and nr Y')
    parser.add_argument('-v', '--version', action='version', version='{} ({})'.format(PROGRAMVERSION, PROGRAMDATE)) 
    parser.add_argument('-x', '--exclude', metavar='STRING', help='Exclude if STRING is found in patchname')
    parser.add_argument('-y', '--yamaha', metavar='MODEL', default='tx81z', help='Specify Yamaha synth MODEL for outfile') 
    parser.add_argument('infile', nargs='+', help='Selects input file(s)')
    parser.add_argument('outfile', help='Select output file')

    args=parser.parse_args()
    infilez = args.infile
    infiles = []
    for i in infilez:
        infiles += glob(i)

    outfile = args.outfile
    outfile_ext = os.path.splitext(outfile)[1]
    outfile_dir = os.path.split(outfile)[0]

    mid_in = ""
    mid_out = ""
    if ENABLE_MIDI:
        mid_in = dxcommon.MID_IN
        mid_out = dxcommon.MID_OUT
        CFG = dxcommon.CFG
        if os.getenv('MID_IN'):
            mid_in = os.getenv('MID_IN')
        mid_out = os.getenv('MID_OUT')
        if os.path.exists(CFG):
            with open(CFG, 'r') as f:
                for line in f.readlines():
                    l = line.split('=')
                    if l[0].strip() == 'MID_IN':
                        mid_in = l[1].strip()
                    if l[0].strip() == 'MID_OUT':
                        mid_out = l[1].strip()

        if args.mid:
            mid_in = args.mid
            mid_out =  args.mid
        if args.mid_in:
            mid_in = args.mid_in
        if args.mid_out:
            mid_out = args.mid_out
        if args.mid_in or args.mid_out:
            with open(CFG, 'w') as f:
                if mid_in: f.write('MID_IN = {}\n'.format(mid_in))
                if mid_out: f.write('MID_OUT = {}\n'.format(mid_out))

    bc = args.breathcontrol
    bc2at = args.bc2at
    brightness = args.brightness
    nosplit = args.nosplit
    ch = args.channel
    check = args.check
    select = args.select
    sort = args.sort
    sort2 = args.sort2
    swap = args.swap
    copy = args.copy
    nodupes = args.nodupes
    nodupes2 = args.nodupes2
    nosilence = args.nosilence
    offset = args.offset
    Random = args.random
    find = args.find
    exclude = args.exclude
    yamaha = args.yamaha.lower().strip()

    FB01 = False
    REFACE = False
    if yamaha in ('ys100', 'ys200', 'tq5', 'b200', 'ds55', 'v50'):
        split = 25
    elif yamaha in ('dx27', 'dx27s', 'dx100'):
        split = 24
    elif yamaha == 'fb01' or outfile_ext.lower() == '.fb1':
        yamaha = 'fb01'
        FB01 = True
        split = 48
    elif yamaha in ('opm', 'vopm') or outfile_ext.lower() == '.opm':
        yamaha = 'vopm'
        FB01 = True
        split = 128
    elif yamaha in ('reface', 'dxreface', 'refacedx'):
        yamaha = 'refacedx'
        REFACE = True
        split = 32
    else:
        split = 32
    
    if args.split:
        split = 1

    if nosplit or (outfile == "MIDI") or (outfile == os.devnull):
        split = sys.maxsize
        nosplit = True

    txdata = []
    for infile in infiles:
        print ("Reading {}".format(infile))
        if not os.path.exists(infile):
            print ("{} not found".format(infile))
            return 1
        if infile == outfile:
            print ("Must have different input and output files")
            return 1

        if os.path.isfile(infile):
            txdat, channel = TXC.read(infile, offset, check, yamaha, mid_in, mid_out)
            txdata += txdat

    if ch != None:
        channel = ch-1
        channel = max(0, channel)
        channel = min(15, channel)

    if nodupes2:
        nodupes = True
            
    if nodupes or nodupes2:
        if FB01:
            txdata = TXC.fbnodupes(txdata, nodupes2)
        elif REFACE:
            txdata = TXC.rdxnodupes(txdata, nodupes2)
        else:
            txdata = TXC.txnodupes(txdata, nodupes2)

    if nosilence:
        if FB01:
            txdata = TXC.fbnosilence(txdata)
        elif REFACE:
            txdata = TXC.rdxnosilence(txdata)
        else:
            txdata = TXC.txnosilence(txdata)

    if select != None: 
        txdat = []
        for i in dxcommon.range2list(select):
            if FB01:
                txdat += txdata[64*(i-1): 64*i]
            elif REFACE:
                txdat += txdata[150*(i-1): 150*i]
            else:
                txdat += txdata[128*(i-1): 128*i]
        txdata = txdat
    
    if args.find != None:
        if FB01:
            txdata = TXC.fbfind(txdata, find)
        elif REFACE:
            txdata = TXC.rdxfind(txdata, find)
        else:
            txdata = TXC.txfind(txdata, find)
    
    if args.exclude:
        if FB01:
            txdata = TXC.fbexclude(txdata, exclude)
        elif REFACE:
            txdata = TXC.rdxexclude(txdata, exclude)
        else:
            txdata = TXC.txexclude(txdata, exclude)
        
    if brightness:
        if FB01:
            txdata = TXC.fbbrightness(txdata, brightness)
        elif REFACE:
            txdata = TXC.rdxbrightness(txdata, brightness)
        else:
            txdata = TXC.txbrightness(txdata, brightness)

    if bc2at:
        if (FB01 == False) and (REFACE == False):
            for i in range(len(txdata)//128):
                txdata[128*i+84:128*i+88] = txdata[128*i+53:128*i+57]
                if txdata[128*i+86]>50:
                    txdata[128*i+86] -= 51
                else:
                    txdata[128*i+86] +=50

    if bc == False:
        if (FB01 == False) and (REFACE == False):
            for i in range(len(txdata)//128):
                txdata[128*i+53:128*i+57] = [0,0,50,0]
    
    if Random:
        if FB01:
            txdata = dxcommon.dxrandom(txdata, 64)
        elif REFACE:
            txdata = dxcommon.dxrandom(txdata, 150)
        else:
            txdata = dxcommon.dxrandom(txdata, 128)

    if sort:
        if FB01:
            txdata = TXC.fbsort(txdata, False)
        elif REFACE:
            txdata = TXC.rdxsort(txdata, False)
        else:
            txdata = TXC.txsort(txdata, False)

    if sort2:
        if FB01:
            txdata = TXC.fbsort(txdata, True)
        elif REFACE:
            txdata = TXC.rdxsort(txdata, True)
        else:
            txdata = TXC.txsort(txdata, False)

    if copy:
        if FB01:
            txdata = TXC.txcopy(dxcommon.range2list(copy[0]), int(copy[1]), txdata, 64)
        elif REFACE:
            txdata = TXC.txcopy(dxcommon.range2list(copy[0]), int(copy[1]), txdata, 150)
        else:
            txdata = TXC.txcopy(dxcommon.range2list(copy[0]), int(copy[1]), txdata, 128)

    if swap:
        if FB01:
            txdata = TXC.txswap(int(swap[0]), int(swap[1]), txdata, 64)
        elif REFACE:
            txdata = TXC.txswap(int(swap[0]), int(swap[1]), txdata, 150)
        else:
            txdata = TXC.txswap(int(swap[0]), int(swap[1]), txdata, 128)

    if FB01:
        n = len(txdata)//64
    elif REFACE:
        n = len(txdata)//150
    else:
        n = len(txdata)//128
        
    if (split == 1) and (n > 1):            
        if FB01:
            for i in range(n):
                outfile_name = dxcommon.list2string(txdata[64*i:64*i+7])
                outfile_name = dxcommon.validfname(outfile_name)
                Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
                
                count = 0
                while os.path.exists(Outfile):
                    count += 1
                    if count>1:
                        Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)

                print (TXC.write(Outfile, txdata[64*i:64*(i+1)], channel, nosplit, 1, yamaha, mid_out))
        elif REFACE:
            for i in range(n):
                outfile_name = dxcommon.list2string(txdata[150*i:150*i+10])
                outfile_name = dxcommon.validfname(outfile_name)
                Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
                
                count = 0
                while os.path.exists(Outfile):
                    count += 1
                    if count>1:
                        Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)
                
                print (TXC.write(Outfile, txdata[150*i:150*(i+1)], channel, nosplit, 1, yamaha, mid_out))
        else:
            for i in range(n):
                outfile_name = dxcommon.list2string(txdata[128*i+57:128*i+67])
                outfile_name = dxcommon.validfname(outfile_name)
                Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
                
                count = 0
                while os.path.exists(Outfile):
                    count += 1
                    if count>1:
                        Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)
                
                print (TXC.write(Outfile, txdata[128*i:128*(i+1)], channel, nosplit, 1, yamaha, mid_out))
    else:
        print (TXC.write(outfile, txdata, channel, nosplit, split, yamaha, mid_out))

    return 0

################### MAIN #####################

if __name__ == '__main__':
    sys.exit(cli_main())
    

