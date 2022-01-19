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

from . import syxmidi
from . import fourop
from . import fb01
from . import pssx80
from . import vopm
from . import dxcommon
from . import wav2syx
from . import dx9
from . import dx7
from . import korg
from . import reface
from . import bohmorla
from . import korgz3

try: 
    range = xrange
except NameError:
    pass

PROGRAMNAME = "TXconvert"
PROGRAMVERSION = dxcommon.PROGRAMVERSION
PROGRAMDATE = dxcommon.PROGRAMDATE
ACED = fourop.ACED
ACED2 = fourop.ACED2
ACED3 = fourop.ACED3
EFEDS = fourop.EFEDS
DELAY = fourop.DELAY
MID_IN = dxcommon.MID_IN
MID_OUT = dxcommon.MID_OUT

BN4NR=[]
for b in range(4):
    for i in range(25):
        BN4NR.append(str(25*b+i))
    for i in range(7):
        BN4NR.append('--')
for i in range(10):
    BN4NR[i]='0'+BN4NR[i]

########## FILE INPORT/EXPORT #########

def read(infile, offset='0', check=False, yamaha='tx81z', mid_in=MID_IN, mid_out=MID_OUT):
    if offset.startswith('-'):
        datasize = os.path.getsize(infile) + int(offset, 0)
        if yamaha == "refacedx":
            offset = datasize % 150
        elif yamaha == "fb01":
            offset = datasize % 64
        else:
            offset = datasize % 128
    else:
        offset = int(offset, 0)

    txdata = []
    channel = 0
    if zipfile.is_zipfile(infile):
        with zipfile.ZipFile(infile, 'r') as zf:
            zflist = zf.namelist()
            print (zflist)
            for n in zflist:
                try:
                    txdat = []
                    d = zf.read(n)
                    tmp = mkstemp()[1]
                    with open(tmp, 'wb') as f:
                        f.write(d)
                    txdat, channel = read2(mid_in, mid_out, tmp, offset, check)
                    os.remove(tmp)
                    txdata += txdat
                    print ("\t{}".format(n))
                except:
                    print ("! only {} from {} files in zip were read".format(zflist.index(n)+1, len(zflist)))
                    break
    else:
        txdata, channel = read2(mid_in, mid_out, infile, offset, check, yamaha)
    return txdata, channel


