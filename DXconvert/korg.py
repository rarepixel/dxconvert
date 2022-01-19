# convert Korg DS8 and 707 fourop FM voicedata
# to Yamaha 4-OP FM voicedata
from . import dx7
from . import fourop
from . import fb01
import math
from . import dxcommon
try:
    range = xrange
except NameError:
    pass

#LFO
lfs = (0.0334, 0.0502, 0.0803, 0.1133, 
       0.1534, 0.2008, 0.2664, 0.3341, 
       0.4001, 0.4551, 0.5176, 0.5887, 
       0.6695, 0.7615, 0.8661, 0.9850, 
       1.1203, 1.2288, 1.3478, 1.4783, 
       1.6215, 1.7785, 1.9508, 2.1397, 
       2.3469, 2.5289, 2.7251, 2.9364, 
       3.1642, 3.4096, 3.6741, 3.9591, 
       4.2662, 4.4496, 4.6408, 4.8403, 
       5.0483, 5.2652, 5.4915, 5.7276, 
       5.9737, 6.2459, 6.5306, 6.8282, 
       7.1393, 7.4647, 7.8049, 8.1605, 
       8.5324, 9.4676, 10.5054, 11.6569, 
       12.9345, 14.3523, 15.9254, 17.6710, 
       19.6078, 23.2450, 26.2230, 30.5773, 
       35.0699, 40.2225, 46.1321, 52.9101) 

lfsh = []
for i in lfs:
    lfsh.append(16*i)
lfsh = tuple(lfsh)

amd = []
for i in range(64):
    amd.append(0.7279*i)

dstimes = (0.04, 0.12, 0.28, 0.36, 0.52, 0.76, 1.0, 1.5, 2.0, 2.5,
        3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 
        8.0, 8.5, 9.0, 9.5, 10.0, 11, 12, 13, 14, 15, 
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 
        26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 
        42, 44, 46, 48, 50, 52, 55, 58, 60, 62, 
        65, 68, 70, 72, 75, 78, 80, 82, 85, 88, 
        90, 92, 95, 98, 100, 105, 110, 115, 120, 125, 
        130, 135, 140, 145, 150, 160, 170, 180, 190, 200, 
        210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 
        310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 
        420, 450, 480, 500, 520, 550, 580, 600, 620, 650, 
        680, 700, 720, 750, 780, 800, 820, 850)

def delaytime_ds_v50(dstime):
    ystime = int(round(dstimes[dstime]/4.))
    return min(75, ystime)

def dblrtime_ds_v50(dstime):
    vtime = int(round(dstimes[dstime]*2.))
    return min(80, vtime)

lfdtime = (
    0.000, 0.084, 0.095, 0.113,
    0.141, 0.180, 0.224, 0.273,
    0.330, 0.399, 0.467, 0.545,
    0.625, 0.710, 0.820, 0.950,
    1.086, 1.225, 1.385, 1.550,
    1.740, 1.968, 2.240, 2.570,
    2.980, 3.500, 4.123, 4.911,
    5.800, 6.878, 8.032, 9.468)

def korg7to8(mid):
    nn = len(mid)//8
    dat = [0]*7*nn
    for n in range(nn):
        for bb in range(7):
            dat[7*n+bb] = mid[8*n+bb+1] + 128*((mid[8*n]>>bb)&1)
    return dat

def korg8to7(dat):
    nn = (len(dat) + (len(dat)%7))//7
    mid = [0]*8*nn
    for n in range(nn):
        for bb in range(7):
            mid[8*n] += (dat[bb+7*n]>>7)<<bb
            mid[8*n+bb+1] = dat[bb+7*n] & 127
    return mid

