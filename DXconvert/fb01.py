# Based on C code for FB to DX7 conversion by Sean Bolton
# ported to Python and improved by M.T.
import os
from . import fourop
from . import dx7
from . import dxcommon
#from . import fbtables
from math import log
try:
    range = xrange
except NameError:
    pass
N = 2.**(1./16.)

#FBTABLES
#LFOSPEED
lfs = [0.]*256
fb250 = 48.0
for i in range(256):
    lfs[i] = fb250 * (2. ** (1. / 16.)) ** (i - 250.)
lfs = tuple(lfs)

lfsh = []
for i in lfs:
    lfsh.append(round(200*i,6))
lfsh = tuple(lfsh)


# based on TX81Z measurements by Andrew Evdokimov (Thanks!)
#alg dependent tl adjustments
TLIMIT = ((0, 0, 0, 0), 
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (8, 0, 8, 0),
        (13, 13, 13, 0),
        (13, 13, 13, 0),
        (16, 16, 16, 16))

LFS = (0, 31, 74, 89, 106, 114, 125, 133, 138, 144, 
        148, 153, 157, 161, 165, 167, 171, 173, 176, 178, 
        181, 184, 185, 188, 189, 191, 194, 195, 197, 198, 
        200, 201, 203, 205, 206, 207, 208, 210, 211, 212, 
        213, 214, 216, 217, 218, 219, 220, 221, 222, 223, 
        223, 225, 226, 226, 227, 228, 229, 230, 231, 231, 
        232, 233, 234, 234, 235, 236, 237, 237, 238, 238, 
        239, 240, 240, 241, 242, 242, 243, 244, 244, 245, 
        246, 246, 247, 247, 248, 249, 249, 250, 250, 251, 
        251, 252, 252, 253, 253, 253, 254, 255, 255, 255)

LFSH = (0, 2, 5, 7, 10, 12, 15, 18, 20, 23, 
        25, 28, 30, 33, 36, 38, 41, 43, 46, 48, 
        51, 54, 56, 59, 61, 64, 67, 69, 72, 74, 
        77, 79, 82, 85, 87, 90, 92, 95, 97, 100, 
        103, 105, 108, 110, 113, 116, 118, 121, 123, 126, 
        128, 131, 134, 136, 139, 141, 144, 146, 149, 152, 
        154, 157, 159, 162, 165, 167, 170, 172, 175, 177, 
        180, 183, 185, 188, 190, 193, 195, 198, 201, 203, 
        206, 208, 211, 213, 216, 219, 221, 224, 226, 229, 
        232, 234, 237, 239, 242, 244, 247, 250, 252, 255)

AMD = (0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 
        2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 
        5, 5, 5, 6, 6, 6, 7, 7, 7, 7, 
        8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 
        11, 12, 12, 12, 13, 13, 14, 14, 15, 15, 
        16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 
        21, 21, 22, 23, 23, 24, 25, 25, 26, 27, 
        28, 28, 29, 30, 31, 32, 33, 34, 35, 36, 
        37, 38, 40, 41, 42, 44, 45, 48, 49, 51, 
        54, 56, 60, 62, 67, 70, 77, 86, 96, 127)

PMD = (0, 0, 2, 3, 4, 5, 7, 8, 9, 11, 
        12, 13, 14, 16, 17, 18, 20, 21, 22, 23, 
        25, 26, 27, 29, 30, 31, 33, 34, 35, 36, 
        38, 39, 40, 42, 43, 44, 45, 47, 48, 49, 
        51, 52, 53, 54, 56, 57, 58, 60, 61, 62, 
        63, 65, 66, 67, 69, 70, 71, 72, 74, 75, 
        76, 78, 79, 80, 82, 83, 84, 85, 87, 88, 
        89, 91, 92, 93, 94, 96, 97, 98, 100, 101, 
        102, 103, 105, 106, 107, 109, 110, 111, 112, 114, 
        115, 116, 118, 119, 120, 121, 123, 124, 125, 127)

def out2tl(out, alg, op):
    TL = dxcommon.out2tl(out) + TLIMIT[alg][op]
    return min(127, TL)

