import os
from subprocess import call
from array import array
from tempfile import mkstemp
from . import fourop
from . import dx7
from . import dx9
from . import dxcommon
try:
    range = xrange
except NameError:
    pass

tx7head = [0xf8, 0xc8, 0x00, 0xd9, 
            0xf8, 0xc8, 0x59, 0x4d,
            0x54, 0x58, 0x37, 0x10, 0x20]

def wav2syx(wavfile, mode='tx'):
    dxtxdata = []
    cas, castemp = mkstemp(suffix='.cas')
    os.close(cas)
    opts = '-p -e 4 -t 10'

    try:
        call('wav2cas {} "{}" "{}"'.format(opts, wavfile, castemp), shell=True)
    except:
        print ("error: wav2cas failed")
        os.remove(castemp)
        return dxtxdata

    size = os.path.getsize(castemp)
    data = array('B')
    with open(castemp, 'rb') as f:
        data.fromfile(f, size)
    os.remove(castemp)
    data = data.tolist()
    if data[:8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
        if mode == 'tx':
            for i in range(len(data)-84):
                if data[i:i+8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                    dxtxdata += cas2vmm(data, i+8)
            if (data[8+64] in range(20)) and (sum(data[8:8+64]) == 256*data[8+65] + data[8+66]):
                for i in range(len(data)-66):
                    if data[i:i+8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                        if data[i+8+64] in range(20) and (sum(data[i+8:i+8+65]) == 256*data[i+8+65] + data[i+8+66]):
                            dxtxdata += dx9cas2vmm(data, i + 8)

        elif mode == 'dx':
            if data[8:21] == tx7head: # "YMTX7"
                for i in range(32):
                    dxtxdata += cas2vmem(data, 22 + 128*i)
        
            elif data[46:51] == dxcommon.string2list("YMDX7"): #YRM-103 DX7 editor CX5M
                for i in range(48):
                    dxtxdata += cas2vmem(data, 54 + 128*i)

            elif (data[8+64] in range(20)) and (sum(data[8:8+64]) == 256*data[8+65] + data[8+66]): #DX9
                for i in range(len(data)-66):
                    if data[i:i+8] == [0x1f, 0xa6, 0xde, 0xba, 0xcc, 0x13, 0x7d, 0x74]:
                        if data[i+8+64] in range(20) and (sum(data[i+8:i+8+65]) == 256*data[i+8+65] + data[i+8+66]):
                            dxtxdata += dx9cas2vmem(data, i + 8)
                    
    return dxtxdata

def cas2vmm(data, offset):
    vmm = fourop.initvmm()
    if data[offset+73] in range(0x80, 0xA0) and (data[offset+73] == data[offset+89]):
        # DX11
        if sum(data[offset:offset+90]) == (data[offset+90]*256 + data[offset+91]):
            vmm[:73] = data[offset:offset+73]
            vmm[73:88] = data[offset+74:offset+89]
    if data[offset+73] in range(0x20, 0x40) and (data[offset+73] == data[offset+85]):
        # TX81Z
        if sum(data[offset:offset+86]) == (data[offset+86]*256 + data[offset+87]):
            vmm[:73] = data[offset:offset+73]
            vmm[73:84] = data[offset+74:offset+85]
    if data[offset+73] in range(0x00, 0x20):
        # DX21/27/100
        if sum(data[offset:offset+74]) == (data[offset+74]*256 + data[offset+75]):
            vmm[:73] = data[offset:offset+73]
    return vmm

def cas2vmem(data, offset):
    # TX7 data 
    vmem = dx7.initvmem()
    for p in range(128):
        vmem[p] = data[offset+p]&127
    return vmem

def dx9cas2vmem(data, offset):
    # DX9 data
    dd = data[offset:offset+64]
    vmem = dx7.initvmem()
    vmem[99] = 0 #OP1 level
    voicenr = data[offset+64]
    voicename = "DX9.{:>2}    ".format(voicenr+1)
    vmem[118:128] = dxcommon.string2list(voicename)
    for opad in range(4):
        opa9 = 14*opad
        opa7 = 17*opad
        for i in range(8):
            vmem[opa7 + i] = dd[opa9 + i]
        vmem[opa7 + 8 ] = 15 # BP = C1
        #vmem[opa7 + 9] = LD
        vmem[opa7 + 10] = dd[opa9 + 8]
        vmem[opa7 + 11] = 4 # RC=-EXP LC=-LIN
        vmem[opa7 + 12] = (dd[opa9 + 13] << 3) + (dd[opa9 + 9] & 7)
        #vmem[opa7 + 13] = KVS(0-7), AMS(0-3)
        vmem[opa7 + 14] = dd[opa9 + 10]
        vmem[opa7 + 15] = dd[opa9 + 11] << 1
        vmem[opa7 + 16] = dd[opa9 + 12]
    #vmem[102:110] = PEG
    vmem[0x6e] = (0, 13, 7, 6, 4, 21, 30, 31)[dd[0x38]] #ALG
    vmem[0x6f] = dd[0x39] #OSCSYNC=0, FB
    vmem[0x70] = dd[0x3a] #LFS
    vmem[0x71] = dd[0x3b] #LFD
    vmem[0x72] = dd[0x3c] #PMD
    vmem[0x73] = dd[0x3d] #AMD
    vmem[0x74] = dd[0x3e] << 1 #(PMS) LFW (LFO KEYSYNC) 
    vmem[0x75] = dd[0x3f] + 12 #TRSP
    return vmem

def dx9cas2vmm(data, offset):
    vmem = dx9cas2vmem(data, offset)
    return dx9.dx9to4op(vmem)