def vce2bnk(vce, ds8=False):
    bnk = [0] * 66
    bnk[0] = vce[0] & 15
    bnk[1] = vce[1] & 15
    bnk[2] = vce[2] & 3

    bnk[3] = vce[3] & 127
    bnk[4] = vce[4] & 63
    bnk[5] = vce[5] & 127
    bnk[6] = vce[6] & 63
    bnk[7] = vce[7] & 63
    bnk[8] = vce[8] & 127

    bnk[9] = (vce[9] & 3)
    bnk[9] += (vce[10] & 7) << 2  
    bnk[10] = (vce[11] & 3)
    bnk[10] += (vce[12] & 1) << 2
    bnk[11] = vce[13] & 3

    bnk[12] = vce[14] & 3
    bnk[12] += (vce[15] & 7) << 2
    bnk[13] = vce[16] & 3
    bnk[13] += (vce[17] & 1) << 2
    bnk[14] = vce[18] & 3
    
    if ds8:
        bnk[15] = vce[19] & 127
        bnk[16] = vce[20] & 15
        bnk[17] = vce[21] & 31
        bnk[17] += (vce[25] & 3) << 6
        bnk[18] = vce[22] & 31
        bnk[19] = vce[23] & 15
        bnk[19] += (vce[24] & 15) << 4

        bnk[20] = vce[26] & 127
        bnk[21] = vce[27] & 15
        bnk[22] = vce[28] & 31
        bnk[22] += (vce[32] & 3) << 6
        bnk[23] = vce[29] & 31
        bnk[24] = vce[30] & 15
        bnk[24] += (vce[31] & 15) << 4

        bnk[25] = vce[33] & 63
        bnk[26] = vce[34] & 31
        bnk[26] += (vce[38] & 3) << 6
        bnk[27] = vce[35] & 31
        bnk[28] = vce[36] & 15
        bnk[28] += (vce[37] & 15) << 4

        bnk[29] = vce[39] & 63
        bnk[30] = vce[40] & 31
        bnk[30] += (vce[44] & 3) << 6
        bnk[31] = vce[41] & 31
        bnk[32] = vce[42] & 15
        bnk[32] += (vce[43] & 15) << 4
    else:
        bnk[15] = vce[19] & 127
        bnk[16] = vce[20] & 15
        bnk[17] = vce[22] & 31
        bnk[17] += (vce[21] & 3) << 6
        bnk[18] = vce[23] & 31
        bnk[19] = vce[24] & 15
        bnk[19] += (vce[25] & 15) << 4

        bnk[20] = vce[26] & 127
        bnk[21] = vce[27] & 15
        bnk[22] = vce[29] & 31
        bnk[22] += (vce[28] & 3) << 6
        bnk[23] = vce[30] & 31
        bnk[24] = vce[31] & 15
        bnk[24] += (vce[32] & 15) << 4

        bnk[25] = vce[33] & 63
        bnk[26] = vce[35] & 31
        bnk[26] += (vce[34] & 3) << 6
        bnk[27] = vce[36] & 31
        bnk[28] = vce[37] & 15
        bnk[28] += (vce[38] & 15) << 4

        bnk[29] = vce[39] & 63
        bnk[30] = vce[41] & 31
        bnk[30] += (vce[40] & 3) << 6
        bnk[31] = vce[42] & 31
        bnk[32] = vce[43] & 15
        bnk[32] += (vce[44] & 15) << 4
    
    if ds8:
        bnk[33] = vce[66] & 3
        bnk[34] = vce[67] & 63
        bnk[35] = vce[68] & 31
        bnk[36] = vce[69] & 63
        bnk[37] = vce[70] & 63
    else:
        bnk[33] = vce[67] & 3
        bnk[34] = vce[68] & 63
        bnk[35] = vce[69] & 31
        bnk[36] = vce[70] & 63
        bnk[37] = vce[71] & 63

    bnk[38] = vce[45] & 3
    bnk[38] += (vce[46] & 3) << 2
    bnk[39] = (vce[47] & 1) << 7
    bnk[39] += vce[48] & 63

    if ds8:
        bnk[40] = vce[77] & 15
        bnk[41] = vce[78] & 3
        bnk[42] = vce[79] & 3
    else:
        bnk[40] = vce[72] & 15
        bnk[41] = vce[73] & 3
        bnk[41] += (vce[74] & 3) << 2
        bnk[41] += (vce[75] & 3) << 4
        bnk[42] = vce[76] & 3

    bnk[43] = vce[49] & 7
    bnk[44] = vce[50] & 7
    bnk[45] = vce[51] & 7
    bnk[46] = vce[52] & 7

    bnk[47] = vce[77] & 3
    bnk[47] += (vce[78] & 3) << 2
    bnk[47] += (vce[79] & 3) << 4
    bnk[47] += (vce[80] & 3) << 6

    bnk[48] = (vce[53] & 1) << 7
    bnk[48] += (vce[54] & 1) << 3
    bnk[48] += (vce[55] & 3)
    
    bnk[49:59] = vce[56:66]

    if ds8:
        bnk[59] = vce[71] & 7
        bnk[60] = vce[72] & 127
        bnk[61] = vce[73] & 31
        bnk[62] = vce[74] & 31
        bnk[63] = vce[75] & 31
        bnk[64] = vce[76] & 15
    else:
        bnk[59] = vce[66] & 2
    return bnk