def tl2out(tl, alg, op):
    TL = max(0, tl - TLIMIT[alg][op])
    return dxcommon.tl2out(TL)

#FB INIT VOICE
def initfb():
    initfb = (83, 105, 110, 101, 87, 97, 118, 0, 205, 128, 0, 120, 0, 0, 64, 0,
          127, 0, 0, 1, 31, 128, 0, 15, 127, 0, 0, 1, 31, 128, 0, 15,
          127, 0, 0, 1, 31, 128, 0, 15, 0, 0, 0, 1, 31, 128, 0, 15,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    return list(initfb)

twave = (0x04, 0x06, 0x00, 0x0a)

talg = ( 0x00, 0x0d, 0x07, 0x06, 0x04, 0x15, 0x1e, 0x1f )

dxop1 = ( 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33 )
dxop2 = ( 0x22, 0x22, 0x11, 0x22, 0x22, 0x22, 0x22, 0x22 )
dxop3 = ( 0x11, 0x11, 0x00, 0x11, 0x11, 0x11, 0x11, 0x11 )
dxop4 = ( 0x00, 0x00, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00 )

tdt = ( 0x38, 0x40, 0x48, 0x50, 0x38, 0x30, 0x28, 0x20 )

tff = ( 0x00, 0x29, 0x39, 0x49 )

freq_fb01_dx21 = (0, 1, 2, 3, 
        4, 5, 6, 7, 
        8, 9, 11, 12, 
        10, 14, 15, 17, 
        13, 18, 20, 21, 
        16, 23, 24, 27, 
        19, 26, 29, 32, 
        22, 30, 33, 37, 
        25, 35, 38, 41, 
        28, 39, 44, 47, 
        31, 43, 48, 51, 
        34, 46, 50, 54, 
        36, 49, 53, 57, 
        40, 52, 56, 60, 
        42, 55, 59, 62, 
        45, 58, 61, 63)

freq_fb01 = (0.5, 0.71, 0.78, 0.87, 
        1.0, 1.41, 1.57, 1.73, 
        2.0, 2.82, 3.14, 3.46, 
        3.0, 4.24, 4.71, 5.19, 
        4.0, 5.65, 6.28, 6.92, 
        5.0, 7.07, 7.85, 8.65, 
        6.0, 8.48, 9.42, 10.38, 
        7.0, 9.89, 10.99, 12.11, 
        8.0, 11.3, 12.56, 13.84, 
        9.0, 12.72, 14.13, 15.57, 
        10.0, 14.1, 15.7, 17.3, 
        11.0, 15.55, 17.27, 19.03, 
        12.0, 16.96, 18.84, 20.76, 
        13.0, 18.37, 20.41, 22.49, 
        14.0, 19.78, 21.98, 24.22, 
        15.0, 21.2, 23.55, 25.95)

###

pms_factor = (0, 0.111, 0.122, 0.156, 0.189, 0.232, 0.573, 0.653)

# FB01->DX7 output level
out = (98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83,
        82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67,
        66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51,
        50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35,
        34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 20,
        19, 18, 18, 17, 16, 15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 10,
        10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 5, 4, 4, 4, 4,
        3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0)

def opconv(fbop, ams):
    dxop = [0] * 0x11
    dxop[0] = fourop.r1[fbop[4] & 31]   #R1
    dxop[1] = fourop.r2[fbop[5] & 31]   #R2
    dxop[2] = fourop.r3[fbop[6] & 31]   #R3
    dxop[3] = fourop.r4[fbop[7] & 15]   #R4
    dxop[4] = 99    #L1
    dxop[5] = fourop.l2[15-(fbop[7] >> 4)]   #L2
    D2R = fbop[6]&31
    if D2R==0:
        dxop[6] = dxop[5]
    else:
        dxop[6] = 0
    #dxop[6] = int(dxop[5] * ((31-D2R)/31.0))    #L3
   
    # Level Scaling (needs more testing)
    BP=0
    LC=0
    RC = (0, 3, 1, 2)[((fbop[1]>>7)&1)+((fbop[3]>>6)&2)]
    LD=0
    if (RC==0) or (RC==3): #LIN
        RD = int(round(0.7*((fbop[2]>>4)&15)))
    else: #EXP
        RD = 5*((fbop[2]>>4)&15)
    dxop[10] = RD
    dxop[11] = (RC<<2)+LC

    dxop[12] = tdt[(fbop[3] >> 4) & 7] | (fbop[4] >> 5) #OSC DET, RS

    KVS = (fbop[1]>>4)&7
    AMS = ams * (fbop[5]>>7)
    AMS = (0, 2, 3, 3)[AMS]    # TODO: DX7II_AMS = (0, 2, 4, 5)[AMS]
    dxop[13] = (KVS<<2) + AMS  #KVS, AMS


    #OUT LEVEL
    tl = fbop[0]&127
    tl = min(127, tl+(fbop[2]&15)) #TL adjust (?)
    dxop[14] = out[tl]
    '''
    if (fbop[0] > 99):
        dxop[14] = 0
    else:
        dxop[14] = 99 - fbop[0]
    '''

    dxop[15] = (fbop[3] & 15) << 1 #FCoarse, Mode

    dxop[16] = tff[fbop[6] >> 6]    #FFine
    return dxop

def fb2vmem(fb):
    fb = fbclean(fb)
    dx = dx7.initvmem()
    dx[14] = 0
    dx[99] = 0
    dx2 = dx7.initamem()

    #dx[118:121] = dxcommon.string2list("FB:")
    for i in range(7):
        dx[i + 118] = fb[i] #NAME
    dx[125:128] = [0x20, 0x20, 0x20]

    i = fb[15]
    if (i>127):
        i=i-256
    i += 24
    while (i < 0):
        i += 12
    while (i > 48): 
        i -= 12
    dx[117] = i #TRANSPOSE
    
    # PMS, LFO wave, LFO sync
    PMS = (fb[13]>>4)&7
    LFW = (2, 3, 0, 5)[(fb[14]>>5)&3]
    LFKS = (fb[10]>>7)&1
    dx[116] = (PMS<<4) + (LFW<<1) + LFKS
    
    #dx[115] = int(0.78*(fb[9]&127))  #LAMD
    amd_fb = fb[9]&127
    if amd_fb == 0:
        dx[115] = 0
    else:
        dx[115] = int(round(max(0, min(99, 99 + log(amd_fb/53.4, N)))))

    # LPMD
    LPMD = fb[10]&127
    LPMD = pms_factor[PMS] * LPMD
    LPMD = int(round(LPMD * 0.78))
    ASGN=fb[59]>>4
    if ASGN == 0:
        dx[114] = LPMD
    elif ASGN == 1: #AT PITCH MOD
        dx2[20] = LPMD
    elif ASGN == 2: #MW PITCH MOD
        dx2[9] = LPMD
    elif ASGN == 3: #BC PITCH MOD
        dx2[16] = LPMD
    elif ASGN == 4: #FC PITCH MOD
        dx2[12] = LPMD

    # FB-01 xrange is 0-255
    if LFW == 5: # S/H
        lfspeed = lfsh[fb[8]]
    else:
        lfspeed = lfs[fb[8]]
    dx[112] = dxcommon.closeto(lfspeed, dx7.lfs)

    dx[111] = (fb[12] >> 3) & 7 #FB

    alg = fb[12] & 7;
    dx[110] = talg[alg] #ALS
    
    dx[dxop1[alg]:dxop1[alg]+17] = opconv(fb[40:48], fb[13]&3)
    dx[dxop2[alg]:dxop2[alg]+17] = opconv(fb[32:40], fb[13]&3)
    dx[dxop3[alg]:dxop3[alg]+17] = opconv(fb[24:32], fb[13]&3)
    dx[dxop4[alg]:dxop4[alg]+17] = opconv(fb[16:24], fb[13]&3)
    
    return dx, dx2

def fb2vmm(fb, yamaha='tx81z'):
    fb = fbclean(fb)
    vmm = fourop.initvmm()
    ALG=fb[12]&7
    for op in range(4):
        vmad = (30, 10, 20, 0)[op]
        fbad = (40, 32, 24, 16)[op]
        vmm[0+vmad] = fb[4+fbad]&31    #AR
        vmm[1+vmad] = fb[5+fbad]&31    #D1R
        vmm[2+vmad] = fb[6+fbad]&31    #D2R
        vmm[3+vmad] = max(1, fb[7+fbad]&15)    #RR
        vmm[4+vmad] = 15-(fb[7+fbad]>>4)    #D1L
        vmm[5+vmad] = int(6.6*(fb[2+fbad]>>4))    #LS
        if fb[1+fbad]>>7 == 1: #negative level scaling
            if yamaha  != 'v50':
                vmm[5+vmad] = 0
       
        AME = fb[5+fbad]>>7
        KVS = (fb[1+fbad]>>4)&7
        vmm[6+vmad] = (AME<<6) + KVS
        
        #OUT LEVEL
        tl = fb[fbad]
        if tl<87:
            tl += (fb[2]&15) #TLADJ
        vmm[7 + vmad] = tl2out(tl, ALG, op)

        mul = fb[3+fbad]&15
        ih = fb[6+fbad]>>6
        freq = freq_fb01[4 * mul + ih]
        vmm[8 + vmad] = dxcommon.closeto(freq, fourop.freq_dx21)
        
        DET = (fb[3+fbad]>>4)&7
        if DET>3:
            DET = -(DET&3)
        DET += 3
        if yamaha == 'v50':
            LS2 = fb[1+fbad]>>7
        else:
            LS2 = 0
        KVS2 = 0
        RS = fb[4+fbad]>>6
        vmm[9+vmad] = (LS2<<6) + (KVS2<<5) + (RS<<3) + DET
    
    FBL = (fb[12]>>3)&7
    SY = 0
    vmm[40] = (SY<<6) + (FBL<<3) + ALG
   
    if (fb[14]>>5) == 3:    #LFW=S/Hold
        vmm[41] = dxcommon.closeto(fb[8], LFSH)
    else:
        vmm[41] = dxcommon.closeto(fb[8], LFS)
    
    #vmm[42] = LFD
    pmd = dxcommon.closeto(fb[10]&127, PMD)
    vmm[44] = dxcommon.closeto(fb[9]&127, AMD)
    PMS = (fb[13]>>4)&7
    AMS = fb[13]&3
    LFW = (fb[14]>>5)&3
    vmm[45] = (PMS<<4) + (AMS<<2) + LFW

    TRPS = fb[15]
    if (TRPS>127):
        TRPS -= 256
    TRPS += 24
    while (TRPS < 0):
        TRPS += 12
    while (TRPS > 48): 
        TRPS -= 12
    vmm[46] = TRPS
    vmm[47] = fb[59]&15 #PBR
    vmm[48] = fb[58]>>4 #MONO
    vmm[49] = int(0.78*(fb[58]&127)) #PORT
    ASGN=fb[59]>>4
    if ASGN == 0:
        vmm[43] = pmd
    elif ASGN == 1: #AT PITCH MOD
        vmm[84] = pmd
    elif ASGN == 2: #MW PITCH MOD
        vmm[51] = pmd
    elif ASGN == 3: #BC PITCH MOD
        vmm[53] = pmd
    elif ASGN == 4: #FC PITCH MOD
        vmm[82] = pmd
    vmm[57:67] = fb[:7] + [0x20, 0x20, 0x20] #FB:VOICENAME
    return vmm

def vmm2fb(vmm):
    fb = initfb()
    vmm = fourop.cleanvmm(vmm)
    vmm = fourop.tx81z_dx21(vmm)[0]
    transposed = fourop.tx81z_dx21(vmm)[1]
    vcd, acd, acd2, acd3, efeds, delay = fourop.vmm2vcd(vmm)
    fb[:7] = name2seven(vcd[77:87]) #NAME
    if vcd[59] == 3: #S/H LFS
        fb[8] = LFSH[vcd[54]]
    else: # normal LFS
        fb[8] = LFS[vcd[54]]
    amd = AMD[vcd[57]]
    fb[9] = 128 + amd # LFO-load-enable AMD
    fb[10] = (vcd[58]<<7) + PMD[vcd[56]]   # LFOsync PMD
    fb[11] = 0b01111000 # OPERATOR on/off
    fb[12] = 0b11000000 + (vcd[53]<<3) + vcd[52]  # FBL ALG
    fb[13] = (vcd[60]<<4) + vcd[61] # PMS AMS
    fb[14] = vcd[59]<<5  # LFW
    TRPS = vcd[62] - 24 - transposed
    if TRPS < 0:
        TRPS += 256
    fb[15] = TRPS
    fb[0x3a] = (vcd[63]<<7) + int(1.28 * vcd[66])
    # CTRL = 0 #0=Off #1=ATPM #2=MWPM #3=BCPM #4=FCPM
    if vcd[56]>0:
        CTRL = 0
    else:
        CTRlist = (vcd[56], acd2[0], vcd[71], vcd[73], acd[21])  
        CTRL = CTRlist.index(max(CTRlist))
    fb[0x3b] = (CTRL << 4) + vcd[64]

    for op in range(4):
        vcad = (39, 13, 26, 0)[op]
        acad = (15, 5, 10, 0)[op]
        fbad = (40, 32, 24, 16)[op]
        TL = dxcommon.out2tl(vcd[10 + vcad])
        TLADJ = min(15, out2tl(vcd[10 + vcad], vcd[52], op) - TL)
        freq = fourop.freq_dx21[vcd[(50, 24, 37, 11)[op]] & 63]
        crs = dxcommon.closeto(freq, freq_fb01)
        MUL = (crs >> 2) & 15
        DT2 = crs & 3  #DT2 = IH
        DT1 = (7, 6, 5, 0, 1, 2, 3, 4)[vcd[12 + vcad]] 
        KVS = vcd[9 + vcad]
        if KVS>7: 
            KVS = 0
        LSTYPE0 = (acd2[8] >> (3 - op)) & 1 #LS SIGN
        LSTYPE1 = 0 #LS LINEAR
        LS = int(round((0.152 * vcd[5 + vcad])))
        RS = vcd[6 + vcad] & 3
        #AME = vcd[8 + vcad] & 1  #!!??
        CARRIER = fourop.carrier(vcd[52], op)
        AME = int(CARRIER)
        AR = vcd[0 + vcad] & 31
        KVSAR = 0
        D1R = vcd[1 + vcad] & 31
        D2R = vcd[2 + vcad] & 31
        RR = vcd[3 + vcad] & 15
        SL = 15 - vcd[4 + vcad] & 15
        fb[fbad + 0] = TL
        fb[fbad + 1] = (LSTYPE0<<7) + (KVS<<4)
        fb[fbad + 2] = (LS<<4) + TLADJ
        fb[fbad + 3] = (LSTYPE1<<7) + (DT1<<4) + MUL
        fb[fbad + 4] = (RS<<6) + AR
        fb[fbad + 5] = (AME<<7) + (KVSAR<<5) + D1R
        fb[fbad + 6] = (DT2<<6) + D2R
        fb[fbad + 7] = (SL<<4) + RR
    return fb

def name2seven(name):
    newname = [32] * 7
    n = 0
    for i in name:
        if i in range(32, 128):
            newname[n] = i
            n += 1
        if n == 7:
            break
    #print("{} ({})".format(dxcommon.list2string(newname), len(newname)))
    return newname

def fbclean(fb):
    if fb == 64 * [fb[0]]:
        return initfb()
    for i in range(7):
        if fb[i] not in range(32, 128):
            fb[i] = 32
    if fb[:7] == [32]*7:
        return initfb()
    fb[11] = fb[11] & 0b01111000
    fb[12] = fb[12] & 0b00111111
    fb[13] = fb[13] & 0b01110011
    fb[14] = fb[14] & 0b01100000
    for op in range(4):
        a=16+8*op
        fb[a] = fb[a] & 127
        fb[a+1] = fb[a + 1] & 0b11110000
        fb[a+4] = fb[a + 4] & 0b11011111
        fb[a+6] = fb[a + 6] & 0b11011111
    fb[59] = fb[59] & 127
    return fb

def fb2syx(fbdata, bank=0, channel=0):

    if len(fbdata) == 64:
        syx = [0xf0, 0x43, 0x75, channel, 0x28, 0x00, 0x00]
        syx += [1, 0]
        sumlist = []
        for i in range(64):
            lo = fbdata[i] & 15
            hi = (fbdata[i] >> 4) & 15
            sumlist += [lo, hi]
        syx += sumlist
        syx += [dxcommon.checksum(sumlist)]

    else:
        if (len(fbdata)//64) < 48:
            fbdata += initfb() * (48 - len(fbdata)//64)

        fbinfo = "YAMAHA FB-01 VOICEDATA          "
        syx = [0xf0, 0x43, 0x75, channel, 0x00, 0x00, bank]
        syx += [0x00, 0x40]
        sumlist = []
        for i in range(32):
            lo = ord(fbinfo[i]) & 15
            hi = ord(fbinfo[i]) >> 4
            sumlist += [lo, hi]
        syx += sumlist
        syx += [dxcommon.checksum(sumlist)]

        for n in range(48):
            syx += [1, 0]
            sumlist = []
            for i in range(64):
                lo = fbdata[64 * n + i] & 15
                hi = (fbdata[64 * n + i] >> 4) & 15
                sumlist += [lo, hi]
            syx += sumlist
            syx += [dxcommon.checksum(sumlist)]

    syx += [0xf7]
    return syx

def det(detune):
    return ('+0', '+1', '+2', '+3', '-0', '-1', '-2', '-3')[detune]

def fb2txt(fbdata):
    Oo = ('Off', 'On')
    lstyp = ('Lin', 'Exp')
    lssig = ('-', '+')
    s = ''
    if len(fbdata)//64 == 1:
        s += 'YAMAHA FB-01 PARAMETERLIST:\n\n'
        s += 'NAME      : {:>8}\n'.format(dxcommon.list2string(fbdata[:7]))
        s += 'LFO speed : {:>8}\n'.format(fbdata[8])
        s += 'LFO enable: {:>8}\n'.format(fbdata[9] >> 7)
        s += 'AMD       : {:>8}\n'.format(fbdata[9] & 127)
        s += 'LFO sync  : {:>8}\n'.format(fbdata[10] >> 7)
        s += 'PMD       : {:>8}\n'.format(fbdata[10] & 127)
        s += 'FB level  : {:>8}\n'.format(fbdata[12] >> 3 & 7)
        s += 'Algorithm : {:>8}\n'.format(1 + (fbdata[12] & 7))
        s += 'PMS       : {:>8}\n'.format(fbdata[13] >> 4 & 7)
        s += 'AMS       : {:>8}\n'.format(fbdata[13] & 3)
        lfw = ('Saw Up', 'Square', 'Triangle', 'S/Hold')
        s += 'LFW       : {:>8}\n'.format(lfw[fbdata[14] >> 5 & 3])
        trps = fbdata[15]
        if trps>127:
            trps = str(trps - 256)
        else:
            trps = '+' + str(trps)
        s += 'TRPS      : {:>8}\n'.format(trps)
        s += 'MONO      : {:>8}\n'.format(fbdata[58] >> 7)
        s += 'PORT      : {:>8}\n'.format(fbdata[58] & 127)
        s += 'PMD ctrl  : {:>8}\n'.format(fbdata[59] >> 4)
        s += 'PBR       : {:>8}\n\n'.format(fbdata[59] & 15)
        
        s += '                 OP1      OP2      OP3      OP4\n'
        s += 'OP enable : {:>8} {:>8} {:>8} {:>8}\n'.format(Oo[fbdata[11]>>3&1], Oo[fbdata[11]>>4&1], Oo[fbdata[11]>>5&1], Oo[fbdata[11]>>6&1])
        s += '127-TL    : {:>8} {:>8} {:>8} {:>8}\n'.format(127-fbdata[40], 127-fbdata[32], 127-fbdata[24], 127-fbdata[16])
        s += 'TL Adjust : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[42]&15, fbdata[34]&15, fbdata[26]&15, fbdata[18]&15)
        s += 'MUL       : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[43]&15, fbdata[35]&15, fbdata[27]&15, fbdata[19]&15)
        s += 'DT2 (ih)  : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[46]>>6, fbdata[38]>>6, fbdata[30]>>6, fbdata[22]>>6)
        f1 = freq_fb01[4*(fbdata[43]&15) + (fbdata[46]>>6)]
        f2 = freq_fb01[4*(fbdata[35]&15) + (fbdata[38]>>6)]
        f3 = freq_fb01[4*(fbdata[27]&15) + (fbdata[30]>>6)]
        f4 = freq_fb01[4*(fbdata[19]&15) + (fbdata[22]>>6)]
        s += 'Freq.ratio: {:>8} {:>8} {:>8} {:>8}\n'.format(f1, f2, f3, f4)
        s += 'DT1 (det.): {:>8} {:>8} {:>8} {:>8}\n'.format(det(fbdata[43]>>4&7), det(fbdata[35]>>4&7), det(fbdata[27]>>4&7), det(fbdata[19]>>4&7))
        s += 'LS type   :     {}{}     {}{}     {}{}     {}{}\n'.format(lssig[fbdata[41]>>7],
                lstyp[fbdata[43]>>7], 
                lssig[fbdata[33]>>7], 
                lstyp[fbdata[35]>>7], 
                lssig[fbdata[25]>>7], 
                lstyp[fbdata[27]>>7], 
                lssig[fbdata[17]>>7],
                lstyp[fbdata[19]>>7])
        s += 'LS depth  : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[42]>>4, fbdata[34]>>4, fbdata[26]>>4, fbdata[18]>>4)
        s += 'RS depth  : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[44]>>6, fbdata[36]>>6, fbdata[28]>>6, fbdata[20]>>6)
        s += 'AME       : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[45]>>7, fbdata[37]>>7, fbdata[29]>>7, fbdata[21]>>7)
        s += 'KVS       : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[41]>>4&7, fbdata[33]>>4&7, fbdata[25]>>4&7, fbdata[17]>>4&7) 
        s += 'KVSAR     : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[45]>>5&3, fbdata[37]>>5&3, fbdata[29]>>5&3, fbdata[21]>>5&3)
        s += 'AR        : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[44]&31, fbdata[36]&31, fbdata[28]&31, fbdata[20]&31)
        s += 'D1R       : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[45]&31, fbdata[37]&31, fbdata[29]&31, fbdata[21]&31)
        s += 'D2R       : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[46]&31, fbdata[38]&31, fbdata[30]&31, fbdata[22]&31)
        s += '15-SL     : {:>8} {:>8} {:>8} {:>8}\n'.format(15-(fbdata[47]>>4), 15-(fbdata[39]>>4), 15-(fbdata[31]>>4), 15-(fbdata[23]>>4))
        s += 'RR        : {:>8} {:>8} {:>8} {:>8}\n'.format(fbdata[47]&15, fbdata[39]&15, fbdata[31]&15, fbdata[23]&15)
    else:
        for i in range(len(fbdata)//64):
            s += "{:03}: {}\n".format(i+1, dxcommon.list2string(fbdata[64*i:64*i+7]))
            if i%48 == 47:
                s += '\n'
    return dxcommon.string2list(s + '\n')

def tfm2fb(tfm, fn):
    vname = os.path.basename(fn)[:-4] + "       "
    vname = vname[:7]
    fb = initfb()
    ALG = tfm[0]
    FBL = tfm[1] 
    fb[:7] = dxcommon.string2list(vname)
    fb[0x0c] = (FBL<<3) + ALG
    for op in range(4):
        fop = (16, 32, 24, 40)[op]
        MUL = tfm[10*op + 2]
        DT = tfm[10*op + 3]
        TL = tfm[10*op + 4]
        RS = tfm[10*op + 5]
        AR = tfm[10*op + 6]
        DR = tfm[10*op + 7]
        SR = tfm[10*op + 8]
        RR = tfm[10*op + 9]
        SL = tfm[10*op + 10]
        SSG = 10*op + 11

        fb[fop] = TL
        fb[fop + 0x03] = (DT<<4) + MUL
        fb[fop + 0x04] = (RS<<6) + AR
        fb[fop + 0x05] = DR
        fb[fop + 0x06] = SR
        fb[fop + 0x07] = (SL<<4) + RR 
    return fb