def read2(mid_in, mid_out, infile, offset, check=False, yamaha='tx81z'):
    if not os.path.exists(infile):
        print ("{}: File not found.".format(infile))
        sys.exit(1)
    ext = os.path.splitext(infile)[1].lower()
    size = os.path.getsize(infile)-offset
    data = array.array("B")
    with open(infile, 'rb') as f:
        data.fromfile(f, offset+size)
    data = data.tolist()[offset:]
    
    REFACE, FB01, TX = False, False, True
    if yamaha in ('fb01', 'vopm'):
        REFACE, FB01, TX = False, True, False
    elif yamaha == 'refacedx':
        REFACE, FB01, TX = True, False, False

    #Dumprequest
    if dxcommon.ENABLE_MIDI:
        if ext == ".req":  # and data[0] == 0xf0:
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
    txdata = []
    fbdata = []
    rdxdata = []
    channel = 0
    rdxcount = 0

    # Yamaha DX21/TX81Z VMEM
    for i in range(size-4098):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x04 and data[i+4]==0x20 and data[i+5]==0x00: # and data[i+6+4097]==0xf7:
            if (check==False) or (dxcommon.checksum(data[i+6:i+6+4096])==data[i+6+4096]):
                for p in range(32):
                    txdata += data[128*p+i+6:128*(p+1)+i+6]
            channel = data[i+2]

    # Yamaha 4op editbuffer formats
    vcd = []
    for i in range(size-95):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x03 and data[i+4]==0x00 and data[i+5]==0x5d:
            #VCED
            vcd += data[i+6:i+6+93]
            channel = data[i+2]

    acd = []
    for i in range(size-25):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+6:i+16]==ACED:
            #ACED
            acd += data[i+16:i+16+23]

    acd2 = []
    for i in range(size-12):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+6:i+16]==ACED2:
            #ACED2
            acd2 += data[i+16:i+16+10]

    acd3 = []
    for i in range(size-22):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+6:i+16]==ACED3:
            #ACED3
            acd3 += data[i+16:i+16+20]
    
    efeds = []
    for i in range(size-5):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+6:i+16]==EFEDS:
            #EFEDS
            efeds += data[i+16:i+16+3]

    delay = []
    for i in range(size-4):    
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x7e and data[i+4]==0x00 and data[i+6:i+16]==DELAY:
            #DELAY
            delay += data[i+16:i+16+2]

    count = len(vcd)//93
    if len(delay) != 2*count:
        delay = fourop.initdelay()*count
    if len(efeds) != 3*count:
        efeds = fourop.initefeds()*count
    if len(acd3) != 20*count:
        acd3 = fourop.initacd3()*count
    if len(acd2) != 10*count:
        acd2 = fourop.initacd2()*count
    if len(acd) != 23*count:
        acd = fourop.initacd()*count
   
    for v in range(count):
        vmm = fourop.vcd2vmm(
            vcd[93*v:93*(v+1)], 
            acd[23*v:23*(v+1)], 
            acd2[10*v:10*(v+1)], 
            acd3[20*v:20*(v+1)], 
            efeds[3*v:3*(v+1)], 
            delay[2*v:2*(v+1)]
            )
        txdata += vmm

    # Yamaha FB01 RAM and ROM voicebanks
    for i in range(size-6360):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x75 and data[i+3]<=0x0f and data[i+6362]==0xf7:
            for p in range(48):
                fb=[]
                if (check==False) or (dxcommon.checksum(data[i+76+131*p:i+76+131*p+128])==data[i+76+131*p+128]):

                    for n in range(64):
                        fb.append(data[i+76+131*p+2*n] + (data[i+76+131*p+2*n+1]<<4))
                    fbdata += fb 

    # Yamaha FB01 voice bank 0
    for i in range(size-6357):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x0c and data[i+6359]==0xf7:
            for p in range(48):
                fb=[]
                if (check==False) or (dxcommon.checksum(data[i+73+131*p:i+73+131*p+128])==data[i+73+131*p+128]):
                    for n in range(64):
                        fb.append(data[i+73+131*p+2*n] + (data[i+73+131*p+2*n+1]<<4))
                    fbdata += fb

    # Yamaha FB01 instrument 1~8
    for i in range(size-136):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x75 and data[i+3]<=0x0f and (data[i+4]&8) and data[i+138]==0xf7:
            fb=[]
            if (check==False) or (dxcommon.checksum(data[i+9:i+9+128])==data[i+9+128]):
                for n in range(64):
                    fb.append(data[i+9+2*n] + (data[i+9+2*n+1]<<4))
                fbdata += fb

    # PSS 480/580/680
    for i in range(size-68):
        if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]==0x76 and data[i+3]==0x00 and data[i+71]==0xf7:
            if (check==False) or (dxcommon.checksum(data[i+4:i+4+66])==data[i+4+66]):
                print ("!! PSS-480/580/680 2-OP to 4-OP conversion")
                pss=[]    
                for n in range(33):
                    pss.append(((data[i+4+2*n]&15)<<4) + (data[i+4+2*n+1]&15))
                if yamaha == "pss":
                    print (pssx80.pss2txt(pss, infile))
                if REFACE:
                    rdxdata += pssx80.pss2rdx(pss, infile)
                else:
                    txdata += pssx80.pss2vmm(pss, infile)

    # Yamaha DX9 sysex
    # Single voice
    if size>160:
        for i in range(size-157):
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0 and data[i+4]==1 and data[i+5]==0x1b and data[i+6+156]==0xf7:
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+155])==data[i+6+155]):
                    dx9data = dx7.vced2vmem(data[i+6:i+6+155])
                else:
                    dx9data = dx7.initvmem()
                if REFACE:
                    rdxdata += reface.dx9tordx(dx9data)
                else:
                    txdata += dx9.dx9to4op(dx9data)
                channel=data[i+2]

    # Yamaha DX9 sysex
    # 32-voice (20-voice) bank
    if size>4101:
        for i in range(size-4098):
            #data[i+4] should be 0x20 but often is 0x10 
            if data[i]==0xf0 and data[i+1]==0x43 and data[i+2]<=0x0f and data[i+3]==0x09 and (data[i+4]==0x10 or data[i+4]==0x20) and data[i+5]==0x00 and data[i+6+4097]==0xf7:
                if (check==False) or (dxcommon.checksum(data[i+6:i+6+4096]) == data[i+6+4096]):
                    dx9data = data[i+6:i+6+4096]
                else:
                    dx9data = dx7.initvmem()*32
                for n in range(len(dx9data)//128):
                    if REFACE:
                        rdxdata += reface.dx9tordx(dx9data[128*n:128*(n+1)])
                    else:
                        txdata += dx9.dx9to4op(dx9data[128*n:128*(n+1)])
                channel = data[i+2]

    # Yamaha Reface DX sysex
    if size>238:
        rdxdat = []
        for i in range(size-40): 
            rdxhead = data[i:i+11]
            if rdxhead[0] == 0xf0:
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
                if REFACE:
                    rdxdata += rdxdat
                else:
                    txdata += reface.rdx2vmm(rdxdat, yamaha)
                rdxdat = []

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
            if REFACE:
                rdxdata += bohmorla.bhm2rdx(bhm, pn)
            elif FB01:
                fbdata += bohmorla.bhm2fb(bhm, pn)
            else:
                txdata += bohmorla.bhm2vmm(bhm, pn)
            if yamaha in ('orla', 'bohm'):
                print(bohmorla.bhm2txt(bhm, pn))

    # BOHM 4x9
    for i in range(size-94):
        if data[i:i+7] == [0xf0, 0x00, 0x42, 0x6f, 0x68, 0x6d, 0x12]:
            print ("!! Bohm 4x9 import (experimental)")
            bhm = data[i+9:i+9+88]
            if REFACE:
                rdxdata += bohmorla.fourxnine2rdx(bhm)
            elif FB01:
                fbdata += bohmorla.fourxnine2fb(bhm)
            else:
                txdata += bohmorla.fourxnine2vmm(bhm)

    # KORG 707 KORG DS8 7985-550=7435
    for i in range(size-7435): #100 programs bank
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and (data[i+3] in (0x1a, 0x13)) and data[i+4]==0x4c and data[i+11] != 0xf7:
            if data[i+3] == 0x13:
                print ("!! DS8 bank import")
                ds8 = True
            else:
                print ("!! 707 bank import")
                ds8 = False
            korgmid = data[i+5:i+5+7984]
            korgdat = korg.korg7to8(korgmid)
            for p in range(100):
                if REFACE:
                    rdxdata += reface.korg2rdx(korgdat[66*p:66*(p+1)], ds8)
                else:
                    txdata += korg.bnk2vmm(korgdat[66*p:66*(p+1)], ds8)

    for i in range(size-97): #1 program
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and (data[i+3] in (0x1a, 0x13)) and data[i+4]==0x40:
            if data[i+3] == 0x13:
                ds8 = True
                print ("!! DS8 prog. import")
            else:
                ds8 = False
                print ("!! 707 prog. import")
            korgmid = data[i+5:i+5+96]
            korgdat = korg.korg7to8(korgmid)
            if REFACE:
                korgbnk = korg.vce2bnk(korgdat, ds8)
                rdxdata += reface.korg2rdx(korgbnk, ds8)
            else:
                txdata += korg.vce2vmm(korgdat, ds8)

    # KORG Z3 all sound
    for i in range(size-12800):
        if data[i]==0xf0 and data[i+1]==0x42 and (data[i+2] & 0xf0)==0x30 and data[i+3]==0x1d and data[i+4]==0x4c:
            print ("!! Korg Z3 import (experimental)")
            for p in range(128):
                if REFACE:
                    vmm = korgz3.z3_to_vmm(data[5+100*p:105+100*p])
                    rdxdata += reface.vmm2rdx(vmm)
                else:
                    #print(korgz3.z3text(data[5+100*p:105+100*p], p))
                    txdata += korgz3.z3_to_vmm(data[5+100*p:105+100*p])

    # WAV data with datacassette dump
    if ext == '.wav':
       txdata += wav2syx.wav2syx(infile, 'tx')
     
    # MidiQuest TX81Z SQL
    if ext == ".sql" and dxcommon.list2string(data[:4]) == "LIST" and dxcommon.list2string(data[0x20:0x20+12]) == "Yamaha TX81Z":
        for i in range(size-128):
            if dxcommon.list2string(data[i:i+6]) == "ccc222":
                txdata += data[i-67:i-67+128]

    # Bowker/Henderson/Michelson TX81Z/DX11 Librarian (.PAT)
    if ext == ".pat" and data[:11] == [0x00, 0x4C, 0x4D, 0x20, 0x20, 0x38, 0x39, 0x37, 0x36, 0x41, 0x45]:
        #ACED 1+10+23 + VCED 1+93+1 = 129 
        for i in range(len(data)/129):
            txdata += fourop.vcd2vmm(data[129*i+35:129*i+35+93], data[129*i+1:129*i+1+23])

    # Still not found anything? Then keep searching ...
    if txdata != []:
        pass

    #Musicode V50 Voice Development System (.VBL)
    if ext == ".vlb" and dxcommon.list2string(data[:16]) == "YSVLYSVLYSVLYSVL":
        txdata += data[4848:4848+12800]

    #Voyetra SIDEMAN and PATCHMASTER
    elif data[0:4] == [0xdf, 0x05, 0x01, 0x00]:
        if ext == ".b15" and size == 10755:
            if dxcommon.list2string(data[6:18]) == "YAMAHA TX81Z":
                for i in range(32):
                    txdata += data[0x060f+128*i:0x60f+128*(i+1)]
        if ext == ".b16" and size == 20837:
            if dxcommon.list2string(data[6:18]) == "YAMAHA FB-01":
                for bank in range(2):
                    for i in range(48):
                        fb = []
                        for p in range(64):
                            lo = data[0x2029*bank + 0x0821 + 130*i + 2*p]&15
                            hi = (data[0x2029*bank + 0x0821 + 130*i + 2*p + 1] & 15) << 4
                            fb.append(lo + hi)
                        fbdata += fb

    # X-OR V50
    elif size == 24576 and ext == ".v5b":
        for i in range(100):
            txdata += data[128*i:128*(i + 1)]

    # X-OR TX81Z
    elif size == 6538 and ext == ".txz":
        for i in range(32):
            txdata += data[128*i:128*(i + 1)]

    # V50 internal disk formats
    elif (size in (17729, 26624) or size>50000) and ext[:-2] in (".i", ".v") and ext[2:].isdigit():
        for i in range(100):
            try:
                vmm = data[0x3600 + 128*i:0x3600 + 128*(i+1)]
                if vmm[86]<50:
                    vmm[86] += 51
                else:
                    vmm[86] -= 50
                txdata += vmm
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
                txdata += vmm
    elif size == 32768 and data[4:10] == [0x56, 0x35, 0x30, 0x53, 0x59, 0x4e]: #"V50SYN"
        for b in range(4):
            for p in range(25):
                vmm = data[0x3900 + 0xc80*b + 128*p : 0x3900 + 0xc80*b + 128*(p+1)]
                if vmm[86]<50:
                    vmm[86] += 51
                else:
                    vmm[86] -= 50
                txdata += vmm

    # m.gregory's TX81Z Programmer .tx8
    elif ext == '.tx8' and data[:5] == [0x54, 0x58, 0x38, 0x31, 0x5a]:        
        for i in range((size-9)//173):
            txdata += data[54 + 173*i:54 + 173*i + 128]

    # Emagic Sounddiver TX81Z
    elif ext == ".lib" and data[:4] == [0x4d, 0x52, 0x4f, 0x46]:
        for i in range(size-158):
            if data[i:i+4] == [0x54, 0x4e, 0x45, 0x4c]:
                nmlen=data[i+21]
                if data[i+nmlen+22:i+nmlen+29] == [0x03, 0x7c, 0x54, 0x58, 0x38, 0x31, 0x5a]:
                    vmm = fourop.initvmm()
                    vmm[:50] = data[i+nmlen+30:i+nmlen+30+50]
                    vmm[57:67] = data[i+22:i+22+nmlen] + [32]*(10-nmlen)
                    vmm[67:100] = data[i+nmlen+30+57:i+nmlen+30+90]
                    txdata += vmm

    # Opcode Galaxy TX81Z
    elif size == 4876 and dxcommon.list2string(data[0x1d:0x29]) == "Yamaha TX81Z":
        for i in range(32):
            vmm = fourop.initvmm()
            vmm[:84] = data[0x7b3 + 84*i: 0x7b3 + 84*(i+1)]
            txdata += vmm
    elif dxcommon.list2string(data[0x1c:0x27]) == "TX81Z Voice":
        for i in range((size-66)//84):
            vmm = fourop.initvmm()
            vmm[:84] = data[0x42 + 84*i: 0x42 + 84*(i+1)]
            txdata += vmm
    elif data[0x48:0x48+6] == data[0x9c:0x9c+6] == data[0xf0:0xf0+6] == [0x63, 0x63, 0x63, 0x32, 0x32, 0x32]:
        for i in range((size-5)//84):
            vmm = fourop.initvmm()
            vmm[:84] = data[5 + 84*i: 5 + 84*(i+1)]
            txdata += vmm

    # Synthworks 4OP
    elif ext == '.bnk' and size == 4032 and data[0] == 0x0a:
        for i in range(32):
            txdata += fourop.steinb2vmm(data[1 + 12*i:11 + 12*i], data[0x180 + 114*i:0x180 + 114*(i+1)])
    elif ext == '.snd' and size == 126 and data[0] == 0x0a:
        txdata += fourop.steinb2vmm(data[1:11], data[12:])
 
    # Atari PSSED pss480-780 library with 100 patches
    elif ext == ".lib" and size == 4908:
        print ("!! PSS-480/580/680 2-OP to 4-OP conversion")
        for i in range(100):
            voicename = dxcommon.list2string(data[8+16*i:8+16*(i+1)])
            if REFACE:
                rdxdata += reface.pss2vmm(data[1608+33*i:1608+33*(i+1)], infile, voicename)
            else:
                txdata += pssx80.pss2vmm(data[1608+33*i:1608+33*(i+1)], infile, voicename)

    # Caged Artist FB01
    elif size == 8768 and ext == ".fb1" and data[:32] == [0]*32:
        for bnk in range(2):
            for i in range(48):
                fbname = dxcommon.list2string(data[32 + 64*i:32 + 64*i + 7])
                fbdata += data[32 + 3104*bnk + 64*i:32 + 3104*bnk + 64*(i+1)]

    # Dr.T FB01 / raw data
    elif (size % 64 == 0) and ext == ".fb1":
        for i in range(48):
            fbdata += data[64*i:64*(i+1)]

    # Synthworks FB01
    elif size == 2450 and ext == ".fbd":
        for i in range(49):
            fb = 64*[0]
            fb[:7] = data[1+8*i:8+8*i]
            fb[8:48] = data[0x188 + 42*i:0x1b0 + 42*i]
            fb[58:60] = data[0x1b0 + 42*i:0x1b2 + 42*i]
            fbdata += fb

    # Frederic Meslin FB01 editor
    elif size == 354 and ext == ".fbv":
        #TODO
        #fbdata += data[0x107:0x107+64]
        pass

    # CX5M VOG
    elif size in (3111, 3079) and ext == ".vog":
        fbdata += data[0x27:0x27 + 48*64]

    # CX5M YRM305
    elif ext == '.d21' and size == 2375:
        for i in range(32):
            vmm = fourop.initvmm()
            vmm[:73] =  data[39+73*i:39+73*(i+1)]
            txdata += vmm

    # VOPM .OPM
    elif ext == ".opm":
        print ("!! VOPM (.opm) to 4-OP DX/TX conversion")
        data = vopm.file2data(infile)
        for i in range(len(data)//76):
            fb = vopm.vopm2fb01(data[76*i:76*(i+1)])
            if FB01:
                fbdata += fb
            else:
                tx = fb01.fb2vmm(fb, yamaha)
                tx[57:67] = data[76*i:76*i+10]
                txdata += tx

    # TFM Music Maker instrument files
    elif ext == ".tfi" and size == 42:
        print("!! TFM Music Maker instrument (.tfi) conversion")
        if FB01:
            fbdata += fb01.tfm2fb(data, infile)
        else:
            fbdat = fb01.tfm2fb(data, infile)
            txdat = fb01.fb2vmm(fbdat)
            vname = os.path.basename(infile)[:-4] + "          "
            vname = vname[:10]
            txdat[57:67] = dxcommon.string2list(vname)
            txdata += txdat
    # Bryan Sutula TX81Z/DX11 Voice Archive
    elif data[:26] == dxcommon.string2list("* TX81Z/DX11 Voice Archive"):
        hx = "0123456789abcdef"
        with open(infile, 'r') as f:
            datatxt = f.readlines()
        for i in range(len(datatxt)):
            if datatxt[i].startswith("** Source:"):
                hextext = ''
                for l in range(1,7):
                    hextext = datatxt[i+l].strip()
                    for n in range(1 + len(hextext)//3):
                        txdata.append (16*(hx.index(hextext[3*n])) + hx.index(hextext[3*n+1]))

    # extracted using Martin Ward's tape-read perl script with baud=1200
    elif ext == ".txt" and size>75:
        txdata += wav2syx.cas2vmm(data, 0)

    # datacassette data extracted using wav2cas
    elif data[:8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
        if data[0x12:0x18] == dxcommon.string2list("VOICE "):
            if data[0x20:0x28] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                fbdata += data[0x4e:0x4e+3072]
            elif data[0x28:0x30] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                fbdata += data[0x56:0x56+3072]

        else:
            for i in range(len(data)-84):
                if data[i:i+8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                    txdata += wav2syx.cas2vmm(data, i+8)

    # P-Farm
    elif ext==".pfm" and data[:4] == [0x50, 0x46, 0x72, 0x6d]: # "PFrm"
        pass
        '''
        # TODO
        for i in range(32):
            vcd = fourop.initvcd()
            for n in range(4):
                for p in range(13):
                    vcd[13*n + p] = data[0x55 + 64*n + 4*p]
            for p in range(77):
                vcd[p] = data[0x52 + 4*p + 400*i]
            vcd[77:87] = data[400*i + 0x3d:400*(i+1) + 0x3d]
            for p in range(87, 93):
                vcd[p] = data[0x52 + 4*(p-10) + 400*i]
            txdata += fourop.vcd2vmm(vcd)
        '''

    # Dr.T FourOp de Luxe or raw headerless sysex
    elif size % 128 == 0 and (data[0] < 128):
        for i in range(size//128):
            if fourop.raw_check(data[128*i:128*i + 128]):
                if sum(data[128*i + 118:128*i + 128]) == 0 and sum(data[128*i:128*i + 118]) != 0:
                    txdata += data[128*i:128 + 128*i]

    # Audiogrill TX81Z/DX11 Voice Archive 
    elif dxcommon.list2string(data[:26]) == "* TX81Z/DX11 Voice Archive":
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
            txdata.append (16*numbers[2*i] + numbers[2*i+1]) 

    # Tim Thompson's Glib tx81z dx100 editor
    elif data[0] == 0xdd and (ext in ('.dx1', '.tx8')) and size==4097:
        txdata += data[1:4097]

    # Ignore many other SysEx
    elif ext in ('.dx7', '.tx7', '.dx2', '.dxc', '.b13', '.b68', '.slb', '.xal', '.dxl'):
        txdata += fourop.initvmm()

    # FB to TX / TX to FB
    if TX:
        if fbdata != []:
            print ("! FB01 to 4-OP DX/TX conversion")
            for i in range(len(fbdata)//64):
                txdata += fb01.fb2vmm(fbdata[64*i:64*(i+1)])
    elif FB01:
        if txdata != []:
            print ("! 4-OP DX/TX to FB01 conversion")
            for i in range(len(txdata)//128):
                fbdata += fb01.vmm2fb(txdata[128*i:128*(i+1)])
    elif REFACE:
        if fbdata != []:
            print ("! FB01 to Reface conversion")
            for i in range(len(fbdata)//64):
                rdxdata += reface.fb2rdx(fbdata[64*i:64*(i+1)])
        if txdata != []:
            print ("! 4OP DX/TX to Reface conversion")
            for i in range(len(txdata)//128):
                rdxdata += reface.vmm2rdx(txdata[128*i:128*(i+1)])
    
    if TX:
        if txdata == []:
            for i in data[:128]:
                if i > 127:
                    txdata += fourop.initvmm()
                    break

    # If everything fails: The worst thing that can happen is
    # creating a TX/DX compatible but completely useless patchbank :-)
    # Should work with e.g. headerless 4096 bytes DXX files
    if fbdata == [] and txdata == [] and rdxdata == []:
        if FB01:
            fbdata += data[:64*(len(data)//64)]
        elif REFACE:
            rdxdata += data[:150*(len(data)//150)]
        else:
            txdata += data[:128*(len(data)//128)]

    # Safety garbage cleanup
    txdat = []
    initcount = 0
    if FB01:
        for i in range(len(fbdata)//64):
            if dxcommon.list2string(fbdata[64*i:64*i+5]).lower() != "initv":
                if dxcommon.list2string(fbdata[64*i:64*i+7]) != "SineWav":
                    if dxcommon.list2string(fbdata[64*i:64*i+7]).strip() != "":
                        txdat += fb01.fbclean(fbdata[64*i:64*(i+1)])

    elif TX:
        for i in range(len(txdata)//128):
            if dxcommon.list2string(txdata[128*i+57:128*i+67]) != "INIT VOICE":
                if dxcommon.list2string(txdata[128*i+57:128*i+67]).strip() != "":
                    txdat += fourop.cleanvmm(txdata[128*i:128*(i+1)])

    elif REFACE:
        for i in range(len(rdxdata)//150):
            if dxcommon.list2string(rdxdata[150*i:150*i+10]).lower() != "Init Voice":
                if dxcommon.list2string(rdxdata[150*i:150*i+10]).strip() != "":
                    txdat += reface.cleanrdx(rdxdata[150*i:150*(i+1)])
    return txdat, channel

###### TX WRITE STUFF #####

def write_rdx(outfile, rdxdata, channel, nosplit, split=32, yamaha='refacedx', mid_out='MID_OUT'):
    if outfile == os.devnull:
        nosplit = True
    ext = os.path.splitext(outfile)[1].lower()
    basename = os.path.split(outfile)[1]
    basename = os.path.splitext(basename)[0]
    dirname = os.path.dirname(outfile)
    mid = False
    if ext.lower() in (".mid", ".midi"):
        mid = True
    if dxcommon.ENABLE_MIDI:
        if outfile[-4:] == "MIDI":
            nosplit = True 
 
    if len(rdxdata)>150:
        patchcount = len(rdxdata)//150
    elif len(rdxdata)<150:
        rdxdata = reface.initrdx()
        patchcount = 1
    else:
        patchcount = 1

    if split == 1:
        patchcount = 1

    dat=[]
    message = ''

    if ext.lower() == ".txt":
        dat = reface.rdx2txt(rdxdata)

    else:
        for pp in range(patchcount): #save as VCED sysex
            if patchcount == 1:
                dat += reface.rdx2syx(rdxdata[150*pp:150*(pp+1)], channel, 0)
            else:
                dat += reface.rdx2syx(rdxdata[150*pp:150*(pp+1)], channel, pp+1)

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

    return "Ready. {} Patch(es) written to output file(s)".format(patchcount)

def write_fb(outfile, fbdata, channel, nosplit, split=48, yamaha='fb01', mid_out='MID_OUT'):
    if outfile == os.devnull:
        nosplit = True
    FB01 = True
    ext = os.path.splitext(outfile)[1].lower()
    if ext == ".opm":
        split = 128
        yamaha = "vopm"
    basename = os.path.split(outfile)[1]
    basename = os.path.splitext(basename)[0]
    dirname = os.path.dirname(outfile)
    mid = False
    if ext.lower() in (".mid", ".midi"):
        mid = True
    if dxcommon.ENABLE_MIDI:
        if outfile[-4:] == "MIDI":
            nosplit = True 
 
    if len(fbdata)>64:
        patchcount = len(fbdata)//64
    elif len(fbdata)<64:
        fbdata = fb01.initfb()
        patchcount = 1
    else:
        patchcount = 1
    
    if len(fbdata)>64:
        #Fill unused patch locations in banks with INIT VOICE
        while len(fbdata)%3072 != 0:
            fbdata += fb01.initfb()

        patchcount = len(fbdata)//64
    
    if split == 1:
        patchcount = 1

    dat=[]
    message = ''

    bankcount = max(1, len(fbdata)//(64*split))
    bankdigits = len(str(bankcount+1))
    for bank in range(bankcount):
        if len(fbdata)//(64*split)>1 and nosplit==False:
            outfile=os.path.join(dirname, basename+"("+str(bank+1).zfill(bankdigits)+")"+ext)
        if nosplit==False:
            dat=[]

        if ext.lower() == ".fb1":
            if patchcount == 1:
                dat = fbdata
            else:
                dat += fbdata[3072*bank:3072*(bank+1)]
        
        elif ext.lower() == ".txt":
            dat = fb01.fb2txt(fbdata)

        elif ext.lower() == ".opm":
            dat += vopm.fb2vopm(fbdata[8192*bank:8192*(bank+1)])
            patchcount = min(patchcount, 128)
        
        else:
            if patchcount == 1: #save as VCED sysex
                dat += fb01.fb2syx(fbdata[:64], bank%2, channel)
                
            else: #save as VMEM sysex
                dat += fb01.fb2syx(fbdata[3072*bank:3072*(bank+1)], bank%2, channel)

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

    return "Ready. {} Patch(es) written to output file(s)".format(patchcount)


def write(outfile, txdata, channel=0, nosplit=False, split=32, yamaha='tx81z', mid_out='MID_OUT'):
    if outfile == os.devnull:
        nosplit = True
    ext = os.path.splitext(outfile)[1]
    if ext.lower() == '.opm':
        yamaha = 'vopm'
        split = 128
    if ext.lower() == '.fb1':
        yamaha = 'fb01'
        if split !=1: split = 48
    if yamaha in ('fb01', 'vopm'):
        return write_fb(outfile, txdata, channel, nosplit, split, yamaha, mid_out)
    if yamaha == 'refacedx':
        return write_rdx(outfile, txdata, channel, nosplit, split, yamaha, mid_out)

    basename = os.path.split(outfile)[1]
    basename = os.path.splitext(basename)[0]
    dirname = os.path.dirname(outfile)

    mid = False
    if ext.lower() in (".mid", ".midi"):
        mid = True
    if dxcommon.ENABLE_MIDI:
        if outfile[-4:] == "MIDI":
            nosplit = True 
 
    if len(txdata)>128:
        patchcount = len(txdata)//128
    elif len(txdata)<128:
        txdata = fourop.initvmm()
        patchcount = 1
    else:
        patchcount = 1

    if split == 0:
        nosplit = True

    elif patchcount>1:
        if patchcount <= 32:
            split = 32
        txdat = []
        txrange = len(txdata)/float(split*128)
        if txrange > int(txrange):
            txrange += 1
        txrange = int(txrange)
        for i in range(txrange):
            txdat += txdata[128*i*split:128*(i+1)*split] + fourop.initvmm()*(32-split)
        txdata = txdat
    
    if yamaha in ('ys200', 'ys100', 'tq5', 'b200'):
        #if len(txdata) == 128*128:
        #    txdata[128*25:128*32] = txdata[128*32:128*39]
        #    txdata[128*57:128*64] = txdata[128*64:128*71]
        #    txdata[128*89:128*96] = txdata[128*96:128*103]
        for i in range(len(txdata)//128):
            txdata[128*i:128*(i+1)] = fourop.v50_ys(txdata[128*i:128*(i+1)])

    if yamaha in ('v50', 'refacedx'):
        for i in range(len(txdata)//128):
            txdata[128*i:128*(i+1)] = fourop.ys_v50(txdata[128*i:128*(i+1)])

    # Operator frequency recalculation on older models
    if yamaha in ('dx100', 'dx27', 'dx27s', 'dx21'):
        for i in range(len(txdata)//128):
            txdata[128*i:128*i+128] = fourop.tx81z_dx21(txdata[128*i:128*i+128])[0]
                
    if yamaha in ('v50', 'ys200', 'ys100', 'tq5', 'ds55', 'b200') and len(txdata)>4096:
        bn=4
    else:
        bn=1
    
    if len(txdata)>128:
        #Fill unused patch locations in banks with INIT VOICE
        while len(txdata)%(4096*bn) != 0:
            txdata += fourop.initvmm()
        patchcount = len(txdata)//128

    dat=[]
    message = ''

    bankcount = max(1, len(txdata)//(bn*4096))
    bankdigits = len(str(bankcount+1))
    for bank in range(bankcount):
        if len(txdata)//(bn*4096)>1 and nosplit==False:
            outfile=os.path.join(dirname, basename+"("+str(bank+1).zfill(bankdigits)+")"+ext)
        if nosplit==False:
            dat=[]

        if ext.lower() == ".dxx":
            if patchcount == 1:
                dat = txdata[:128]
            else:
                dat += txdata[4096*bn*bank:4096*bn*(bank+1)]

        elif ext.lower() == ".txt":
            if patchcount == 1 or len(txdata) == 128:
                dat = fourop.vmm2txt(txdata[:128], yamaha)
            else:
                t = ''
                for i in range(32*bn):
                    if bn == 4:
                        bnr = BN4NR[i%128]
                        t += "{}: {}\n".format(bnr, fourop.voicename(txdata[4096*bank*bn+128*i:4096*bank*bn+128*(i+1)]))
                    else:
                        bnr = 1+i+bank*32*bn
                        t += "{:03}: {}\n".format(bnr, fourop.voicename(txdata[4096*bank*bn+128*i:4096*bank*bn+128*(i+1)]))
                t += "\n"

                for i in t:
                    dat.append(ord(i))

        else:
            if patchcount == 1: #save as VCED sysex
                vcd, acd, acd2, acd3, efeds, delay = fourop.vmm2vcd(txdata) 
                
                #ACED3
                if yamaha in ('v50', 'all'):
                    dat += [0xf0, 0x43, channel, 0x7e, 0x00, 0x1e]
                    dat += ACED3
                    dat += acd3
                    dat += [dxcommon.checksum(acd3+ACED3), 0xf7]
                
                #EFEDS
                if yamaha in ('ys100', 'ys200', 'b200', 'tq5', 'all'):
                    dat += [0xf0, 0x43, channel, 0x7e, 0x00, 0x0d]
                    dat += EFEDS
                    dat += efeds
                    dat += [dxcommon.checksum(efeds+EFEDS), 0xf7]
                
                #DELAY
                if yamaha in ('ds55', 'all'):
                    dat += [0xf0, 0x43, channel, 0x7e, 0x00, 0x0c]
                    dat += DELAY
                    dat += delay
                    dat += [dxcommon.checksum(delay+DELAY), 0xf7]
                
                #ACED2
                if yamaha in ('dx11', 'v2', 'v50', 'ys100', 'ys200', 'tq5', 'b200', 'wt11', 'all'):
                    dat += [0xf0, 0x43, channel, 0x7e, 0x00, 0x14]
                    dat += ACED2
                    dat += acd2
                    dat += [dxcommon.checksum(acd2+ACED2), 0xf7]
                
                #ACED
                if yamaha in ('ds55', 'dx11', 'v2', 'v50', 'ys100', 'ys200', 'tq5', 'b200', 'tx81z', 'wt11', 'all'):
                    dat += [0xf0, 0x43, channel, 0x7e, 0x00, 0x21]
                    dat += ACED
                    dat += acd
                    dat += [dxcommon.checksum(acd+ACED), 0xf7]

                #VCED
                dat += [0xf0, 0x43, channel, 0x03, 0x00, 0x5d]
                dat += vcd
                dat += [dxcommon.checksum(vcd), 0xf7]
                
                
            else: #save as VMEM sysex
                if bn > 1:
                    for block in range(bn):
                        dat += [0xf0, 0x43 , 0x10+channel, 0x24, 0x07, 1+block, 0xf7]
                        dat += [0xf0, 0x43, channel, 0x04, 0x20, 0x00]
                        dat += txdata[4096*block+16384*bank:4096*(block+1)+16384*bank]
                        dat += [dxcommon.checksum(txdata[4096*block+16384*bank:4096*(block+1)+16384*bank]), 0xf7]
                if bn == 1:
                    dat += [0xf0, 0x43, channel, 0x04, 0x20, 0x00]
                    dat += txdata[4096*bank:4096*(bank+1)]
                    dat += [dxcommon.checksum(txdata[4096*bank:4096*(bank+1)]), 0xf7]

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
    return "Ready. {} Patch(es) written to output file(s)".format(len(txdata)//128)

def tx2list(txdata):
    txlist = []
    for i in range(len(txdata)//128):
        txdat = txdata[128*i:128*(i+1)]
        a = txdat[57:67]+txdat[:57]+txdat[67:]
        txlist.append(a)
    return txlist

def fb2list(fbdata):
    fblist = []
    for i in range(len(fbdata)//64):
        fblist.append(fbdata[64*i:64*(i+1)])
    return fblist

def list2tx(data):
    txdata = []
    for i in data:
        txdata += i[10:67]+i[:10]+i[67:]
    return txdata

def list2fb(data):
    fbdata = []
    for i in data:
        fbdata += i
    return fbdata

def rdx2list(rdxdata):
    rdxlist = []
    for i in range(len(rdxdata)//150):
        rdxlist.append(rdxdata[150*i:150*(i+1)])
    return rdxlist

def list2rdx(data):
    rdxdata = []
    for i in data:
        rdxdata += i
    return rdxdata

def rdxsort(rdxdata, casesens=False):
    if (len(rdxdata)//150) > 1:
        print ("Sorting patches by name ...")
        l = rdx2list(rdxdata)
        L = []
        for n in range(len(l)):
            if dxcommon.list2string(l[n][:10]) != "Init Voice":
                L.append(l[n])
        if casesens:
            L.sort()
        else:
            for i in range(len(L)):
                L[i] = dxcommon.list2string(L[i])
            L.sort(key=str.lower)
            for i in range(len(L)):
                L[i] = dxcommon.string2list(L[i])
        rdxdata = list2rdx(L)
    return rdxdata

def txsort(txdata, casesens=False):
    if (len(txdata)//128) > 1:
        print ("Sorting patches by name ...")
        l = tx2list(txdata)
        L = []
        for n in range(len(l)):
            for i in range(10):
                #remove leading space
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
        txdata = list2tx(L)
    return txdata

def fbsort(fbdata, casesens=True):
    if (len(fbdata)//64) > 1:
        print ("Sorting patches by name ...")
        l = fb2list(fbdata)
        L = []
        for n in range(len(l)):
            if dxcommon.list2string(l[n][:6]) != "InitVc":
                L.append(l[n])
        if casesens:
            L.sort()
        else:
            for i in range(len(L)):
                L[i] = dxcommon.list2string(L[i])
            L.sort(key=str.lower)
            for i in range(len(L)):
                L[i] = dxcommon.string2list(L[i])
        fbdata = list2fb(L)
    return fbdata

def rdxnodupes(rdxdata, nodupes2):
    if (len(rdxdata)//150) > 1:
        print ("Searching and removing duplicates ...")
        L = rdx2list(rdxdata)
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
        rdxdata = list2rdx(l)
    return rdxdata

def txnodupes(txdata, nodupes2):
    if (len(txdata)//128) > 1:
        print ("Searching and removing duplicates ...")
        L = tx2list(txdata)
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
        txdata = list2tx(l)
    return txdata

def fbnodupes(fbdata, nodupes2):
    if (len(fbdata)//64) > 1:
        print ("Searching and removing duplicates ...")
        L = fb2list(fbdata)
        l=[L[0]]
        if nodupes2 == True:
            for i in range(len(L)):
                dup = False
                for j in range(len(l)):
                    if l[j][7:] == L[i][7:]:
                        dup=True
                        break
                if dup == False:
                    l.append(L[i])
        else:
            for i in L:
                if not i in l:
                    l.append(i)
        fbdata = list2fb(l)
    return fbdata

def rdxfind(rdxdata, keywords, include=True):
    print ("Searching for {}".format(keywords))
    rdxdat = []
    keywords = keywords.split(",")
    for keyword in keywords:
        for i in range(len(rdxdata)//150):
            s = ''
            for k in range(150*i, 150*i+10):
                s += chr(rdxdata[k])
            if keyword.lower() in s.lower():
                if include:
                    rdxdat += rdxdata[150*i:150*(i+1)]
            else:
                if not include:
                    rdxdat += rdxdata[150*i:150*(i+1)]
    return rdxdat

def txfind(txdata, keywords, include=True):
    print ("Searching for {}".format(keywords))
    txdat = []
    keywords = keywords.split(",")
    for keyword in keywords:
        for i in range(len(txdata)//128):
            s = ''
            for k in range(128*i+57, 128*i+67):
                s += chr(txdata[k])
            if keyword.lower() in s.lower():
                if include:
                    txdat += txdata[128*i:128*i+128]
            else:
                if not include:
                    txdat += txdata[128*i:128*i+128]
    return txdat

def fbfind(fbdata, keywords, include=True):
    print ("Searching for {}".format(keywords))
    fbdat = []
    keywords = keywords.split(",")
    for keyword in keywords:
        for i in range(len(fbdata)//64):
            s = ''
            for k in range(64*i, 64*i+7):
                s += chr(fbdata[k])
            if keyword.lower() in s.lower():
                if include:
                    fbdat += fbdata[64*i:64*(i+1)]
            else:
                if not include:
                    fbdat += fbdata[64*i:64*(i+1)]
    return fbdat

def txswap(a, b, txdata, size=128):
    print ("Swapping patches ...")
    adata = txdata[size*(a-1):size*a]
    bdata = txdata[size*(b-1):size*b]
    txdata[size*(a-1):size*a] = bdata
    txdata[size*(b-1):size*b] = adata
    return txdata

def txcopy(a, b, txdata, size=128):
    print ("Copying patch(es) ...")
    for i in a:
        adata = txdata[size*(i-1):size*i]
        txdata[size*(b-1):size*b] = adata
        b += 1
    return txdata

def txbrightness(txdata, brightness):
    for p in range(len(txdata)//128):
        txdat = txdata[128*p:128*(p+1)]
        alg = txdat[52] & 7
        for op in range(4):
            if fourop.carrier(alg, op) == False:
                out = txdat[(37, 17, 27, 7)[op]] + brightness
                out = min(99, max(0, out))
                txdat[(37, 17, 27, 7)[op]] = out
        txdata[128*p:128*(p+1)] = txdat
    return txdata

def fbbrightness(fbdata, brightness):
    for p in range(len(fbdata)//64):
        fbdat = fbdata[64*p:64*(p+1)]
        alg = fbdat[12] & 7
        for op in range(4):
            if fourop.carrier(alg, op) == False:
                tl = fbdat[(40, 32, 24, 16)[op]] - brightness
                tl = min(127, max(0, tl))
                fbdat[(40, 32, 24, 16)[op]] = tl
        fbdata[64*p:64*(p+1)] = fbdat
    return fbdata

def rdxbrightness(rdxdata, brightness):
    for p in range(len(rdxdata)//150):
        rdxdat = rdxdata[150*p:150*(p+1)]
        alg = min(rdxdat[16], 11)
        for op in range(4):
            if reface.carrier(alg, op) == False:
                out = rdxdat[18 + 38 + 28*op] + brightness
                out = min(127, max(0, out))
                rdxdat[18 + 38 + 28*op] = out
        rdxdata[150*p:150*(p+1)] = rdxdat
    return rdxdata

def txnosilence(txdata):
    for p in range(len(txdata)//128):
        txdat = txdata[128*p:128*(p+1)]
        acd = fourop.vmm2vcd(txdat)[1]
        alg = txdat[52] & 7
        outlevel = 0
        eglevel = 0
        allow = 0
        for op in range(4):
            if fourop.carrier(alg, op):
                outlevel += txdat[(37, 17, 27, 7)[op]]
                eglevel += txdat[(34, 14, 24, 4)[op]]
                if acd[(15,5,10,0)[op]]: #Fixed Freq
                    if 16000 > float(fourop.vmm2freq(txdat, op)[:-1]) > 16:
                        allow += 1
                else:
                    allow += 1
        if outlevel * allow * eglevel < 4:
            txdata[128*p:128*(p+1)] = fourop.initvmm()
    return txdata

def fbnosilence(fbdata):
    for p in range(len(fbdata)//64):
        fbdat = fbdata[64*p:64*(p+1)]
        alg = fbdat[12] & 7
        outlevel = 0
        eglevel = 0
        for op in range(4):
            if fourop.carrier(alg, op):
                outlevel += (127 - fbdat[(40, 32, 24, 16)[op]])
                outlevel *= (fbdat[0x0b] >> (6-op)) & 1
                eglevel += (15 - (fbdat[(47, 39, 31, 23)[op]] >> 4))
        if outlevel * eglevel < 4:
            fbdata[64*p:64*(p+1)] = fb01.initfb()
    return fbdata

def rdxnosilence(rdxdata):
    for p in range(len(rdxdata)//150):
        rdxdat = rdxdata[150*p:150*(p+1)]
        alg = min(rdxdat[16], 11)
        outlevel = 0
        eglevel = 0
        allow = 0
        for op in range(4):
            if reface.carrier(alg, op):
                eglevel += max(rdxdat[0x05 + 38 + 28*op: 0x09 + 38 + 28*op])
                outlevel += (rdxdat[0x12 + 38 + 28*op] * rdxdat[38 + 28*op])
            if rdxdat[0x15 + 38 + 28*op]: #Fixed Freq
                crs = rdxdat[0x16 + 38 + 28*op]
                fine = rdxdat[0x17 + 38 + 28*op]
                if reface.freq(crs, fine, 1) > 16:
                    allow += 1
            else:
                allow += 1

        if (eglevel * outlevel * allow) < 4:
            rdxdata[150*p:150*(p+1)] = reface.initrdx()
    return rdxdata

def txexclude(txdata, exclude):
    return txfind(txdata, exclude, False)

def fbexclude(fbdata, exclude):
    return fbfind(fbdata, exclude, False)

def rdxexclude(rdxdata, exclude):
    return rdxfind(rdxdata, exclude, False)