def bnk2vce(bnk, ds8=False):
    vce = [0]*84 
    vce[0] = bnk[0] & 15
    vce[1] = bnk[1] & 15
    vce[2] = bnk[2] & 3

    vce[3] = bnk[3] & 127
    vce[4] = bnk[4] & 63
    vce[5] = bnk[5] & 127
    vce[6] = bnk[6] & 63
    vce[7] = bnk[7] & 63
    vce[8] = bnk[8] & 127

    vce[9] = bnk[9] & 3
    vce[10] = (bnk[9] >> 2) & 7
    vce[11] = bnk[10] & 3
    vce[12] = (bnk[10] >> 2) & 1
    vce[13] = bnk[11] & 3 

    vce[14] = bnk[12] & 3
    vce[15] = (bnk[12] >> 2) & 7
    vce[16] = bnk[13] & 3
    vce[17] = (bnk[13] >> 2) & 1
    vce[18] = bnk[14] & 3

    if ds8:
        vce[19] = bnk[15] & 127
        vce[20] = bnk[16] & 15
        vce[21] = bnk[17] & 31
        vce[22] = bnk[18] & 31
        vce[23] = bnk[19] & 15
        vce[24] = (bnk[19] >> 4) & 15
        vce[25] = (bnk[17] >> 6) & 3

        vce[26] = bnk[20] & 127
        vce[27] = bnk[21] & 15
        vce[28] = bnk[22] & 31
        vce[29] = bnk[23] & 31
        vce[30] = bnk[24] & 15
        vce[31] = (bnk[24] >> 4) & 15
        vce[32] = (bnk[22] >> 6) & 3

        vce[33] = bnk[25] & 63
        vce[34] = bnk[26] & 31
        vce[35] = bnk[27] & 31
        vce[36] = bnk[28] & 15
        vce[37] = (bnk[28] >> 4) & 15
        vce[38] = (bnk[26] >> 6) & 3

        vce[39] = bnk[29] & 63
        vce[40] = bnk[30] & 31
        vce[41] = bnk[31] & 31
        vce[42] = bnk[32] & 15
        vce[43] = (bnk[32] >> 4) & 15
        vce[44] = (bnk[30] >> 6) & 3

    else: #707
        vce[19] = bnk[15] & 127
        vce[20] = bnk[16] & 15
        vce[22] = bnk[17] & 31
        vce[23] = bnk[18] & 31
        vce[24] = bnk[19] & 15
        vce[25] = (bnk[19] >> 4) & 15
        vce[21] = (bnk[17] >> 6) & 3

        vce[26] = bnk[20] & 127
        vce[27] = bnk[21] & 15
        vce[29] = bnk[22] & 31
        vce[30] = bnk[23] & 31
        vce[31] = bnk[24] & 15
        vce[32] = (bnk[24] >> 4) & 15
        vce[28] = (bnk[22] >> 6) & 3

        vce[33] = bnk[25] & 63
        vce[35] = bnk[26] & 31
        vce[36] = bnk[27] & 31
        vce[37] = bnk[28] & 15
        vce[38] = (bnk[28] >> 4) & 15
        vce[34] = (bnk[26] >> 6) & 3

        vce[39] = bnk[29] & 63
        vce[41] = bnk[30] & 31
        vce[42] = bnk[31] & 31
        vce[43] = bnk[32] & 15
        vce[44] = (bnk[32] >> 4) & 15
        vce[40] = (bnk[30] >> 6) & 3

    vce[45] = bnk[38] & 3
    vce[46] = (bnk[38] >> 2) & 3

    vce[47] = (bnk[39] >> 7) & 1
    vce[48] = bnk[39] & 63

    vce[49] = bnk[43] & 7
    vce[50] = bnk[44] & 7
    vce[51] = bnk[45] & 7
    vce[52] = bnk[46] & 7

    vce[53] = (bnk[48] >> 7) & 1
    vce[54] = (bnk[48] >> 3) & 1
    vce[55] = bnk[48] & 3

    vce[56:66] = bnk[49:59] #VOICENAME

    if ds8:
        vce[66] = bnk[33] & 3
        vce[67] = bnk[34] & 63
        vce[68] = bnk[35] & 31
        vce[69] = bnk[36] & 63
        vce[70] = bnk[37] & 63
        vce[71] = bnk[59] & 7
        vce[72] = bnk[60] & 127
        vce[73] = bnk[61] & 31
        vce[74] = bnk[62] & 31
        vce[75] = bnk[63] & 31
        vce[76] = bnk[64] & 15
        vce[77] = bnk[40] & 15
        vce[78] = bnk[41] & 3
        vce[79] = bnk[42] & 3
        vce[80] = bnk[47] & 3
        vce[81] = (bnk[47] >> 2) & 3
        vce[82] = (bnk[47] >> 4) & 3
        vce[83] = (bnk[47] >> 6) & 3
    else: #707
        vce[66] = bnk[59] & 3
        vce[67] = bnk[33] & 3
        vce[68] = bnk[34] & 63
        vce[69] = bnk[35] & 31
        vce[70] = bnk[36] & 63
        vce[71] = bnk[37] & 63
        vce[72] = bnk[40] & 15
        vce[73] = bnk[41] & 3
        vce[74] = (bnk[41] >> 2) & 3
        vce[75] = (bnk[41] >> 4) & 3
        vce[76] = bnk[42] & 3
        vce[77] = bnk[47] & 3
        vce[78] = (bnk[47] >> 2) & 3
        vce[79] = (bnk[47] >> 4) & 3
        vce[80] = (bnk[47] >> 6) & 3
    return vce

