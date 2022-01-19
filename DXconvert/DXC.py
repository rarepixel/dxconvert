"""

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

import array
import os
import sys
import zipfile
from tempfile import mkstemp
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import base64
import gzip

from . import dx7
from . import dx200
from . import syxmidi
from . import fourop
from . import tx7
from . import fb01
from . import pssx80
from . import vopm
from . import dxcommon
from . import wav2syx
from . import korg
from . import reface
from . import bohmorla
from . import korgz3

try:
    range = xrange
except NameError:
    pass

PROGRAMNAME="DXconvert"
PROGRAMVERSION=dxcommon.PROGRAMVERSION
PROGRAMDATE=dxcommon.PROGRAMDATE
MID_IN=dxcommon.MID_IN
MID_OUT=dxcommon.MID_OUT

########## FILE INPORT/EXPORT #########

def read(infile, offset='0', check=False, mid_in=MID_IN, mid_out=MID_OUT):
    if offset.startswith('-'):
        datasize = os.path.getsize(infile) + int(offset, 0)
        offset = datasize % 128
    else:
        offset = int(offset, 0)

    dx7data = []
    dx72data = []
    tx7data = []
    channel = 0
    if zipfile.is_zipfile(infile):
        with zipfile.ZipFile(infile, 'r') as zf:
            zflist = zf.namelist()
            for n in zflist:
                try:
                    dx7dat = []
                    dx72dat = []
                    tx7dat = []
                    d = zf.read(n)
                    tmp = mkstemp()[1]
                    with open(tmp, 'wb') as f:
                        f.write(d)
                    dx7dat, dx72dat, tx7dat, channel = read2(mid_in, mid_out, tmp, offset, check)
                    os.remove(tmp)
                    dx7data += dx7dat
                    dx72data += dx72dat
                    tx7data += tx7dat
                    print ("\t{}".format(n))
                except:
                    print ("! only {} from {} files in zip were read".format(zflist.index(n)+1, len(zflist)))
                    break
    else:
        dx7data, dx72data, tx7data, channel = read2(mid_in, mid_out, infile, offset, check)
    return dx7data, dx72data, tx7data, channel

def read2(mid_in, mid_out, infile, offset, check=False):
    ext = os.path.splitext(infile)[1].lower()
    size = os.path.getsize(infile)-offset
    data = array.array("B")
    with open(infile, 'rb') as f:
        data.fromfile(f, offset+size)
    data = data.tolist()[offset:]
    
    #Dump Request
    if dxcommon.ENABLE_MIDI:
        if ext==".req" and data[0] == 0xf0:
            data, size = dxcommon.req2data(data, mid_in, mid_out)

    #check if file is a MIDI file
    if data[0:4] == [0x4d, 0x54, 0x68, 0x64]: #"MThd"
        data = syxmidi.mid2syx(data)
        size = len(data)

    #JSynthLib patchdata.xml
    if infile.endswith(".patchlib.xml"):
        tmpgz = mkstemp(suffix='.gz')[1]
        tree = ET.parse(infile)
        root = tree.getroot()
        s = root.findall(".//patchData")
        with open(tmpgz, 'wb') as f:
            for t in s:
                f.write(base64.b64decode(t.text))
        with gzip.open(tmpgz, 'rb') as f:
            if sys.hexversion > 0x3000000:
                data = list(f.read())
            else:
                data = dxcommon.string2list(f.read())

        size = len(data) 
        os.remove(tmpgz)

    data += [0xf7, 0xf7, 0, 0, 0, 0, 0, 0, 0, 0]
    dx7data = []
    dx72data = []
    tx7data = []
    channel = 0
    
    #single voice(s)
    if size>160:
        for i in range(size-51):
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==5 and data[i+4]==0 and data[i+5]==0x31 and data[i+6+50]==0xf7:
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+49]) == data[i+6+49]):
                    dx72data += dx7.aced2amem(data[i+6:i+6+49])
                else:
                    dx72data += dx7.initamem()
                channel=data[i+2]
        for i in range(size-157):
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0 and data[i+4]==1 and data[i+5]==0x1b and (data[i+6+156]==0xf7 or data[i+6+157]==0xf7):
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+155])==data[i+6+155]):
                    dx7data += dx7.vced2vmem(data[i+6:i+6+155])
                else:
                    dx7data += dx7.initvmem()
                channel=data[i+2]

    #Grey Matter Response E! 1 single voice
    if size>262:
        for i in range(size-259):
            if data[i]==0xf0 and data[i+1]==0x12 and data[i+264]==0xf7:
                for p in range(6128):
                    d2 = data[i+7+2*p] & 15
                    d1 = data[i+7+2*p+1] & 15
                    data[p] = (d1<<4) + d2
                dx7data += dx7.cleanvmem(data[:128])
                dx72data += dx7.initamem()

    #Grey Matter Response E! 1 bank 32 voices
    if size>8198:
        for i in range(size-8195):
            if data[i]==0xf0 and data[i+1]==0x12 and data[i+8200]==0xf7:
                for p in range(128*32):
                    d2 = data[i+7+2*p] & 15
                    d1 = data[i+7+2*p+1] & 15
                    data[p] = (d1<<4) + d2
                #dx7data += data[:128*32]
                for p in range(32):
                    dx7data += dx7.cleanvmem(data[128*p:128*p+128])
                dx72data += dx7.initamem()*32

    #Grey Matter Response DX7 E! ROM 256 voices
    if size==32768 and ext==".bin":
        for i in range(32768):
            dx7data.append(data[i]&127)
        dx72data += dx7.initamem()*256

    if size >= 49170:
        for i in range(size-49166):
            if data[i]==0xf0 and data[i+1]==0x43 and dxcommon.list2string(data[i+6:i+14])=="LM  GMRE":
                for p in range(128*32):
                    d2 = data[i+16+2*p] & 15
                    d1 = data[i+16+2*p+1] & 15
                    data[p] = (d2<<4) + d1
                #dx7data += data[:128*32]
                for p in range(32):
                    dx7data += dx7.cleanvmem(data[128*p:128*p+128])
                dx72data += dx7.initamem()*32

    #packed 32 voices
    if size>4101:
        for i in range(size-4098):
            #data[i+4] should be 0x20 but often is 0x10 
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x09 and (data[i+4]==0x10 or data[i+4]==0x20) and data[i+5]==0x00 and data[i+6+4097]==0xf7:
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+4096]) == data[i+6+4096]):
                    dx7data += data[i+6:i+6+4096]
                else:
                    dx7data += dx7.initvmem()*32
                channel = data[i+2]
        for i in range(size-1122):
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x06 and data[i+4]==0x08 and data[i+5]==0x60 and data[i+6+1121]==0xf7:
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+1120]) == data[i+6+1120]): 
                    dx72data += data[i+6:i+6+1120]
                else:
                    dx72data += dx7.initamem()*32
                channel=data[i+2]
    
    
    # Yamaha DX21/TX81Z VMEM
    for i in range(size-4098):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x04 and data[i+4]==0x20 and data[i+5]==0x00 and data[i+6+4097]==0xf7:
            print ("! 4op to 6op conversion")
            if (check==False) or (dxcommon.checksum(data[i+6:i+6+4096])==data[i+6+4096]):
                for p in range(32):
                    dx7data += fourop.vmm2vmem(data[128*p+i+6:128*(p+1)+i+6])[0]
                    dx72data += fourop.vmm2vmem(data[128*p+i+6:128*(p+1)+i+6])[1]
            else:
                dx7data += dx7.initvmem()*32
                dx72data += dx7.initamem()*32

    vcd = []
    for i in range(size-95):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x03 and data[i+4]==0x00 and data[i+5]==0x5d:
            #VCED
            vcd += data[i+6:i+6+93]
    
    acd2 = []
    for i in range(size-12):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+5]==0x14 and dxcommon.list2string(data[i+6:i+16])=='LM__8023AE':
            #ACED2
            acd2 += data[i+16:i+16+10]
    
    acd = []
    for i in range(size-25):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+5]==0x21 and dxcommon.list2string(data[i+6:i+16])=='LM__8976AE':
            #ACED
            acd += data[i+16:i+16+23]
    
    count = len(vcd)//93
    delay = fourop.initdelay()*count
    efeds = fourop.initefeds()*count
    acd3 = fourop.initacd3()*count
    if len(acd2) != 10*count: acd2 = fourop.initacd2()*count
    if len(acd) != 23*count: acd = fourop.initacd()*count

    for v in range(count):
        vmm = fourop.vcd2vmm(
            vcd[93*v:93*(v+1)], 
            acd[23*v:23*(v+1)], 
            acd2[10*v:10*(v+1)], 
            acd3[20*v:20*(v+1)], 
            efeds[3*v:3*(v+1)], 
            delay[2*v:2*(v+1)]
            )
        dx7data += fourop.vmm2vmem(vmm)[0]
        dx72data += fourop.vmm2vmem(vmm)[1]

    # Yamaha FB01 RAM and ROM voicebanks
    for i in range(size-6360):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x75 and data[i+3]<=0x0f and data[i+6362]==0xf7:
            print ("! FB01 to 6op conversion")
            for p in range(48):
                fb=[]
                if (check==False) or (dxcommon.checksum(data[i+76+131*p:i+76+131*p+128])==data[i+76+131*p+128]):
                    for n in range(64):
                        fb.append(data[i+76+131*p+2*n] + (data[i+76+131*p+2*n+1]<<4))
                    dx7data += fb01.fb2vmem(fb)[0] 
                    dx72data += fb01.fb2vmem(fb)[1]  
                else:
                    dx7data += dx7.initvmem()
                    dx72data += dx7.initamem()

    # Yamaha FB01 voice bank 0
    for i in range(size-6357):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x0c and data[i+6359]==0xf7:
            print ("! FB01 to 6op conversion")
            for p in range(48):
                fb=[]
                if (check==False) or (dxcommon.checksum(data[i+73+131*p:i+73+131*p+128])==data[i+73+131*p+128]):
                    for n in range(64):
                        fb.append(data[i+73+131*p+2*n] + (data[i+73+131*p+2*n+1]<<4))
                    dx7data += fb01.fb2vmem(fb)[0]
                    dx72data += fb01.fb2vmem(fb)[1]
                else:
                    dx7data += dx7.initvmem()
                    dx72data += dx7.initamem()

    # Yamaha FB01 instrument 1~8
    for i in range(size-136):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x75 and data[i+3]<=0x0f and (data[i+4]&8) and data[i+138]==0xf7:
            print ("! FB01 to 6op conversion")
            fb=[]
            if (check==False) or (dxcommon.checksum(data[i+9:i+9+128])==data[i+9+128]):
                for n in range(64):
                    fb.append(data[i+9+2*n] + (data[i+9+2*n+1]<<4))
                dx7data += fb01.fb2vmem(fb)[0]
                dx72data += fb01.fb2vmem(fb)[1]
            else:
                dx7data += dx7.initvmem()
                dx72data += dx7.initamem()


    # TX7 1 Performance
    for i in range(size-96):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x01 and data[i+4]==0x00 and data[i+5]==0x5e:
            if (check==False) or (dxcommon.checksum(data[i+6:i+6+94])==data[i+6+94]):
                tx7data += tx7.pced2pmem(data[i+6:i+6+94])
            else:
                tx7data += tx7.initpmem()

    # TX7 32+32 Performances
    for i in range(size-4098):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x02 and data[i+4]==0x20 and data[i+5]==0x00:
            if (check==False) or (dxcommon.checksum(data[i+6:i+6+4096])==data[i+6+4096]):
                tx7data += data[i+6:i+6+2048]
            else:
                tx7data += tx7.initpmem()
    
    # PSS 480/580/680/780
    for i in range(size-68):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x76 and data[i+3]==0x00 and data[i+71]==0xf7:
            if (check==False) or (dxcommon.checksum(data[i+4:i+4+66])==data[i+4+66]):
                print ("!! PSS-480/580/680 2-OP to 6-OP conversion")
                pss=[]    
                for n in range(33):
                    pss.append((data[i+4+2*n]<<4) + data[i+4+2*n+1])
                dx7data += pssx80.pss2vmem(pss, infile)
            else:
                dx7data += dx7.initvmem()
            dx72data += dx7.initamem()

    # Yamaha Reface DX sysex
    if size>238:
        rdxdat = []
        for i in range(size-40): 
            rdxhead = data[i:i+11]
            rdxhead[2] = 0
            if rdxhead == [0xf0, 0x43, 0x00, 0x7f, 0x1c, 0x00, 0x2a, 0x05, 0x30, 0x00, 0x00]:
                channel = data[i+2]
                rdxdat = data[i+11:i+11+38]
            elif rdxhead == [0xf0, 0x43, 0x00, 0x7f, 0x1c, 0x00, 0x20, 0x05, 0x31, 0x00, 0x00]:
                rdxdat += data[i+11:i+11+28]
            elif rdxhead == [0xf0, 0x43, 0x00, 0x7f, 0x1c, 0x00, 0x20, 0x05, 0x31, 0x01, 0x00]:
                rdxdat += data[i+11:i+11+28]
            elif rdxhead == [0xf0, 0x43, 0x00, 0x7f, 0x1c, 0x00, 0x20, 0x05, 0x31, 0x02, 0x00]:
                rdxdat += data[i+11:i+11+28]
            elif rdxhead == [0xf0, 0x43, 0x00, 0x7f, 0x1c, 0x00, 0x20, 0x05, 0x31, 0x03, 0x00]:
                rdxdat += data[i+11:i+11+28]
            if len(rdxdat) == 150:
                print("!! RefaceDX to DX7 conversion")
                dx7data += reface.rdx2vmem(rdxdat)[0]
                dx72data += reface.rdx2vmem(rdxdat)[1] 
                rdxdat = []

    # KORG 707 KORG DS8
    for i in range(size-7435): #100 programs bank
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and data[i+3] in (0x13, 0x1a) and data[i+4]==0x4c and data[i+11] != 0xf7:
            ds8 = False
            if data[i+3] == 0x13: # and data[i+7549] == 0xf7:
                print ("!! Korg DS8 bank import")
                ds8 = True
            else:
                print ("!! Korg 707 bank import")
            korgmid = data[i+5:i+5+7544]
            korgdat = korg.korg7to8(korgmid)
            for i in range(100):
                dx7data += korg.bnk2vmem(korgdat[66*i:66*(i+1)], ds8)[0]
                dx72data += korg.bnk2vmem(korgdat[66*i:66*(i+1)], ds8)[1]
                #vmm = korg.bnk2vmm(korgdat[66*i:66*(i+1)], ds8)
                #dx7data += fourop.vmm2vmem(vmm)[0]
                #dx72data += fourop.vmm2vmem(vmm)[1]
 
    for i in range(size-97): #1 program
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and (data[i+3] in (0x1a, 0x13)) and data[i+4]==0x40:
            if data[i+3] == 0x13:
                print ("!! Korg DS8 single patch import")
                ds8 = True
            else:
                print ("!! Korg 707 single patch import")
                ds8 = False
            korgmid = data[i+5:i+5+96]
            korgdat = korg.korg7to8(korgmid)
            dx7data += korg.vce2vmem(korgdat, ds8)[0]
            dx72data += korg.vce2vmem(korgdat, ds8)[1]
            #vmm = korg.vce2vmm(korgdat, ds8)
            #dx7data += fourop.vmm2vmem(vmm)[0]
            #dx72data += fourop.vmm2vmem(vmm)[1]

    # KORG Z3 all sound
    for i in range(size-12800):
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and data[i+3]==0x1d and data[i+4]==0x4c:
            print ("!! Korg Z3 import (experimental)")
            for p in range(128):
                vmm = korgz3.z3_to_vmm(data[5+100*p:105+100*p])
                dx7data += fourop.vmm2vmem(vmm)[0]
                dx72data += fourop.vmm2vmem(vmm)[1]

    # ORLA DSE 12/24
    for i in range(size-70):
        if data[i:i+7] == [0xf0, 0x00, 0x42, 0x6f, 0x68, 0x6d, 0x05]:
            print ("!! Bohm/Orla 12/24 import (experimental)")
            bhm = data[i+8:i+8+64]
            pp = data[i+7]
            if size == 8300: #UNI_MAN Bohm/Orla 12/24 adaptor
                pn = data[10*pp:10*pp+10]
            else:
                pn = dxcommon.string2list("{:02}--------".format(pp))
            vmm = bohmorla.bhm2vmm(bhm, pn)
            dx7data += fourop.vmm2vmem(vmm)[0]
            dx72data += fourop.vmm2vmem(vmm)[1]

    # BOHM 4x9
    for i in range(size-94):
        if data[i:i+7] == [0xf0, 0x00, 0x42, 0x6f, 0x68, 0x6d, 0x12]:
            print ("!! Bohm 4x9 import (experimental)")
            bhm = data[i+9:i+9+88]
            vmm = bohmorla.fourxnine2vmm(bhm)
            dx7data += fourop.vmm2vmem(vmm)[0]
            dx72data += fourop.vmm2vmem(vmm)[1]

    # WAV data with datacassette dump
    if ext == '.wav': 
        dd = wav2syx.wav2syx(infile, 'dx')
        dx7data += dd
        dx72data += dx7.initamem() * (len(dd)//128)

    # MidiQuest TX81Z SQL
    if ext == ".sql" and dxcommon.list2string(data[:4]) == "LIST" and dxcommon.list2string(data[0x20:0x20+12]) == "Yamaha TX81Z":
        for i in range(size-128):
            if dxcommon.list2string(data[i:i+6]) == "ccc222":
                dx7data += fourop.vmm2vmem(data[i-67:i-67+128])[0]
                dx72data += fourop.vmm2vmem(data[i-67:i-67+128])[1]

    # Bowker/Henderson/Michelson TX81Z/DX11 Librarian (.PAT)
    if ext == ".pat" and data[:11] == [0x00, 0x4C, 0x4D, 0x20, 0x20, 0x38, 0x39, 0x37, 0x36, 0x41, 0x45]:
        #ACED 1+10+23 + VCED 1+93+1 = 129 
        for i in range(len(data)/129):
            txdata = fourop.vcd2vmm(data[129*i+35:129*i+35+93], data[129*i+1:129*i+1+23])
            dx7data += fourop.vmm2vmem(txdata)[0]
            dx72data += fourop.vmm2vmem(txdata)[1]
    
    # Still not found anything? Then keep searching ...
    if dx7data != []:
        pass

    elif os.path.basename(infile) == "SuperDXLib" and size == 1455808:
        for i in range(4529):
            dx7data += dx7.vced2vmem(data[128+256*i:128+256*i+155])

    #Dr.T TX7 files, Steinberg
    elif (ext in (".snd", ".tx7")) and size==8192:
        dx7data += data[:4096]
        tx7data += data[4096:4096+2048]

    #Transform XSyn
    elif ext==".bnk" and size==8192:
        for i in range(32):
            dx7data += data[256*i:256*i+128]
            tx7data += data[256*i+128:256*i+192]

    #DX200 DX2
    elif ext==".dx2" and size==326454:
        for patch in range(128):
            dx7data += dx200.dx2tovmem(data[34+patch*381:34+(patch+1)*381])
            dx72data += dx200.dx2toamem(data[34+patch*381:34+(patch+1)*381])

    #Yamaha DX Simulator DXC
    elif ext==".dxc" and size==18004:
        for patch in range(64):
            dx7data += dx200.dx2tovmem(data[20+patch*281:20+(patch+1)*281])
            dx72data += dx200.dx2toamem(data[20+patch*281:20+(patch+1)*281])

    #Voyetra SIDEMAN and PATCHMASTER
    elif data[0:4] == [0xdf, 0x05, 0x01, 0x00]:
        if ext==".b13" and size==5663:
            if dxcommon.list2string(data[6:19]) == "YAMAHA DX7/TX":
                dx7data += data[0x060f:0x160f]
                dx72data += 32*dx7.initamem()

        if ext == ".b15" and size==10755:
            if dxcommon.list2string(data[6:18]) == "YAMAHA TX81Z":
                for i in range(32):
                    dx7data += fourop.vmm2vmem(data[0x060f+128*i:0x60f+128*(i+1)])[0]
                    dx72data += fourop.vmm2vmem(data[0x060f+128*i:0x60f+128*(i+1)])[1]

        if ext == ".b16" and size == 20837:
            if dxcommon.list2string(data[6:18]) == "YAMAHA FB-01":
                for bank in range(2):
                    for i in range(48):
                        fbdata = []
                        for p in range(64):
                            lo = data[0x2029*bank + 0x0821 + 130*i + 2*p] & 15
                            hi = (data[0x2029*bank + 0x0821 + 130*i+ 2*p + 1] & 15) << 4
                            fbdata.append(lo+hi)
                        dx7data += fb01.fb2vmem(fbdata)[0]
                        dx72data += fb01.fb2vmem(fbdata)[1]

        if ext == ".b68" and size==9816:
            if dxcommon.list2string(data[6:16]) == "SIDEMAN DX":
                dx7data += data[0x60f:0x160f]
                for i in range(32):
                    tx7data += data[0x1bd8+84*i:0x1bd8+84*i+64]
        
    # DX7IIFD floppy data
    elif ext[:2] ==".i" and size==16384:
        dx7data = data[0x2000:0x4000]
        for i in range(32):
            dx72data += data[0x1980+26*i:0x1980+26*(i+1)]
            dx72data += data[0x1740+9*i:0x1740+9*(i+1)]
        for i in range(32):
            dx72data += data[0x1cc0+26*i:0x1cc0+26*(i+1)]
            dx72data += data[0x1860+9*i:0x1860+9*(i+1)]

    # DX7 Steinberg Synthworks/Satellit SND
    elif ext==".snd" and size==5216:
        dx7data = data[:4096]
        dx72data += 32*dx7.initamem()

    # FM-Alive DX Manager DXM
    elif ext == ".dxm" and data[:7] == [0xfc, 0, 0, 0, 0x44, 0x58, 0x4d] and size>256:
        if dxcommon.list2string(data[0xfd:0xfd+3]) != 'OP4':
            for i in range(255, size-159):
                if data[i:i+4] == [155, 0, 0, 0]:
                    dx7data += dx7.vced2vmem(data[i+4:i+159])
                    if data[i+159:i+163] == [49, 0, 0, 0]:
                        dx72data += dx7.aced2amem(data[i+163:i+163+49])
                    else:
                        dx72data += dx7.initamem()
                if data[i:i+4] == [128, 0, 0, 0]:
                    dx7data += data[i+4:i+132]
                    if data[i+132:i+136] == [35, 0, 0, 0]:
                        dx72data += data[i+136:i+136+35]
                    else:
                        dx72data += dx7.initamem()

    # Soundlib SLB
    elif ext==".slb" and size>138:
        for i in range(size-139):
            if data[i:i+11] == [0x00, 0x00, 0x08, 0x44, 0x58, 0x37, 0x56, 0x6F, 0x69, 0x63, 0x65]:
                dx7data += data[i+11:i+11+128]
                dx72data += dx7.initamem()


    # Opcode Galaxy Yamaha DX7
    elif size==4170 and data[0x1c:0x1c+10]==[0x59, 0x61, 0x6d, 0x61, 0x68, 0x61, 0x20, 0x44, 0x58, 0x37]:
        dx7data += data[0x42:0x42+4096]
        dx72data += 32*dx7.initamem()
    elif dxcommon.list2string(data[0x1c:0x27]) == "TX81Z Voice":
        for i in range((size-66)//84):
            vmm = fourop.initvmm()
            vmm[:84] = data[0x42 + 84*i: 0x42 + 84*(i+1)]
            dx7data += vmm2vmem(vmm)[0]
            dx72data += vmm2vmem(vmm)[1]
    elif data[0x48:0x48+6] == data[0x9c:0x9c+6] == data[0xf0:0xf0+6] == [0x63, 0x63, 0x63, 0x32, 0x32, 0x32]:
        for i in range((size-5)//84):
            vmm = fourop.initvmm()
            vmm[:84] = data[5 + 84*i: 5 + 84*(i+1)]
            dx7data += vmm2vmem(vmm)[0]
            dx72data += vmm2vmem(vmm)[1]

    # Opcode Galaxy DX7II
    elif size==0x2948 and data[0x1c:0x1c+13]==[0x44, 0x58, 0x37, 0x20, 0x49, 0x49, 0x20, 0x56, 0x6F, 0x69, 0x63, 0x65, 0x73]:
        for i in range(64):
            dx7data += data[164*i + 0x42:164*i + 0x42 + 128]
            dx72data += data[164*i + 0xc2:164*i + 0xc2 + 35]

    # Opcode Galaxy TX81Z
    elif size == 4876 and dxcommon.list2string(data[0x1d:0x29]) == "Yamaha TX81Z":
        for i in range(32):
            vmm = fourop.initvmm()
            vmm[:84] = data[0x7b3 + 84*i: 0x7b3 + 84*(i+1)]
            dx7data += fourop.vmm2vmem(vmm)[0]
            dx72data += fourop.vmm2vmem(vmm)[1]

    # C-Lab X-ALyzer XAL
    elif ext==".xal":
        for i in range(32*(size//8000)):
            dx7data += data[252+250*i:380+250*i]
            dx72data += data[380+250*i:415+250*i]
    
    # Amiga DXEditor093
    elif data[:10] == [0x46, 0x4f, 0x52, 0x4d, 0, 0, 0, 0, 0x44, 0x78]:
        for i in range((size-12)//212):
            vced=[]
            for oop in range(6):
                op=5-oop
                vced += data[12+212*i+22*op:12+212*i+22*op+20]
                if data[12+212*i+22*op+20]&128 == 128:
                    vced += [(data[12+212*i+22*op+20]&7)-1]
                else:
                    vced += [7+(data[12+212*i+22*op+20]&7)]
            vced += data[12+212*i+132:12+212*i+132+19]
            vced += data[12+212*i+152:12+212*i+162]
            dx7data += dx7.vced2vmem(vced)
            dx72data += dx7.initamem()
    
    # Marc Bareille SynLib DX-TX DXL
    elif ext==".dxl" and size==4128320:
        for patch in range(32000):
            if data[129*patch:129*patch+118] != [0]*118:
                dx7data += data[129*patch:129*(patch+1)-1]
                dx72data += dx7.initamem()

    # Metrasound DX Supervisor DXL CLP
    elif ext==".dxl" and data[:4] == [0x44, 0x58, 0x53, 0x4c]:
        dx7dat = data[(len(data) - 10) % 128:]
        dx7data += dx7dat
        dx72data += dx7.initamem() * (len(dx7dat) // 128)
    elif ext==".clp" and data[:4] == [0x44, 0x58, 0x53, 0x43]:
        dx7dat = data[(len(data) - 10) % 128:]
        dx7data += dx7dat
        dx72data += dx7.initamem() * (len(dx7dat) // 128)

    # Emagic Sounddiver
    elif ext == ".lib" and data[:4] == [0x4d, 0x52, 0x4f, 0x46]:
        for i in range(size-158):
            if data[i:i+4] == [0x54, 0x4e, 0x45, 0x4c]:
                nmlen=data[i+21]
                if data[i+22+nmlen:i+25+nmlen] == [0x03, 0x81, 0x19]:
                    dx7data += data[i+25+nmlen:i+25+nmlen+118]
                    dx7data += data[i+22:i+22+nmlen] + [32]*(10-nmlen)
                    dx72data += data[i+25+nmlen+118:i+25+nmlen+118+35]
                    i += 127+27
                elif data[i+42+nmlen:i+45+nmlen] == [0x03, 0x83, 0x0f]:
                    dx7data += data[i+45+nmlen:i+45+nmlen+118]
                    dx7data += data[i+22:i+22+nmlen] + [32]*(10-nmlen)
                    dx72data += data[i+45+nmlen+118:i+45+nmlen+118+35]
                    i += 127+47
                elif data[i+nmlen+22:i+nmlen+29] == [0x03, 0x7c, 0x54, 0x58, 0x38, 0x31, 0x5a]:
                    vmm = fourop.initvmm()
                    vmm[:50] = data[i+nmlen+30:i+nmlen+30+50]
                    vmm[57:57+nmlen] = data[i+22:i+22+nmlen]
                    vmm[57:57+nmlen] = data[i+22:i+22+nmlen]
                    vmm[57+nmlen:67] = [32]*(10-nmlen)
                    vmm[67:84] = data[i+nmlen+30+57:i+nmlen+30+74]
                    dx7data += fourop.vmm2vmem(vmm)[0]
                    dx72data += fourop.vmm2vmem(vmm)[1]
                   

    # C-Lab PolyFrame
    elif ext == ".pl" and dxcommon.list2string(data[:13]) == "PolyFrame Lib":
        for i in range(len(data)-4):
            if data[i:i+4] == dxcommon.string2list('DX7')+[0]:
                data_start = i+4
                for n in range(i-14, i):
                    if data[n:n+2] == [0x60, 0]:
                        name_start = n+4
                        dx7dat = 118*[0]+10*[32]
                        dx7dat[:118] = data[data_start:data_start+118]
                        dx7dat[118:118+(i-name_start)] = data[name_start:i]
                        dx7data += dx7dat
            elif data[i:i+6] == dxcommon.string2list('DX7II')+[0]:
                data_start = i+6
                for n in range(i-14, i):
                    if data[n:n+2] == [0x60, 0] and (i-n>5):
                        name_start = n+4
                        dx7dat = 118*[0]+10*[32]
                        dx7dat[:118] = data[data_start:data_start+118]
                        dx7dat[118:118+(i-name_start)] = data[name_start:i]
                        dx7data += dx7dat
                    elif data[n:n+2] == [0x60, 0] and (i-n==5):
                        dx72data += data[data_start:data_start+35]
            elif data[i:i+6] == dxcommon.string2list('TX802')+[0]:
                data_start = i+6
                for n in range(i-14, i):
                    if data[n:n+2] == [0x60, 0] and (i-n>5):
                        name_start = n+4
                        dx7dat = 118*[0]+10*[32]
                        dx7dat[:118] = data[data_start:data_start+118]
                        dx7dat[118:118+(i-name_start)] = data[name_start:i]
                        dx7data += dx7dat
                    elif data[n:n+2] == [0x60, 0] and (i-n==5):
                        dx72data += data[data_start:data_start+35]

    # GenEdit TX7
    elif size==4172 and ext==".tx7":
        dx7data += data[64:64+4096]
        dx72data += dx7.initamem()*32

    # DX7 Librarian (Mac)
    elif ext == ".dx7lib":
        #import base64
        #import xml.etree.ElementTree as ET
        tree = ET.parse(infile)
        root = tree.getroot()
        vmemkey = False
        vcedkey = False
        for key in root.findall('./dict/key'):
            if key.text == "DX7Multi":
                vmemkey = True
                break
            if key.text == "DX7Single":
                vcedkey = True
                break
            if key.text == "MIDI channel":
                pass
        if vmemkey:
            for d in root.findall("./dict/array/data"):
                dx7data += list(bytearray(base64.b64decode(d.text)))
                dx72data += dx7.initamem()
        if vcedkey:
            d = root.findall("./dict/data")[1]
            dx7data += dx7.vced2vmem(list(bytearray(base64.b64decode(d.text))))

    # Dr.T FourOp de Luxe and TXconvert headerless raw sysex
    elif size%128 == 0 and ext==".dxx":
        print ("! 4op to 6op conversion")
        for i in range(size//128):
            if sum(data[128*i+118:128*i+128])==0 and sum(data[128*i:128*i+118])!=0:
                dx7data += fourop.vmm2vmem(data[128*i:128+128*i])[0]
                dx72data += fourop.vmm2vmem(data[128*i:128+128*i])[1]

    #Musicode V50 Voice Development System (.VBL)
    if ext == ".vlb" and dxcommon.list2string(data[:16]) == "YSVLYSVLYSVLYSVL":
        print ("! 4op to 6op conversion")
        for i in range(100):
            dx7data += fourop.vmm2vmem(data[4848+128*i:4848+128*(i+1)])[0]
            dx72data += fourop.vmm2vmem(data[4848+128*i:4848+128*(i+1)])[1]
        
    # X-OR V50
    elif size==24576 and ext==".v5b":
        print ("! 4op to 6op conversion")
        for i in range(100):
            dx7data += fourop.vmm2vmem(data[128*i:128*(i+1)])[0]
            dx72data += fourop.vmm2vmem(data[128*i:128*(i+1)])[1]

    # X-OR TX81Z
    elif size==6538 and ext==".txz":
        print ("! 4op to 6op conversion")
        for i in range(32):
            dx7data += fourop.vmm2vmem(data[128*i:128*(i+1)])[0]
            dx72data += fourop.vmm2vmem(data[128*i:128*(i+1)])[1]

    # V50 internal disk SYN format
    elif size in (17729, 26624) and ext[:-2]==".i" and ext[2:].isdigit():
        print ("! 4op to 6op conversion")
        for i in range(100):
            try:
                vmm = data[13824+128*i:13824+128*(i+1)]
                if vmm[86]<50:
                    vmm[86] += 51
                else:
                    vmm[86] -= 50
                dx7data += fourop.vmm2vmem(vmm)[0]
                dx72data += fourop.vmm2vmem(vmm)[1]
            except:
                break

    # V50 YS MCD32 V50 disk
    elif size == 32768 and data[4:10] == [0x59, 0x53, 0x20, 0x53, 0x2f, 0x56]: #"YS S/V"
        for b in range(4):
            for p in range(25):
                vmm = data[0x1000 + 0x2000*b + 128*p : 0x1000 + 0x2000*b + 128*(p+1)]
                if vmm[86]<50:
                    vmm[86] += 51
                else:
                    vmm[86] -= 50
                dx7data += fourop.vmm2vmem(vmm)[0]
                dx72data += fourop.vmm2vmem(vmm)[1]
    elif size == 32768 and data[4:10] == [0x56, 0x35, 0x30, 0x53, 0x59, 0x4e]: #"V50SYN"
        for b in range(4):
            for p in range(25):
                vmm = data[0x3900 + 0xc80*b + 128*p : 0x3900 + 0xc80*b + 128*(p+1)]
                if vmm[86]<50:
                    vmm[86] += 51
                else:
                    vmm[86] -= 50
                dx7data += fourop.vmm2vmem(vmm)[0]
                dx72data += fourop.vmm2vmem(vmm)[1]

    # m.gregory's TX81Z Programmer .tx8
    elif ext=='.tx8' and data[:5] == [0x54, 0x58, 0x38, 0x31, 0x5a]:        
        for i in range((size-9)//173):
            dx7data += fourop.vmm2vmem(data[54+173*i:54+173*i+128])[0]
            dx72data += fourop.vmm2vmem(data[54+173*i:54+173*i+128])[1]

    # AudioGrill TX81Z/DX11 Voice Archive
    elif dxcommon.list2string(data[:26]) == "* TX81Z/DX11 Voice Archive":
        txdat = []
        numbers = []
        hexnum = '0123456789abcdef'
        with open(infile, 'r') as f:
            lines = f.readlines()
        for ll in lines:
            if ll[:1] in hexnum:
                for l in ll:
                    if l in hexnum:
                        numbers.append(hexnum.index(l))
        for i in range(len(numbers)//2):
            txdat.append (16*numbers[2*i] + numbers[2*i+1]) 
        for i in range(len(txdat)//128):
            dx7data += fourop.vmm2vmem(txdat[128*i:128*i+128])[0]
            dx72data += fourop.vmm2vmem(txdat[128*i:128*i+128])[1]

    # Tim Thompson's Glib tx81z dx100 editor
    elif data[0]==0xdd and (ext in ('.dx1', '.tx8')) and size==4097:
        dx7data += fourop.vmm2vmem(data[1:4097])[0]
        dx72data += fourop.vmm2vmem(data[1:4097])[1]

    # Tim Thompson's Glib dx7s
    elif data[0]==0xd7 and ext=='.d7s' and size==5217:
        for i in range(32):
            dx7data += data[1+163*i:1+163*i+128]
            dx72data += data[1+163*i+128:1+163*i+128+35]

    # Synthworks 4OP
    elif ext=='.bnk' and size==4032 and data[0]==0x0a:
        for i in range(32):
            txdat = fourop.steinb2vmm(data[1+12*i:11+12*i], data[0x180+114*i:0x180+114*(i+1)])
            dx7data += fourop.vmm2vmem(txdat)[0]
            dx72data += fourop.vmm2vmem(txdat)[1]
    elif ext=='.snd' and size==126 and data[0]==0x0a:
        txdat = fourop.steinb2vmm(data[1:11], data[12:])
        dx7data += fourop.vmm2vmem(txdat)[0]
        dx72data += fourop.vmm2vmem(txdat)[1]

    # Caged Artist FB01
    elif size==8768 and ext==".fb1":
        print ("! FB01 to 6op conversion")
        for bnk in range(2):
            for i in range(48):
                dx7data += fb01.fb2vmem(data[32+3104*bnk+64*i:32+3104*bnk+64*(i+1)])[0]
                dx72data += fb01.fb2vmem(data[32+3104*bnk+64*i:32+3104*bnk+64*(i+1)])[1]
    
    # Dr.T FB01 48 * 64 bytes / raw data
    elif (size % 64 == 0) and ext==".fb1":
        print ("! FB01 to 4op TX/DX conversion")
        for i in range(48):
            dx7data += fb01.fb2vmem(data[64*i:64*(i+1)])[0]
            dx72data += fb01.fb2vmem(data[64*i:64*(i+1)])[1]

    # Frederic Meslin FB01 editor
    elif size==354 and ext==".fbv":
        pass
        #print ("**! FB01 to 4op TX/DX conversion")
        #dx7data += fb01.fb2vmem(data[0x107:0x107+64])[0]
        #dx72data += fb01.fb2vmem(data[0x107:0x107+64])[1]

    # CX5M VOG
    elif size in (3079, 3111) and ext==".vog":
        for i in range(47):
            fb = data[0x27 + 64*i:0x27 + 64*(i+1)]
            dx7data += fb01.fb2vmem(fb)[0]
            dx72data += fb01.fb2vmem(fb)[1]

    #CX5M YRM305
    elif ext == '.d21' and size == 2375:
        for i in range(32):
            vmm = fourop.initvmm()
            vmm[:73] =  data[39+73*i:39+73*(i+1)]
            dx7data += fourop.vmm2vmem(vmm)[0]
            dx72data += fourop.vmm2vmem(vmm)[1]

    elif size==2450 and ext==".fbd":
        print ("! FB01 to 4op TX/DX conversion")
        for i in range(49):
            fb = 64*[0]
            fb[:7] = data[1+8*i:8+8*i]
            fb[8:48] = data[0x188+42*i:0x1b0+42*i]
            fb[58:60] = data[0x1b0+42*i:0x1b2+42*i]
            dx7data += fb01.fb2vmem(fb)[0]
            dx72data += fb01.fb2vmem(fb)[1]

    # TFM Music Maker instrument files
    elif ext == ".tfi" and size == 42:
        print ("!! TFM Music Maker instrument (.tfi) conversion")
        fbdat = fb01.tfm2fb(data, infile)
        dx7dat = fb01.fb2vmem(fbdat)[0]
        vname = os.path.basename(infile)[:-4] + "          "
        vname = vname[:10]
        dx7dat[118:128] = dxcommon.string2list(vname)
        dx7data += dx7dat
        dx72data += fb01.fb2vmem(fbdat)[1]

    # VOPM .OPM
    elif ext==".opm":
        dx7data = []
        dx72data = []
        tx7data = []
        print ("!! VOPM (.opm) to 6-OP conversion")
        data = vopm.file2data(infile)
        for i in range(len(data)//76):
            fb = vopm.vopm2fb01(data[76*i:76*(i+1)])
            dx = fb01.fb2vmem(fb)[0]
            dx[118:128] = data[76*i:76*i+10]
            dx7data += dx
            dx72data += fb01.fb2vmem(fb)[1]

    # datacassette data from TX7
    # extracted using Martin Ward's tape-read perl script with baud=1200
    elif ext == ".txt" and data[:13] == wav2syx.tx7head:
        for i in range(32):
            dx7data += wav2syx.cas2vmem(data, 14 + 128*i)
            dx72data += dx7.initamem()

    # datacassete data from DX21/27/100/11/TX81Z 
    # extracted using Martin Ward's tape-read perl script with baud=1200
    elif ext == ".txt" and size>64:
        if sum(data[:65]) == 256*data[65] + data[66]: #DX9
            dx7data += wav2syx.dx9cas2vmem(data, 0)
            dx72data += dx7.initamem()
        else:
            txdata = wav2syx.cas2vmm(data, 0)
            dx7data += fourop.vmm2vmem(txdata)[0]
            dx72data += fourop.vmm2vmem(txdata)[1]

    # datacassette data extracted using wav2cas
    elif ext == ".cas":
        if data[8:8+13] == wav2syx.tx7head: # "YMTX7"
            for i in range(32):
                dx7data += wav2syx.cas2vmem(data, 22 + 128*i)
                dx72data += dx7.initamem()
        elif data[8+32:8+13+32] == wav2syx.tx7head: # "YMTX7"
            for i in range(32):
                dx7data += wav2syx.cas2vmem(data, 22 + 128*i + 32)
                dx72data += dx7.initamem()
        elif data[46:51] == dxcommon.string2list("YMDX7"): #YRM-103 DX7 editor CX5M
            for i in range(48):
                dx7data += wav2syx.cas2vmem(data, 54 + 128*i)
                dx72data += dx7.initamem()
        elif data[:8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
            if data[0x12:0x18] == dxcommon.string2list("VOICE "):
                for i in range(48):     
                    fbdat = []
                    if data[0x20:0x28] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                        fbdat = data[0x4e+64*i:0x4e+64*(i+1)]
                    elif data[0x28:0x30] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                        fbdat = data[0x56+64*i:0x56+64*(i+1)]
                    dx7data += fb01.fb2vmem(fbdat)[0]
                    dx72data += fb01.fb2vmem(fbdat)[1]
            else:
                for i in range(len(data)-84):
                    if data[i:i+8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                        if sum(data[i+8:i+8+65]) == 256*data[i+8+65] + data[i+8+66]:
                            dd = wav2syx.dx9cas2vmem(data, i + 8)
                            dx7data += dd
                            dx72data += dx7.initamem() * (len(dd)//128)
                        else:
                            txdata = wav2syx.cas2vmm(data, i + 8)
                            dx7data += fourop.vmm2vmem(txdata)[0]
                            dx72data += fourop.vmm2vmem(txdata)[1]

    # Atari PSSED pss480-780 library with 100 patches
    elif ext == ".lib" and size == 4908:
        print ("!! PSS-480/580/680 2-OP to 6-OP conversion")
        for i in range(100):
            voicename = dxcommon.list2string(data[8+16*i:8+16*(i+1)])
            dx7data += pssx80.pss2vmem(data[1608+33*i:1608+33*(i+1)], infile, voicename)
            dx72data += dx7.initamem()

    # Bryan Sutula TX81Z/DX11 Voice Archive
    elif data[:26] == dxcommon.string2list("* TX81Z/DX11 Voice Archive"):
        hx = "0123456789abcdef"
        with open(infile, 'r') as f:
            datatxt = f.readlines()
        for i in range(len(datatxt)):
            if datatxt[i].startswith("** Source:"):
                hextext = ''
                txdat = []
                for l in range(1,7):
                    hextext = datatxt[i+l].strip()
                    for n in range(1 + len(hextext)//3):
                        txdat.append (16*(hx.index(hextext[3*n])) + hx.index(hextext[3*n+1]))
                dx7data += fourop.vmm2vmem(txdat)[0]
                dx72data += fourop.vmm2vmem(txdat)[1]

    # P-Farm
    elif ext==".pfm" and data[:4] == [0x50, 0x46, 0x72, 0x6d]: # "PFrm"
        pass
     
    # single VCED 
    elif (size%155)==0:
        if (size%128)!=0:
            for i in range(size//155):
                dx7data += dx7.vced2vmem(data[155*i:155*(i+1)])

    # geminisolstice "Michael Jackson" collection Yamaha DX7, TX7 and TX816
    elif size>192:
        for n in (0, 1):
            sizecheck = (data[0]<<8) + data[1] + n
            if (size==2+(192*sizecheck)) or (size==32+(192*sizecheck)):
                for i in range(sizecheck):
                    dx7data += data[2+192*i:2+192*i+128]
                    tx7data += data[2+192*i+128:2+192*i+192]
            elif (size==2+(128*sizecheck)) or (size==32+(128*sizecheck)):
                for i in range(sizecheck):
                    dx7data += data[2+128*i:2+128*(i+1)]

    # Ignore many other SysEx
    if dx7data == []:
        for i in data[:64]:
            if i > 127:
                dx7data += dx7.initvmem()
                break

    # If everything fails: The worst thing that can happen is
    # creating a DX7 compatible but completely useless patchbank :-)
    # Should work with e.g. headerless 4096 bytes DX7 files
    if dx7data == []:
        dx7data += data[:128*(len(data)//128)]
    if dx72data == []:
        if len(tx7data)//64 == len(dx7data)//128:
            for i in range(len(dx7data)//128):
                dx72data += tx7.pmem2amem(tx7data[64*i:64*(i+1)])
        else:
            dx72data = dx7.initamem()*(len(dx7data)//128)
    if tx7data == []:
        if len(dx72data)//35 == len(dx7data)//128:
            for i in range(len(dx7data)//128):
                tx7data += tx7.amem2pmem(dx72data[35*i:35*(i+1)])
        else:
            tx7data = tx7.initpmem()*(len(dx7data)//128)

    # Safety garbage cleanup
    dx7dat = []
    dx72dat = []
    tx7dat = []
    initcount = 0
    for i in range(len(dx7data)//128):        
        if dxcommon.list2string(dx7data[128*i+118:128*i+128]) != "INIT VOICE":
            if dxcommon.list2string(dx7data[128*i+118:128*i+128]).strip() != "":
                dx7dat += dx7.cleanvmem(dx7data[128*i:128*(i+1)])
                dx72dat += dx7.cleanamem(dx72data[35*i:35*(i+1)])
                tx7dat += tx7.cleanpmem(tx7data[64*i:64*(i+1)])
        else:
            initcount += 1

    # restore INITVOICE
    dx7dat += dx7.initvmem() * initcount
    dx72dat += dx7.initamem() * initcount
    tx7dat += tx7.initpmem() * initcount

    return dx7dat, dx72dat, tx7dat, channel

def pre_write(dx7data, dx72data, tx7data, dx72, TX7):
    # AMS AMEM/VMEM correction and conversion
    ams=(0, 1, 2, 3, 3, 3, 3, 3)
    # ams=(0, 1, 1, 2, 2, 2, 3, 3)
    for p in range(len(dx7data)//128):
        for op in range(6):
            ams1=dx7data[128*p+17*(5-op)+13]&3
            if op in (0, 2, 4):
                ams2 = (dx72data[35*p+1+((5-op)//2)]//8)&7
            if op in (1, 3, 5):
                ams2 = dx72data[35*p+1+((5-op)//2)]&7
            if ams2 == 0:
                ams2 = ams1
            ams1 = ams[ams2]
            dx7data[128*p+17*(5-op)+13] = ams1 + (dx7data[128*p+17*(5-op)+13]&0b11100)
            if op in (0, 2, 4):
                dx72data[35*p+1+((5-op)//2)] = (dx72data[35*p+1+((5-op)//2)]&7) + 8*ams2
            if op in (1, 3, 5):
                dx72data[35*p+1+((5-op)//2)] = (dx72data[35*p+1+((5-op)//2)]&0b111000) + ams2
    # Change Key Scaling Mode from Fractional to Normal
    for p in range(len(dx72data)//35):
        dx72data[35*p]=0

    return dx7data, dx72data, tx7data

def write(outfile, dx7data, dx72data, tx7data, dx72, TX7, channel=0, nosplit=False, mid_out=MID_OUT, split=False):
    if outfile == os.devnull:
        nosplit = True
    dx7data, dx72data, tx7data = pre_write(dx7data, dx72data, tx7data, dx72, TX7)
    ext = os.path.splitext(outfile)[1]
    basename = os.path.split(outfile)[1]
    basename = os.path.splitext(basename)[0]
    dirname = os.path.dirname(outfile)
    mid = False
    if ext.lower() in (".mid", ".midi"):
        mid = True
    if ext.lower() == ".dx7":
        dx72 = False
    if dxcommon.ENABLE_MIDI:
        if outfile[-4:] == "MIDI":
            nosplit = True
 
    # PEG range DX7II AMEM to DX7 VMEM conversion:
    if dx72==False:
        for p in range(len(dx7data)//128):
            for i in range(106, 110):
                pegr=dx72data[35*p+4]&3
                peg=dx7data[128*p+i]
                # dx7data[128*p+i]=int((peg-50)*(50, 32, 18, 10)[pegr]/50.0) + 50
                dx7data[128*p+i]=int((peg-50)*(50, 32, 16, 8)[pegr]/50.0) + 50

    # DX7 "Rocksplit" correction
    rocksplit = (100, 102, 103, 104, 106, 107, 108, 109, 110, 115,
                  116, 118, 120, 121, 122, 123, 125, 126, 127)
    if dx72 or TX7:
        for p in range(len(dx7data)//128):
            for op in range(6):
                if dx7data[128*p + 14 + 17*op] in rocksplit: #TL
                    if dx7data[128*p + 11 + 17*op] >> 2 == 0: #RC
                        dx7data[128*p + 10 + 17*op] = 99 #RD
                    if dx7data[128*p +11 + 17*op] & 3 == 0: #LC
                        dx7data[128*p + 9 + 17*op] = 99
                    if dx72:
                        dx7data[128*p + 14 + 17*op] = 99 + 16 * (99 - dx7data[128*p + 14 + 17*op]) // 28

    if len(dx7data)>128:
        #Fill unused patch locations in 32-voice banks with INIT VOICE
        while len(dx7data)%4096 != 0:
            dx7data += dx7.initvmem()
            dx72data += dx7.initamem()
            tx7data += tx7.initpmem()
        patchcount=len(dx7data)//128
    elif len(dx7data) < 128:
        dx7data, dx72data, tx7data = dx7.initvmem(), dx7.initamem(), tx7.initpmem()
        patchcount = 1
    else:
        patchcount = 1

    dat=[]
    message = ''
    bankcount=max(1, len(dx7data)//4096)
    bankdigits=len(str(bankcount+1))
    for bank in range(bankcount):
        if len(dx7data)//4096>1 and nosplit==False:
            outfile=os.path.join(dirname, basename+"("+str(bank+1).zfill(bankdigits)+")"+ext)
        if nosplit==False:
            dat=[]

        if ext.lower()==".dx7":
            if patchcount==1:
                dat = dx7data[:128]
            else:
                dat += dx7data[4096*bank:4096*(bank+1)]

        elif ext.lower()==".txt":
            if patchcount==1 or len(dx7data) == 128:
                dat = dx7.vmem2txt(dx7data[:128])
                if dx72:
                    dat += dx7.amem2txt(dx72data[:35])
                if TX7:
                    dat += tx7.pmem2txt(tx7data[:64])
            else:
                t = ''
                for i in range(32):
                    t += "{:03}: {}\n".format(i+1+bank*32, dx7.voicename(dx7data[4096*bank+128*i:4096*bank+128*(i+1)]))
                t += "\n"

                for i in t:
                    dat.append(ord(i))
        
        else: # syx and mid files
            if patchcount==1: #save as VCED sysex
                if dx72:
                    dat += [0xf0, 0x43, channel, 0x05, 0x00, 0x31]
                    dat += dx7.amem2aced(dx72data[:35])
                    dat += [dxcommon.checksum(dx7.amem2aced(dx72data[:35])), 0xf7]
                dat += [0xf0, 0x43, channel, 0x00, 0x01, 0x1b]
                dat += dx7.vmem2vced(dx7data)
                dat += [dxcommon.checksum(dx7.vmem2vced(dx7data[:128])), 0xf7]
                if TX7:
                    dat += [0xf0, 0x43, channel, 0x01, 0x00, 0x5e]
                    dat += tx7.pmem2pced(tx7data)
                    dat += [dxcommon.checksum(tx7.pmem2pced(tx7data[:64])), 0xf7]
                
            else: #save as VMEM sysex
                if nosplit==True:
                    if patchcount > 32:
                        dat += [0xf0, 0x43, 0x10+channel, 0x19, 0x4d, bank%128, 0xf7]
                if dx72:
                    dat += [0xf0, 0x43, channel, 0x06, 0x08, 0x60]
                    dat += dx72data[1120*bank:1120*(bank+1)]
                    dat += [dxcommon.checksum(dx72data[1120*bank:1120*(bank+1)]), 0xf7]
                dat += [0xf0, 0x43, channel, 0x09, 0x20, 0x00]
                dat += dx7data[4096*bank:4096*(bank+1)]
                dat += [dxcommon.checksum(dx7data[4096*bank:4096*(bank+1)]), 0xf7]
                if TX7:
                    dat += [0xf0, 0x43, channel, 0x02, 0x20, 0x00]
                    dat += tx7data[2048*bank:2048*(bank+1)]*2
                    dat += [dxcommon.checksum(tx7data[2048*bank:2048*(bank+1)]*2), 0xf7]

        if nosplit==False:
            if mid:
                dat = syxmidi.syx2mid(dat)
            with open(outfile, 'wb') as f:
                array.array('B', dat).tofile(f)

    if nosplit==True:
        if mid:
            dat = syxmidi.syx2mid(dat)
        with open(outfile, 'wb') as f:
            array.array('B', dat).tofile(f)

    if dxcommon.ENABLE_MIDI:
        if outfile[-4:] == "MIDI":
            dxcommon.data2midi(dat, mid_out)

    return "Ready. {} Patch(es) written to output file(s)".format(len(dx7data)//128)

def dx2list(dx7data, dx72data, tx7data, dx72, TX7):
    dxlist = []
    for i in range(len(dx7data)//128):
        dx7dat = dx7data[128*i:128*(i+1)]
        dx72dat = dx72data[35*i:35*(i+1)]
        tx7dat = tx7data[64*i:64*(i+1)]

        a = dx7dat[118:128] + dx7dat[:118]
        a += dx72dat
        a += tx7dat

        dxlist.append(a)
    return dxlist

def list2dx(data):
    dx7data, dx72data, tx7data = [], [], []
    for i in data:
        dx7data += i[10:128] + i[:10]
        dx72data += i[128:128+35]
        tx7data += i[128+35:128+35+64]
    return dx7data, dx72data, tx7data

def dxsort(dx7data, dx72data, tx7data, dx72, TX7, casesens=False):
    if (len(dx7data)//128) > 1:
        print ("Sorting patches by name...")
        l = dx2list(dx7data, dx72data, tx7data, dx72, TX7)
        L = []
        for n in range(len(l)):
            for i in range(10):
                if l[n][0]<33:
                    l[n][:10] = l[n][1:10]+[32]
                else:
                    break
            if dxcommon.list2string(l[n][:10]) != "INIT VOICE":
                L.append(l[n])
        if casesens:
            L.sort()
        else:
            for i in range(len(L)):
                L[i] = dxcommon.list2string(L[i])
            L.sort(key=str.lower)
            for i in range(len(L)):
                L[i] = dxcommon.string2list(L[i])


        dx7data, dx72data, tx7data = list2dx(L)
    return dx7data, dx72data, tx7data

def dxnodupes(dx7data, dx72data, tx7data, dx72, TX7, nodupes2):
    if (len(dx7data)//128) > 1:
        print ("Searching and removing duplicates ...")
        L = dx2list(dx7data, dx72data, tx7data, dx72, TX7)
        l=[L[0]]
        if nodupes2 == True:
            for i in range(len(L)):
                dup = False
                for j in range(len(l)):
                    if l[j][10:] == L[i][10:]:
                        dup=True
                        break
                if dup == False:
                    l.append(L[i])
        else:
            for i in L:
                if not i in l:
                    l.append(i)
        dx7data, dx72data, tx7data = list2dx(l)
    return dx7data, dx72data, tx7data

def dxfind(dx7data, dx72data, tx7data, keywords, include=True):
    print ("Searching for: {}".format(keywords))
    dx7dat, dx72dat, tx7dat = [], [], []
    keywords = keywords.split(",")
    for keyword in keywords:
        for i in range(len(dx7data)//128):
            s = ''
            for k in range(128*i+118, 128*i+128):
                s += chr(dx7data[k])
            if keyword.lower() in s.lower():
                if include:
                    dx7dat += dx7data[128*i:128*i+128]
                    dx72dat += dx72data[35*i:35*i+35]
                    tx7dat += tx7data[64*i:64*i+64]
            else:
                if not include:
                    dx7dat += dx7data[128*i:128*i+128]
                    dx72dat += dx72data[35*i:35*i+35]
                    tx7dat += tx7data[64*i:64*i+64]
    return dx7dat, dx72dat, tx7dat

def dxswap(a, b, dx7data, dx72data, tx7data):
    print ("Swapping patches ...")
    adata = dx7data[128*(a-1):128*a], dx72data[35*(a-1):35*a], tx7data[64*(a-1):64*a]
    bdata = dx7data[128*(b-1):128*b], dx72data[35*(b-1):35*b], tx7data[64*(b-1):64*b]
    dx7data[128*(a-1):128*a], dx72data[35*(a-1):35*a], tx7data[64*(a-1):64*a] = bdata
    dx7data[128*(b-1):128*b], dx72data[35*(b-1):35*b], tx7data[64*(b-1):64*b] = adata
    return dx7data, dx72data, tx7data

def dxcopy(a, b, dx7data, dx72data, tx7data):
    print ("Copying patch(es) ...")
    for i in a:
        adata = dx7data[128*(i-1):128*i], dx72data[35*(i-1):35*i], tx7data[64*(i-1):64*i]
        dx7data[128*(b-1):128*b], dx72data[35*(b-1):35*b], tx7data[64*(b-1):64*b] = adata
        b += 1
    return dx7data, dx72data, tx7data

def dxbrightness(dx7data, brightness):
    for p in range(len(dx7data)//128):
        dx7dat = dx7data[128*p:128*(p+1)]
        alg = dx7dat[110]
        for op in range(6):
            if dx7.carrier(alg, op) == False:
                out = dx7dat[14 + (5-op)*17] + brightness
                out = min(99, max(0, out))
                dx7dat[14 + (5-op)*17] = out
        dx7data[128*p:128*(p+1)] = dx7dat
    return dx7data

def dxnosilence(dx7data, dx72data, tx7data):
    for p in range(len(dx7data)//128):
        dx7dat = dx7data[128*p:128*(p+1)]
        outlevel = 0
        eglevel = 0
        allow = 0
        alg = dx7dat[110]

        for op in range(6):
            if dx7.carrier(alg, op):
                outlevel += dx7dat[14 + (5-op)*17]
                eglevel += max(dx7dat[4 + (5-op)*17:8 + (5-op)*17])
                crs = (dx7dat[15 + (5-op)*17] >> 1) & 31
                fine = dx7dat[16 + (5-op)*17] & 127
                fix = dx7dat[15 + (5-op)*17] & 1
                if fix: #Fixed Freq
                    if 16000 > dx7.fix_dx7(crs, fine) > 16:
                         allow += 1
                else:
                    allow += 1
        if outlevel * eglevel * allow < 4:
            dx7data[128*p:128*(p+1)] = dx7.initvmem()
            dx72data[35*p:35*(p+1)] = dx7.initamem()
            tx7data[64*p:64*(p+1)] = tx7.initpmem()
    return dx7data, dx72data, tx7data

def dxexclude(dx7data, dx72data, tx7data, exclude):
    return dxfind(dx7data, dx72data, tx7data, exclude, False)

def dxview(dx7data):
    for i in range(len(dx7data)//128):
        print(dx7.voicename(dx7data[128*i:128*(i+1)]))