def bnk2vmm(bnk, ds8=True):
    vce = bnk2vce(bnk, ds8)
    return vce2vmm(vce, ds8)

def vce2vmm(vce, ds8=False):
    # TEG LIMIT
    if vce[12]==1:
        vce[19] = min(71, vce[19])
    if vce[17]==1:
        vce[26] = min(71, vce[26])

    if ds8:
        vmm = vce2vmm_ds8(vce)
    else:
        vmm = vce2vmm_707(vce)
    return vmm

def ratio(carf, wtyp, spct, ring, wfrm2=False):
    x = (carf + (wtyp % 2)) % 2 
    if (wtyp == 2) and (wfrm2 == True):
        mul = spct
    else:
        mul = 2 * spct + x
    ratio = fb01.freq_fb01_dx21[4*mul + ring]
    return ratio

def kvs_adjust(kvs, aeg=False):
    if aeg:
        return (0, 0, 1, 2, 2, 3, 3, 4)[kvs]
    else:
        return (0, 2, 2, 4, 4, 6, 6, 8)[kvs]
        
def vce2vmm_707(vce):
    #AMPADJUST1= #?
    TIMADJUST1=6 #?
    #AMPADJUST2= #?
    TIMADJUST2=6 #?

    vcd, acd, acd2, acd3, delay, efeds = fourop.initvcd(), fourop.initacd(), fourop.initacd2(), fourop.initacd3(), fourop.initdelay(), fourop.initefeds()

    if vce[14] == 2:  #XMOD
        vcd[52] = 3   #ALG 4
    else:
        vcd[52] = 4   #ALG 5

    if vce[9] > 1:
        vcd[53] = 7   #FBL
    else:
        vcd[53] = 0

    vcd[59] = (2, 0, 1, 3)[vce[67]] #LFW
    if vcd[59] == 3: #S/H
        lfspeed = lfsh[vce[68]]
    else:
        lfspeed = lfs[vce[68]]
    vcd[54] = dxcommon.closeto(lfspeed, fourop.lfs, True) #Frequency | LFS
    vcd[55] = fourop.lfd(lfdtime[vce[69]])  #Delay Time | LFD
    vcd[56] = math.ceil(int(650 * vce[70] / 63) / 10) #Pitch Intensity | PMD
    #Timbre/Ampl. Intensity | AMD
    vcd[57] = dxcommon.closeto(amd[vce[71]], fourop.amd, True)
    vcd[58] = 0 #SYNC
    vcd[60] = 7 #PMS
    vcd[61] = 3 #AMS
    vcd[62] = (12,24,36,24)[vce[66]] #TRPS
    vcd[63] = vce[53] #MONO
    if vce[72] < 2:
        vcd[64] = vce[72]
    else:
        vcd[64] = vce[72]-1 #PBR
    if vce[53] == 1:
        vcd[65] = vce[47] #PORMOD
        vcd[66] = int(round(63*vce[48]/99.)) #PORT

    vcd[71] = vce[74] * 33 #MW PITCH ?
    # vcd[72] = #MW AMPL
    
    for k in range(10):
        vcd[k+77] = vce[k+56] + 32 #VOICE NAME
    
    '''
    vcd[87] = min(99, 2 * int(round(1.57 * (63 - vce[4])))) #PR1
    vcd[88] = min(99, 2 * int(round(1.57 * (63 - vce[6])))) #PR2
    vcd[89] = min(99, 2 * int(round(1.57 * (63 - vce[7])))) #PR3
    vcd[90] = 25 + int(round(vce[5]/2.52))    #PL1 attacklevel
    vcd[91] = 50 #PL2 sustainlevel releaselevel
    if abs(vce[3] - vce[8]) < 3:
        ptch = 0.5 * (vce[3] + vce[8])
        vcd[92] = 25 + int(round(ptch / 2.52)) #PL3
    else:
        vcd[92] = 50
    '''
 
    # OP1 carrier OSC2 amp 
    n = 39
    vcd[n] = 31 - vce[41]   #AR = ATK
    vcd[n+1] = 31 - vce[42] #D1R = DEC
    vcd[n+2] = 0            #D2R
    vcd[n+3] = 15 - vce[44] #RR = REL
    vcd[n+4] = vce[43]      #D1L = SUS
    # vcd[n+5] = #LS
    vcd[n+6] = vce[48]      #RS
    vcd[n+7] = 2 * vce[80] #EBS
    vcd[n+8] = vce[46]>>1 #AME
    vcd[n+9] = vce[52] #KVS
    if vce[39] > 0:
        vcd[n+10] = min(99, int(round(48 + 29*math.log(vce[39], 10)))) #OUT
        vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[52], True))
    else:
        vcd[n+10] = 0
    vcd[n+11] = fb01.freq_fb01_dx21[4*vce[1]] #MUL (IH=0)
    vcd[n+12] = 3 - vce[2] #DET
    if vce[14] == 14:
        vcd[n+12] = 3 - vce[2]//2

    # OP2 modulator OSC2 timbre
    n = 13
    ATK = int(round(vce[29] * vce[27] / 15.))
    vcd[n] = 31 - ATK  #AR = ATK
    DEC = int(round(vce[30] * vce[27] / 15.))
    vcd[n+1] = 31 - DEC #D1R = DEC
    vcd[n+2] = 0            #D2R
    REL = int(round(vce[32] * vce[27] / 15.))
    vcd[n+3] = 15 - REL  #RR = REL
    SUS = int(round((15-vce[31]) * vce[27]/15.))
    vcd[n+4] = 15 - SUS      #D1L = SUS
    #LS timbre
    if vce[18] < 1:
        vcd[n+5] = 18 #LS
    elif vce[18] > 1:
        acd2[8] = 4
        vcd[n+5] = (16, 34)[vce[18]-2]
    else:
        vcd[n+5] = 0
    vcd[n+6] = vce[28] #RS = KBD
    vcd[n+7] = 2 * vce[79] #EBS
    vcd[n+8] = vce[45]>>1 #AME
    vcd[n+9] = vce[50] #KVS
    vcd[n+10] = min(99, vce[26] + TIMADJUST2) #OUT
    vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[50], False))
    vcd[n+11] = ratio(vce[1], vce[14], vce[15], vce[16], True) #OSC2, TYPE, SPCT, RING 
    vcd[n+12] = 3 - vce[2] #DET
    if vce[14] == 2:
        vcd[n+12] == 3 - vce[2]//2

    # OP3 carrier OSC1 amp
    n=26
    vcd[n] = 31 - vce[35]   #AR = ATK
    vcd[n+1] = 31 - vce[36] #D1R = DEC
    vcd[n+2] = 0            #D2R
    vcd[n+3] = 15 - vce[38] #RR = REL
    vcd[n+4] = vce[37]      #D1L = SUS
    #vcd[n+5] = #LS
    vcd[n+6] = vce[34] #RS
    vcd[n+7] = 2 * vce[79] #EBS
    vcd[n+8] = vce[46]&1 #AME
    vcd[n+9] = vce[51] #KVS

    if vce[33] > 0:
        vcd[n+10] = int(round(29 * math.log(vce[33], 10) + 48)) #OUT
        if vce[14] == 2:
            vcd[n+10] = vcd[n+10] + 2
        vcd[n+10] = min(99, vcd[n+10])
        vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[51], True))
    else:
        vcd[n+10] = 0

    vcd[n+11] = fb01.freq_fb01_dx21[vce[0]*4] #MUL
    vcd[n+12] = 3 + vce[2] #DET

    # OP4 modulator OSC1 timbre
    n=0
    ATK = int(round(vce[22] * vce[20] / 15.))
    vcd[0] = 31 - ATK  #AR = ATK
    DEC = int(round(vce[23] * vce[20] / 15.))
    vcd[1] = 31 - DEC #D1R = DEC
    vcd[2] = 0            #D2R
    REL = int(round(vce[25] * vce[20] / 15.))
    vcd[3] = 15 - REL  #RR = REL
    SUS = int(round((15-vce[24]) * vce[20]/15.))
    vcd[4] = 15 - SUS      #D1L = SUS
    #LS timbre
    if vce[13] < 1:
        vcd[5] = 18
    elif vce[13] > 1:
        acd2[8] += 1
        vcd[5] = (16, 32)[vce[13]-2]
    else:
        vcd[5] = 0
 
    vcd[n+6] = vce[21] #RS = KBD
    vcd[n+7] = 2 * vce[78] #EBS
    vcd[n+8] = vce[45]&1 #AME
    vcd[n+9] = vce[49] #KVS
    vcd[n+10] = min(99, vce[19] + TIMADJUST1) #OUT
    vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[49], False))
    vcd[n+11] = ratio(vce[0], vce[9], vce[10], vce[11]) #OSC1, TYPE, SPCT, RING 
    vcd[n+12] = 3 + vce[2] #DET
    
    acd2[0] = int(round(99*vce[77]/3.)) #AT PITCH
    # acd2[1] = #AT AMPL
    # acd2[2] = #AT P.BIAS
    acd2[3] = 99 #AT EG BIAS
    
    vmm = fourop.vcd2vmm(vcd, acd, acd2, acd3, efeds, delay)
    return vmm


def vce2vmm_ds8(vce):
    #AMPADJUST1= #?
    TIMADJUST1=6 #?
    #AMPADJUST2= #?
    TIMADJUST2=6 #?

    vcd, acd, acd2, acd3, delay, efeds = fourop.initvcd(), fourop.initacd(), fourop.initacd2(), fourop.initacd3(), fourop.initdelay(), fourop.initefeds()

    if vce[14] == 2:
        vcd[52] = 3   #ALG 4
    else:
        vcd[52] = 4   #ALG 5

    if vce[9] > 1:
        vcd[53] = 7   #FBL
    else:
        vcd[53] = 0

    vcd[59] = (2, 0, 1, 3)[vce[66]] #LFW
    if vcd[59] == 3: #S/H
        lfspeed = lfsh[vce[67]]
    else:
        lfspeed = lfs[vce[67]]
    vcd[54] = dxcommon.closeto(lfspeed, fourop.lfs, True) #Frequency | LFS
    vcd[55] = fourop.lfd(lfdtime[vce[68]])  #Delay Time | LFD
    vcd[56] = math.ceil(int(650 * vce[69] / 63) / 10) #Pitch Intensity | PMD
    #Timbre/Ampl. Intensity | AMD
    vcd[57] = dxcommon.closeto(amd[vce[70]], fourop.amd, True)
    vcd[58] = 0 #SYNC
    vcd[60] = 7 #PMS
    vcd[61] = 3 #AMS
    vcd[62] = 24 #TRPS
    vcd[63] = vce[53] #MONO
    vcd[64] = vce[77] #PBR
    if vce[53] == 1:
        vcd[65] = vce[47] #PORMOD
        vcd[66] = int(round(63*vce[48]/99.)) #PORT

    if vce[76] > 0: #Effect Level
        acd3[2] = 100
        acd3[3] = 0
        if abs(vce[73]-15) > 2:
            acd3[0] = efeds[0] = 6 #Delay
        else:
            efeds[0] = 4 # Echo
        acd3[1] = efeds[2] = int(round(vce[76] * 3.33)) #Balance
        acd3[4] = efeds[1] = delaytime_ds_v50(vce[72])  #Time
        acd3[6] = int(round(99*abs(vce[73]-15)/15.)) #Feedback
        
        if vce[71] == 0: #Manual delay
            # Long Delay (105-720ms, FB=0-15)
            if vce[72] > 70:
                delay[0] = 1
                delay[1] = 1
            # Short Delay (20-88ms, FB=0-15)
            else:
                delay[0] = 1
                delay[1] = 0
            # Doubler (10-40ms, FB=0)
            # Flanger (0.12 - 5.5ms, FB=-15+15 + MFRQ=0~24)
            # Chorus (5-32ms + mfrq=15~29)
            if vce[75] > 2:
                vcd[70] = 1 #DX21 Chorus

        if vce[71] == 1: #Long Delay
            delay[0] = 1 #DS55
            delay[1] = 1

        if vce[71] in (2, 3): #Short Delay 
            delay[0] = 1 #DS55
            delay[1] = 0

        if vce[71] in (4, 5): #Chorus, Flanger
            vcd[70] = 1 #DX21 Chorus

#    vcd[71] = MW PITCH
#    vcd[72] = MW AMPLI
    
    for k in range(10):
        vcd[k+77] = vce[k+56] + 32 #VOICE NAME
    
    '''
    vcd[87] = min(99, 2 * int(round(1.57 * (63 - vce[4])))) #PR1
    vcd[88] = min(99, 2 * int(round(1.57 * (63 - vce[6])))) #PR2
    vcd[89] = min(99, 2 * int(round(1.57 * (63 - vce[7])))) #PR3
    vcd[90] = 25 + int(round(vce[5]/2.52))    #PL1 attacklevel
    vcd[91] = 50 #PL2 sustainlevel releaselevel
    if abs(vce[3] - vce[8]) < 3:
        ptch = 0.5 * (vce[3] + vce[8])
        vcd[92] = 25 + int(round(ptch / 2.52))
    else:
        vcd[92] = 50
    '''

    # OP1 carrier OSC2 amp 
    n = 39
    vcd[n] = 31 - vce[40]   #AR = ATK
    vcd[n+1] = 31 - vce[41] #D1R = DEC
    vcd[n+2] = 0            #D2R
    vcd[n+3] = 15 - vce[43] #RR = REL
    vcd[n+4] = vce[42]      #D1L = SUS
    # vcd[n+5] = #LS
    vcd[n+6] = vce[44]      #RS
    vcd[n+7] = 2 * vce[83] #EBS
    vcd[n+8] = vce[46]>>1 #AME
    vcd[n+9] = vce[52] #KVS
    if vce[39] > 0:
        vcd[n+10] = min(99, int(round(48 + 29*math.log(vce[39], 10)))) #OUT
        vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[52], True))
    else:
        vcd[n+10] = 0
    vcd[n+11] = fb01.freq_fb01_dx21[4*vce[1]] #MUL (IH=0)
    vcd[n+12] = 3 + vce[2] #DET

    # OP2 modulator OSC2 timbre
    n = 13
    ATK = int(round(vce[28] * vce[27] / 15.))
    vcd[n] = 31 - ATK  #AR = ATK
    DEC = int(round(vce[29] * vce[27] / 15.))
    vcd[n+1] = 31 - DEC #D1R = DEC
    vcd[n+2] = 0            #D2R
    REL = int(round(vce[31] * vce[27] / 15.))
    vcd[n+3] = 15 - REL  #RR = REL
    SUS = int(round((15-vce[30]) * vce[27]/15.))
    vcd[n+4] = 15 - SUS      #D1L = SUS
    #LS timbre
    if vce[18] < 1:
        vcd[n+5] = 18
    elif vce[18] > 1:
        acd2[8] += 1
        vcd[n+5] = (16, 32)[vce[18]-2]
    else:
        vcd[n+5] = 0
 
    vcd[n+6] = vce[32] #RS = KBD
    vcd[n+7] = 2 * vce[81] #EBS
    vcd[n+8] = vce[45]>>1 #AME
    vcd[n+9] = vce[50] #KVS
    vcd[n+10] = min(99, vce[26] + TIMADJUST2) #OUT
    vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[50], False))
    vcd[n+11] = ratio(vce[1], vce[14], vce[15], vce[16], True) #OSC2, TYPE, SPCT, RING, WFRM2 
    vcd[n+12] = 3 + vce[2] #DET

    # OP3 carrier OSC1 amp
    n=26
    vcd[n] = 31 - vce[34]   #AR = ATK
    vcd[n+1] = 31 - vce[35] #D1R = DEC
    vcd[n+2] = 0            #D2R
    vcd[n+3] = 15 - vce[37] #RR = REL
    vcd[n+4] = vce[36]      #D1L = SUS
    #vcd[n+5] = #LS
    vcd[n+6] = vce[38] #RS
    vcd[n+7] = 2 * vce[82] #EBS
    vcd[n+8] = vce[46]&1 #AME
    vcd[n+9] = vce[51] #KVS
    if vce[33] > 0:
        vcd[n+10] = 29 * math.log(vce[33], 10) + 48 #OUT
        vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[51], True))
        if vce[14] == 2:
            vcd[n+10] = vcd[n+10] + 2
        vcd[n+10] = min(99, int(round(vcd[n+10])))
    else:
        vcd[n+10] = 0
    vcd[n+11] = fb01.freq_fb01_dx21[vce[0]*4] #MUL
    vcd[n+12] = 3 - vce[2] #DET

    # OP4 modulator OSC1 timbre
    n=0
    ATK = int(round(vce[21] * vce[20] / 15.))
    vcd[0] = 31 - ATK  #AR = ATK
    DEC = int(round(vce[22] * vce[20] / 15.))
    vcd[1] = 31 - DEC #D1R = DEC
    vcd[2] = 0            #D2R
    REL = int(round(vce[24] * vce[20] / 15.))
    vcd[3] = 15 - REL  #RR = REL
    SUS = int(round((15-vce[23]) * vce[20]/15.))
    vcd[4] = 15 - SUS      #D1L = SUS
    #LS timbre
    if vce[13] < 1:
        vcd[5] = 18
    elif vce[13] > 1:
        acd2[8] += 1
        vcd[5] = (16, 32)[vce[13]-2]
    else:
        vcd[5] = 0
 
    vcd[n+6] = vce[25] #RS = KBD
    vcd[7] = 2 * vce[81] #EBS
    vcd[8] = vce[45]&1 #AME
    vcd[9] = vce[49] #KVS
    vcd[10] = min(99, vce[19] + TIMADJUST1) #OUT
    vcd[n+10] = max(0, vcd[n+10] - kvs_adjust(vce[49], False))
    vcd[11] = ratio(vce[0], vce[9], vce[10], vce[11]) #OSC1, TYPE, SPCT, RING 
    vcd[n+12] = 3 - vce[2] #DET
    
    acd2[0] = int(round(99*vce[80]/3.)) #AT PITCH
    #acd2[1] = #AT AMPL
    #acd2[2] = #AT P.BIAS
    acd2[3] = 99 #AT EG BIAS
    
    vmm = fourop.vcd2vmm(vcd, acd, acd2, acd3, efeds, delay)
    return vmm

def vcename(vce):
    s = ''
    for k in range(10):
        s += chr(vce[k+56] + 32) 
    #VOICE NAME
    return s

def vce2vmem(vce, ds8):
    vmm = vce2vmm(vce, ds8)
    vmem = fourop.vmm2vmem(vmm)[0]
    amem = fourop.vmm2vmem(vmm)[1]

    # FB + OSCSYNC
    vmem[111] += 8

    # LEVEL SCALING
    # BP = 27 (C2)
    vmem[8] = 27
    vmem[8+17] = 27
    vmem[8+34] = 27
    vmem[8+51] = 27
    
    #OP6 OSC1 timbre
    KBD = vce[13]
    vmem[9] = (14, 0, 8, 22)[KBD] #LD
    vmem[10] = (9, 0, 8, 17)[KBD] #RD
    LC = (3, 3, 0, 0)[KBD]
    RC = (0, 0, 3, 3)[KBD]
    vmem[11] = 4*RC + LC
 
    #OP5 OSC1 amp
    if vce[33] > 0:
        vmem[31] = 48 + 29*math.log(vce[33], 10) #OUTPUT LEVEL
        if vce[14] == 2:
            vmem[31] += 2
        vmem[31] = int(round(min(99, vmem[31])))
        vmem[31] = max(0, vmem[31] - kvs_adjust(vce[51], True))
    else:
        vmem[31] = 0
    outB = vmem[31]

    #OP4 OSC2 timbre
    KBD = vce[18]
    vmem[9+34] = (14, 0, 8, 22)[KBD] #LD
    vmem[10+34] = (9, 0, 8, 17)[KBD] #RD
    LC = (3, 3, 0, 0)[KBD]
    RC = (0, 0, 3, 3)[KBD]
    vmem[11+34] = 4*RC + LC

    #OP3 OSC2 amp
    if vce[39] > 0:
        vmem[65] = min(99, int(round(48 + 29*math.log(vce[39], 10)))) #OUTPUT LEVEL
        vmem[65] = max(0, vmem[65] - kvs_adjust(vce[52], True))
    else:
        vmem[14+51] = 0

    #LFO DS8|707
    if ds8:
        lfoadr = 66
    else:
        lfoadr = 67
    vmem[112] = dxcommon.closeto(lfs[vce[lfoadr+1]], dx7.lfs, True)  #Frequency | LFS
    vmem[113] = dx7.lfd(lfdtime[vce[lfoadr+2]]) #Delay Time | LFD
    vmem[114] = math.ceil(int(650 * vce[lfoadr+3] /63) / 10) #Pitch Intensity | PMD
    if vce[lfoadr + 4] == 0:
        vmem[115] = 0
    else:
        vmem[115] = int(round(46 * math.log(vce[lfoadr+4], 10))) #Timbre/Ampl Intensity | AMD
    return vmem, amem

def bnk2vmem(bnk, ds8):
    vce = bnk2vce(bnk, ds8)
    vmem, amem = vce2vmem(vce, ds8)
    return vmem, amem


