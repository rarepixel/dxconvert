import sys
from . import fourop
from . import fb01
from . import dx7
from . import dx9
from . import korg
from . import dxcommon
from math import log
try:
    range = xrange
except NameError:
    pass

#OUT level
out_rdx_dx7 = [10, 11, 11, 13, 15, 17, 18, 20, 22, 24, 25, 27, 29, 31, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 52, 53, 53, 54, 54, 55, 55, 56, 56, 57, 57, 58, 58, 59, 59, 60, 60, 61, 61, 62, 62, 63, 63, 64, 64, 65, 65, 66, 66, 67, 67, 68, 68, 69, 69, 70, 70, 71, 71, 72, 72, 73, 73, 74, 74, 75, 75, 76, 76, 77, 77, 78, 78, 79, 79, 80, 80, 81, 81, 82, 82, 83, 83, 84, 99, 84, 85, 85, 86, 86, 87, 87, 88, 88, 89, 89, 90, 90, 91, 91, 92, 92, 93, 93, 94, 94, 95, 95, 96, 96, 97, 97, 98, 98, 99]

out_dx7_rdx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 4, 4, 5, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 127]

out_rdx_4op = (
        0, 0, 0, 5, 11, 13, 15, 17, 20, 21, 23, 25, 28, 30, 32, 33, 
        35, 37, 38, 39, 40, 41, 42, 43, 43, 45, 46, 47, 48, 49, 49, 50, 
        51, 52, 52, 53, 53, 54, 54, 55, 55, 56, 56, 57, 57, 58, 58, 59, 
        59, 60, 60, 61, 61, 62, 62, 63, 63, 64, 64, 65, 65, 66, 66, 67, 
        67, 68, 68, 69, 69, 70, 70, 71, 71, 72, 72, 73, 73, 74, 74, 75, 
        75, 76, 76, 77, 77, 78, 78, 79, 79, 80, 80, 81, 81, 82, 82, 83, 
        83, 84, 84, 85, 85, 86, 86, 87, 87, 88, 88, 89, 90, 90, 91, 91, 
        92, 92, 93, 93, 94, 94, 95, 95, 96, 96, 97, 97, 98, 98, 99, 99)

out_4op_rdx = (
        0, 3, 3, 3, 3, 3, 3, 3, 3, 4, 
        4, 4, 5, 5, 6, 7, 7, 7, 8, 8, 
        8, 9, 9, 10, 11, 11, 11, 12, 12, 12, 
        13, 14, 14, 15, 15, 16, 16, 17, 18, 19, 
        20, 21, 22, 24, 24, 25, 26, 27, 28, 29, 
        31, 32, 33, 35, 37, 39, 41, 43, 45, 47, 
        49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 
        69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 
        89, 91, 93, 95, 97, 99, 101, 103, 105, 107, 
        109, 111, 113, 115, 117, 119, 121, 123, 125, 127,
        127, 127, 127, 127, 127, 127, 127, 127)

#LFO Speed
lfs = [0.0263, 0.0421, 0.0841, 0.1262, 0.1682, 0.2103, 0.2524, 0.2944, 
        0.3364, 0.3723, 0.4120, 0.4560, 0.5047, 0.5423, 0.5827, 0.6261, 
        0.6728, 0.7114, 0.7523, 0.7954, 0.8411, 0.8803, 0.9213, 0.9642, 
        1.0091, 1.0488, 1.0901, 1.1330, 1.1776, 1.2175, 1.2588, 1.3014, 
        1.3455, 1.3858, 1.4273, 1.4700, 1.5140, 1.5543, 1.5956, 1.6380, 
        1.6815, 1.7223, 1.7640, 1.8067, 1.8505, 1.8910, 1.9323, 1.9746, 
        2.0178, 2.0587, 2.1006, 2.1432, 2.1867, 2.2274, 2.2689, 2.3111, 
        2.3540, 2.3953, 2.4372, 2.4799, 2.5233, 2.5643, 2.6060, 2.6483, 
        2.6914, 2.7717, 2.8545, 2.9398, 3.0276, 3.1080, 3.1906, 3.2754, 
        3.3625, 3.4441, 3.5277, 3.6133, 3.7010, 3.8585, 4.0228, 4.1940, 
        4.3725, 4.5324, 4.6981, 4.8699, 5.0480, 5.2061, 5.3693, 5.5375, 
        5.7110, 6.0235, 6.3530, 6.7006, 7.0671, 7.3811, 7.7089, 8.0514, 
        8.4090, 8.7273, 9.0575, 9.4003, 9.7561, 10.2908, 10.8548, 11.4498, 
        12.0773, 12.7102, 13.3762, 14.0771, 14.8148, 15.4396, 16.2486, 17.1001, 
        17.4764, 18.5376, 19.6633, 20.8574, 22.1239, 23.3385, 24.6198, 25.9714, 
        27.3973, 28.9017, 30.3030, 31.6456, 33.0033, 34.3643, 37.0370, 39.6825]
lfsh8 = []
for i in lfs:
    lfsh8.append(8*i)
lfs += lfsh8
lfs = tuple(lfs)

amd = (0.00, 0.05, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30,
        0.40, 0.50, 0.60, 0.80, 0.90, 1.00, 1.20, 1.40,
        1.60, 1.80, 2.00, 2.20, 2.40, 2.70, 2.90, 3.20,
        3.50, 3.80, 4.10, 4.40, 4.70, 5.10, 5.40, 5.80,
        6.10, 6.50, 6.90, 7.30, 7.80, 8.20, 8.70, 9.10,
        9.60, 10.10, 10.50, 11.00, 11.50, 12.00, 12.60, 13.10,
        13.70, 14.30, 14.90, 15.50, 16.10, 16.70, 17.30, 18.00,
        18.65, 19.30, 20.00, 20.70, 21.40, 22.10, 22.90, 23.60,
        24.40, 25.10, 25.90, 26.70, 27.50, 28.30, 29.15, 30.00,
        30.85, 31.70, 32.60, 33.50, 34.40, 35.30, 36.20, 37.15,
        38.10, 39.00, 39.95, 41.00, 41.95, 42.90, 44.00, 44.90,
        46.00, 46.90, 48.00, 49.00, 50.10, 51.20, 52.20, 53.10,
        54.30, 55.40, 56.40, 57.60, 58.80, 59.90, 60.90, 61.80,
        63.00, 64.30, 65.20, 66.10, 67.50, 67.80, 69.50, 70.20,
        71.10, 71.30, 72.10, 73.50, 73.70, 74.00, 74.80, 76.00,
        76.12, 76.25, 76.37, 76.50, 76.62, 76.75, 76.87, 77.00)

amd_4op_reface = (0, 0, 0, 0, 0, 6, 6, 6, 6, 14, 
        14, 14, 14, 18, 18, 18, 18, 21, 21, 21,
        24, 24, 24, 27, 27, 27, 29, 29, 29, 31,
        31, 31, 31, 33, 33, 33, 35, 35, 35, 36,
        36, 36, 38, 38, 40, 40, 41, 43, 43, 43, 
        44, 44, 46, 46, 47, 47, 48, 48, 50, 50, 
        51, 51, 52, 53, 53, 54, 55, 55, 57, 58, 
        59, 59, 60, 61, 62, 63, 64, 65, 66, 67, 
        68, 69, 70, 71, 72, 73, 74, 77, 77, 79, 
        81, 82, 84, 85, 88, 89, 92, 92, 95, 95)

def lfdtime(lfd):
    if lfd == 0:
        return 0
    step = 1.03477327
    start = 0.03646005
    return step**lfd * start

def lfd(t):
    if t == 0:
        return 0
    step = 1.03477327
    start = 0.03646005
    return int(round(max(0, min(127, log(t/start, step)))))

#EG
RR = (0, 0, 1, 2, 4, 5, 7, 8, 10, 11,
        13, 15, 16, 18, 19, 21, 22, 24, 26, 27,
        29, 30, 32, 33, 35, 37, 38, 40, 41, 43,
        44, 46, 48, 49, 51, 52, 54, 55, 57, 59,
        60, 62, 63, 65, 66, 68, 70, 71, 73, 74,
        76, 77, 79, 80, 82, 84, 85, 87, 88, 90,
        91, 93, 95, 96, 98, 99, 101, 102, 104, 106,
        107, 109, 110, 112, 113, 115, 117, 118, 120, 121, 
        123, 124, 126, 127, 127, 127, 127, 127, 127, 127, 
        127, 127, 127, 127, 127, 127, 127, 127, 127, 127)

R2 = []
R3 = []
for i in range(32):
    R2.append(RR[fourop.r2[i]])
    R3.append(RR[fourop.r3[i]])
R2 = tuple(R2)
R3 = tuple(R3)
R4 = (0, 21, 31, 40, 50, 60, 69, 79, 88, 98, 107, 117, 126, 127, 127, 127)
R1 = (0, 14, 20, 25, 30, 36, 41, 46, 52, 57, 62, 68, 73, 78, 84, 89,
        95, 100, 105, 111, 116, 121, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127)
'''
R2 = (6, 11, 15, 20, 25, 30, 35, 39, 44, 49, 54, 59, 63, 68, 73, 78,
        83, 87, 92, 97, 102, 107, 111, 116, 121, 126, 127, 127, 127, 127, 127, 127)
R3 = (6, 11, 15, 20, 25, 30, 35, 39, 44, 49, 54, 59, 63, 68, 73, 78,
        83, 87, 92, 97, 102, 107, 111, 116, 121, 126, 127, 127, 127, 127, 127, 127)
R4 = (20, 35, 50, 65, 80, 95, 110, 125, 127, 127, 127, 127, 127, 127, 127, 127)
'''        
L1 = 127
L2 = (0, 3, 5, 8, 12, 16, 21, 28, 37, 46, 57, 69, 82, 95, 111, 127)
L3 = 0
L4 = 0

#DX9/DX7 EG
eg_up_dx9_reface = (
        0, 0, 0, 0, 0, 0, 0, 1, 3, 5, 
        6, 7, 9, 10, 12, 14, 15, 17, 19, 20, 
        21, 22, 24, 27, 29, 31, 32, 33, 34, 36, 
        39, 41, 42, 44, 46, 47, 48, 50, 51, 53, 
        54, 56, 58, 59, 60, 61, 63, 65, 67, 69, 
        72, 73, 74, 75, 77, 80, 81, 83, 85, 86, 
        88, 89, 91, 92, 94, 95, 97, 98, 100, 101, 
        102, 104, 106, 108, 110, 113, 113, 114, 115, 117, 
        120, 121, 123, 125, 126, 127, 127, 127, 127, 127, 
        127, 127, 127, 127, 127, 127, 127, 127, 127, 127)

eg_down_dx9_reface = (
        0, 0, 1, 3, 4, 6, 7, 8, 10, 12, 
        14, 15, 16, 17, 19, 21, 22, 24, 25, 26, 
        28, 30, 33, 35, 36, 37, 39, 41, 42, 44, 
        45, 46, 47, 49, 51, 53, 54, 55, 57, 58, 
        60, 61, 63, 64, 65, 67, 69, 73, 74, 75, 
        77, 78, 80, 81, 83, 85, 86, 86, 88, 90, 
        92, 93, 94, 96, 98, 99, 101, 102, 103, 105, 
        106, 109, 112, 113, 114, 116, 117, 119, 120, 122, 
        124, 125, 126, 127, 127, 127, 127, 127, 127, 127, 
        127, 127, 127, 127, 127, 127, 127, 127, 127, 127)


rdx_dtimes = (
        0011.6, 0019.9, 0028.0, 0036.2, 0044.3, 0052.5, 0060.6, 0068.8,
        0077.0, 0085.2, 0093.3, 0101.5, 0109.6, 0117.8, 0125.9, 0134.1,
        0142.3, 0150.4, 0158.6, 0166.7, 0174.9, 0183.0, 0191.2, 0199.3, 
        0207.4, 0215.6, 0223.7, 0231.9, 0240.1, 0248.2, 0256.4, 0264.6,
        0272.8, 0280.9, 0289.0, 0297.2, 0305.3, 0313.5, 0321.6, 0329.7,
        0337.9, 0346.0, 0354.2, 0362.3, 0370.4, 0378.6, 0386.7, 0394.9,
        0403.0, 0411.2, 0419.3, 0427.5, 0435.7, 0443.8, 0452.0, 0460.2,
        0468.3, 0479.4, 0490.5, 0501.6, 0512.7, 0523.7, 0534.8, 0545.9,
        0557.0, 0567.2, 0577.4, 0587.7, 0597.9, 0608.1, 0618.3, 0628.5,
        0638.8, 0648.9, 0659.1, 0669.2, 0679.4, 0689.5, 0699.7, 0709.8,
        0720.0, 0730.3, 0740.6, 0750.9, 0761.3, 0771.6, 0781.9, 0792.2,
        0802.5, 0812.7, 0822.9, 0833.1, 0843.3, 0853.4, 0863.6, 0873.8,
        0884.0, 0894.3, 0904.5, 0914.8, 0925.0, 0935.3, 0945.5, 0955.8,
        0966.0, 0976.3, 0986.5, 0996.8, 1007.0, 1017.3, 1027.5, 1037.8,
        1048.0, 1058.2, 1068.4, 1078.6, 1088.9, 1099.1, 1109.3, 1119.5,
        1129.7, 1139.9, 1150.1, 1160.3, 1170.6, 1180.8, 1191.0, 1201.0)

def rdx_dtime(ms):
    return dxcommon.closeto(ms, rdx_dtimes)

def carrier(alg, op):
    CM = ((1, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0),
            (1, 0, 0, 0), (1, 1, 0, 0), (1, 1, 0, 0), (1, 0, 1, 0),
            (1, 1, 1, 0), (1, 1, 1, 0), (1, 1, 1, 0), (1, 1, 1, 1))
    return bool(CM[alg][op])

#ALGO conversion
#ALG from dx100 to dx7/9
def alg6(alg4, op4):
    alg6 = (0, 13, 7, 6, 4, 21, 30, 31)[alg4]
    if alg4 == 2:
        op6 = (2, 4, 5, 3)[op4]
    else:
        op6 = (2, 3, 4, 5)[op4]
    op6ad = 21*(5-op6)
    return alg6, op6, op6ad

#ALG from dx100 to reface
def alg(alg4, op4):
    alg = (0, 1, 2, 2, 7, 8, 10, 11)[alg4]
    if alg4 == 3:
        op = (0, 3, 1, 2)[op4]
    else:
        op = op4
    opad = 28*op + 38
    return alg, op, opad

#ALG from reface to dx100
#TODO

#ALG from dx7 to reface
#TODO

#ALG from reface to dx9
#TODO

def initrdx():
    #rdx: Reface DX data = 38 bytes common + 4 * 28 bytes operator data = 150 bytes
    return [73, 110, 105, 116, 32, 86, 111, 105, 99, 101,
            0, 0, 64, 0, 0, 66, 0, 0, 64, 0, 0, 64, 64, 64, 64, 64, 64, 64, 64, 0, 64, 64, 0, 64, 64, 0, 0, 0,
            1, 127, 127, 127, 100, 127, 127, 127, 0, 0, 0, 0, 0, 3, 0, 1, 1, 0, 100, 0, 0, 0, 1, 0, 64, 0, 0, 0,
            1, 127, 127, 127, 100, 127, 127, 127, 0, 0, 0, 0, 0, 3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 64, 0, 0, 0,
            1, 127, 127, 127, 100, 127, 127, 127, 0, 0, 0, 0, 0, 3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 64, 0, 0, 0,
            1, 127, 127, 127, 100, 127, 127, 127, 0, 0, 0, 0, 0, 3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 64, 0, 0, 0]

def dx9tordx(vmem):
    vmm = dx9.dx9to4op(vmem)
    rdx = vmm2rdx(vmm)
    vced = dx7.vmem2vced(vmem)
    vcd, acd, acd2, acd3, efeds, delay = fourop.vmm2vcd(vmm)

    #rdx = initrdx()
    #VOICE common
    rdx[0:0x0a] = vced[145:155] #Voice Name ASCII 32~126
    rdx[0x0c] = vced[144] + 40 #Transpose = 0x28~0x58 = -24~+24

    alg4 = vmm[40]&7
    ALG = alg(alg4, 0)[0]
    rdx[0x10] = ALG #Algorithm 0~11 = 1~12

    rdx[0x11] = (1, 3, 2, 4, 0, 6)[vced[142]] #LFO Wave = 0~6 = SIN, TRI, SAW up, SAW down, SQR, S&H8, S&H
    lfspeed = dx7.lfs[vced[137]]
    if rdx[0x11] == 6:
        val = dxcommon.closeto(lfspeed, lfs)
        if val>127:
            rdx[0x11] = 5
            rdx[0x12] = val - 128
        else:
            rdx[0x12] = val
    else:
        val = dxcommon.closeto(lfspeed, lfs[:128])
        rdx[0x12] = min(127, val) #LFO Speed 0~127
    rdx[0x13] = lfd(dx7.lfdtime(vced[138])) #LFO Delay
    #PMD
    pmdepth = (0, 90., 180., 300., 500., 850., 1400., 2400.)[vced[143]] * vced[139] / 99.
    if pmdepth != 0:
        rdx[0x14] = int(round((2 ** log((256./75.) * pmdepth, 4)))) #LFO PMD
    else:
        rdx[0x14] = 0

    #Operator 1-4
    for op4 in range(4):
        ALG, op, opad = alg(alg4, op4) #Reface
        ALG6, op6, op6ad = alg6(alg4, op4) #DX7/9
        op4ad = (39, 13, 26, 0)[op4]
        iscarrier = carrier(ALG, op)

        rdx[0x00 + opad] = 1 #Off, ON

        [dxR1, dxR2, dxR3, dxR4, dxL1, dxL2, dxL3, dxL4]  = vced[op6ad + 0:op6ad + 8]
        if dxL1 > dxL4:
            rdx[0x01 + opad] = eg_up_dx9_reface[dxR1]
        else:
            rdx[0x01 + opad] = eg_down_dx9_reface[dxR1]

        if dxL2 > dxL1:
            rdx[0x02 + opad] = eg_up_dx9_reface[dxR2]
        else:
            rdx[0x02 + opad] = eg_down_dx9_reface[dxR2]
        
        if dxL3 > dxL2:
            rdx[0x03 + opad] = eg_up_dx9_reface[dxR3]
        else:
            rdx[0x03 + opad] = eg_down_dx9_reface[dxR3]
        
        if dxL4 > dxL3:
            rdx[0x04 + opad] = eg_up_dx9_reface[dxR4]
        else:
            rdx[0x04 + opad] = eg_down_dx9_reface[dxR4]
        for i in range(4, 8):
            rdx[0x01 + opad + i] = int(round(127 * vced[op6ad + i] / 99))  #EG L1 L2 L3 L4

        '''
        rdx[0x05 + opad] = int(round(127 * vced[op6ad + 4] / 99.)) #EG L1
        rdx[0x06 + opad] = int(round(127 * vced[op6ad + 5] / 99.)) #EG L2
        rdx[0x07 + opad] = int(round(127 * vced[op6ad + 6] / 99.)) #EG L3
        rdx[0x08 + opad] = int(round(127 * vced[op6ad + 7] / 99.)) #EG L4
        '''
        
        rdx[0x09 + opad] = (0, 43, 85, 127)[vcd[op4ad+6]&3] #Rate Scaling #TODO
        rdx[0x0a + opad] = int(round(127 * vced[op6ad + 9] / 99.))  #LS Left Depth
        rdx[0x0b + opad] = int(round(127 * vced[op6ad + 10] / 99)) #LS Right Depth
        rdx[0x0c + opad] = vced[op6ad + 11] #LC
        rdx[0x0d + opad] = vced[op6ad + 12] #RC
       
        # rdx[0x0e + opad] = amd_4op_reface[vcd[57] * vcd[8 + op4ad]]  #LFO AM depth * AME
        # amdx = dx7.amd[vced[140]]
        # rdx[0x0e + opad] = dxcommon.closeto(amdx, amd, True)
        '''
        if carrier(ALG, op):
            rdx[0x0f + opad] = 1 #LFO PM depth Off/On
        else:
            rdx[0x0f + opad] = 0
        '''
        rdx[0x0f + opad] = 1
        rdx[0x10 + opad] = 0 #PEG Off, On 
        rdx[0x11 + opad] = vced[15 + op6ad] << 4 #KVS
       
        OUT = out_4op_rdx[vcd[op4ad+10]] #OUT
        rdx[0x12 + opad] = OUT

        if op4 == 3: #FEEDBACK operator
            rdx[0x13 + opad] = 8 * vced[135] #? 

        fr = dx7.dx7_freq(vced[op6ad+18], vced[op6ad+19])
        while fr>31.99:
            fr /= 2
        fr_crs = int(fr)
        if fr_crs > 0:
            fr_fine = int(round(100*(fr-fr_crs)))
        else:
            fr_fine = int(round(200*(fr-0.5)))
        rdx[0x16 + opad] = fr_crs #FREQ CRS/FIX 0 ~ 31
        rdx[0x17 + opad] = fr_fine #FREQ FINE 0 ~ 99
        det = vced[20 + op6ad] - 7 
        det = int(round(12*det/7))
        rdx[0x18 + opad] = det + 64 # DETUNE -64~+63 (center=64)
    return cleanrdx(rdx)

def fb2rdx(fb):
    vmm = fb01.fb2vmm(fb)
    rdx = vmm2rdx(vmm)
    rdx[0x11] = (2, 4, 1, 6)[(fb[14]>>5)&3] #LFO Wave = 0~6 = SIN, TRI, SAW up, SAW down, SQR, S&H8, S&H
    if rdx[0x11] == 6:
        lfspeed = fb01.lfsh[fb[8]]
        val = dxcommon.closeto(lfspeed, lfs)
        if val>127:
            rdx[0x11] = 5
            rdx[0x12] = val - 128
        else:
            rdx[0x12] = val
    else:
        lfspeed = fb01.lfs[fb[8]]
        rdx[0x12] = dxcommon.closeto(lfspeed, lfs[:128]) #LFO Speed 0~127
    return cleanrdx(rdx)

def korg2rdx(bnk, ds8=True):
    '''
    Korg DS8 Effects
    vce71: MAN, LD, SD, FL, CH
    vce72: TIME (0.04~850 ms), (105~720), (20.0~88.0), (0.04~5.50), (5.0~32.0)
    vce73: FEEDBACK (0~30=+/-15)
    vce74: FREQ/SPEED (0~31)
    vce75: INT/DEPTH (0~31)
    vcd76: EFFECT LEVEL (0~15)
    '''
    vce = korg.bnk2vce(bnk, ds8)
    vmm = korg.vce2vmm(vce, ds8)
    rdx = vmm2rdx(vmm)
    if ds8:
        rdx[0x1d:0x23] = [0, 50, 50, 0, 50, 50]

        fx = ('MAN', 'LD', 'SD', 'DB', 'FL', 'CH')[vce[71]]
        dstime = korg.dstimes[vce[72]]
        dsfb = abs(vce[73]-15)
        dsspeed = vce[74]
        dsmint = vce[75]
        dsfxlevel = vce[76]

        rdxtime = rdx_dtime(dstime)

        if fx == 'MAN':
            if vce[72] in range(16) and dsmint and dsfb:
                fx = 'FL'
            elif vce[72] in range(13,46) and dsmint:
                fx = 'CH'
            else:
                fx = 'LD'
        if fx in ('LD', 'SD'):
            rdx[0x1d] = 6
            rdx[0x1e] = int(round(127 * (dsfb/15.) * (dsfxlevel/15.)))
            rdx[0x1f] = rdxtime
        elif fx == 'DB':
            rdx[0x1d] = 6
            rdx[0x1e] = 8 * dsfxlevel
            rdx[0x1f] = rdxtime
        elif fx == 'FL':
            rdx[0x1d] = 4
            rdx[0x1e] = 4 * dsmint
            rdx[0x1f] = int(round(127 * dsspeed/31.))
        elif fx == 'CH':
            rdx[0x1d] = 3
            rdx[0x1e] = 4 * dsmint
            rdx[0x1f] = 4 * dsspeed
            
        if rdx[0x11] == 6:
            lfspeed = korg.lfsh[vce[67]]
            val = dxcommon.closeto(lfspeed, lfs)
            if val>127:
                rdx[0x11] = 5
                rdx[0x12] = val - 128
            else:
                rdx[0x12] = val
        else:
            lfspeed = korg.lfs[vce[67]]
            rdx[0x12] = dxcommon.closeto(lfspeed, lfs[:128]) #LFO Speed 0~127


    else: #707
        if rdx[0x11] == 6:
            lfspeed = korg.lfsh[vce[68]]
            val = dxcommon.closeto(lfspeed, lfs)
            if val>127:
                rdx[0x11] = 5
                rdx[0x12] = val - 128
            else:
                rdx[0x12] = val
        else:
            lfspeed = korg.lfs[vce[68]]
            rdx[0x12] = dxcommon.closeto(lfspeed, lfs[:128]) #LFO Speed 0~127
        rdx[0x0c] = (0x40-12, 0x40, 0x40+12)[vce[66]]

    #LEVELSCALING TIMBRE
    # op4( if xmod: 3) / osc1 timbre = vce[13]
    if vce[14] == 2:
        opad = 28*2 + 38
    else:
        opad = 28*3 + 38
    rdx[0x0a + opad] = (24, 0, 14, 28)[vce[13]] #LD
    rdx[0x0b + opad] = (6, 0, 5, 11)[vce[13]] #RD
    if vce[13] > 1:
        rdx[0x0c + opad] = 0 #-LIN
        rdx[0x0d + opad] = 3 #+LIN
    else:
        rdx[0x0c + opad] = 3 #+LIN
        rdx[0x0d + opad] = 0 #-LIN
    #level correction
    correction = (-6, 0, 5, 11)[vce[13]]
    if rdx[0x12 + opad] < 32:
        correction = correction//2
    if rdx[0x12 + opad] < 16:
        correction = correction//2
    if rdx[0x12 + opad] < 4:
        correction = correction//2
    rdx[0x12 + opad] += correction
    rdx[0x12 + opad] = max(0, min(127, rdx[0x12 + opad]))
    
    # op2 (if xmod: 4) / osc2timbre = vce[18]
    if vce[14] == 2:
        opad = 28*3 + 38
    else:
        opad = 28 + 38
    rdx[0x0a + opad] = (24, 0, 14, 28)[vce[18]] #LD
    rdx[0x0b + opad] = (6, 0, 5, 11)[vce[18]] #RD
    if vce[18] > 1:
        rdx[0x0c + opad] = 0 #-LIN
        rdx[0x0d + opad] = 3 #+LIN
    else:
        rdx[0x0c + opad] = 3 #+LIN
        rdx[0x0d + opad] = 0 #-LIN
    #level correction
    correction = (-6, 0, 5, 11)[vce[18]]
    if rdx[0x12 + opad] < 32:
        correction = correction//2
    if rdx[0x12 + opad] < 16:
        correction = correction//2
    if rdx[0x12 + opad] < 4:
        correction = correction//2
    rdx[0x12 + opad] += correction
    rdx[0x12 + opad] = max(0, min(127, rdx[0x12 + opad]))

    return cleanrdx(rdx)

#Reface DX detune (0 .. 127 = -64 ... +63 = *0.978531766 ... *1.021592756 
def rdx2detune(value):
    value = value - 64
    return 1.00033913 ** dt
def detune2rdx(dtfactor):
    rdxdt = 64 + int(round(log(dtfactor, 1.00033913))) 

def vmm2rdx(vmm):
    vmem = fourop.vmm2vmem(vmm)[0]
    vced = dx7.vmem2vced(vmem)
    vmm = fourop.ys_v50(vmm)
    vcd, acd, acd2, acd3, efeds, delay = fourop.vmm2vcd(vmm)

    rdx = initrdx()

    #VOICE common
    rdx[0:0x0a] = vcd[77:87] #Voice Name ASCII 32~126
    rdx[0x0a] = 0 #reserved
    rdx[0x0b] = 0 #reserved
    rdx[0x0c] = vcd[62] + 40 #Transpose = 0x28 0x40 0x58 = -24 00 +24
    rdx[0x0d] = vcd[63] * (vcd[65] + 1)
    #Partmode = POLY, MONO-FULL, MONO-LGATO
    rdx[0x0e] = vcd[66] * 127 // 99 #Portamento = 0~127
    rdx[0x0f] = vcd[64] + 64 #Pitchbend = 0x28~0x58 = -24~+24 = 0~48

    alg4 = vmm[40]&7
    ALG = alg(alg4, 0)[0]
    rdx[0x10] = ALG #Algorithm 0~11 = 1~12

    rdx[0x11] = (2, 4, 1, 6)[vcd[59]] #LFO Wave = 0~6 = SIN, TRI, SAW up, SAW down, SQR, S&H8, S&H
    lfspeed = fourop.lfs[vcd[54]]
    if rdx[0x11] == 6: #S&H
        val = dxcommon.closeto(lfspeed, lfs)
        if val>127:
            rdx[0x11] = 5 #S&H8
            rdx[0x12] = val - 128
        else:
            rdx[0x12] = val
    else:
        rdx[0x12] = dxcommon.closeto(lfspeed, lfs[:128]) #LFO Speed 0~127
    
    rdx[0x13] = lfd(fourop.lfdtime(vcd[55]))  #LFO Delay 0~127
    #PMD
    pmdepth = (0, 9.3, 21.9, 45.7, 96.0, 195.2, 794.4, 1587.8)[vcd[60]] * vcd[56] / 99.
    if pmdepth != 0:
        rdx[0x14] = int(round(2 ** (7 - log(4800./pmdepth, 4)))) #LFO PMD
    else:
        rdx[0x14] = 0
    rdx[0x15] = int(round(vcd[87] * 127 / 99.)) #Pitch EG Rate1 0~127
    rdx[0x16] = int(round(vcd[88] * 127 / 99.)) #Pitch EG Rate2 0~127
    rdx[0x17] = 127 #Pitch EG Rate3 0~127
    rdx[0x18] = int(round( vcd[89] * 127 / 99.)) #Pitch EG Rate 4 0~127

    rdx[0x19] = vcd[90] + 14 #Pitch EG Level1 0x10~0x70 = -48~+48
    rdx[0x1a] = vcd[91] + 14 #Pitch EG Level2 0x10~0x70 = -48~+48
    rdx[0x1b] = vcd[91] + 14 #Pitch EG Level3 0x10~0x70 = -48~+48
    rdx[0x1c] = vcd[92] + 14 #Pitch EG Level4 0x10~0x70 = -48~+48


    #Operator 1-4
    for op4 in range(4):
        ALG, op, opad = alg(alg4, op4) #Reface
        ALG6, op6, op6ad = alg6(alg4, op4) #DX7/9
        op4ad = (39, 13, 26, 0)[op4]
        iscarrier = carrier(ALG, op)

        AR = vcd[op4ad] & 31
        D1R = vcd[op4ad+1] & 31
        D2R = vcd[op4ad+2] & 31
        RR = vcd[op4ad+3] & 15
        D1L = vcd[op4ad+4] & 15

        rdx[0x00 + opad] = 1 #Off, ON
        egshift = (0, 2, 28, 68)[acd[(19, 14, 9, 4)[op4]]&3]
        rateshift = (127-egshift)/127.
        scalingshift = (0,6,12,18)[vcd[op4ad+6]&3]

        rdx[0x01 + opad] = min(127, scalingshift + int(round(rateshift * R1[AR ]))) #EG R1 AR
        rdx[0x02 + opad] = min(127, scalingshift + int(round(rateshift * R2[D1R]))) #EG R2 D1R
        rdx[0x03 + opad] = min(127, scalingshift + int(round(rateshift * R3[D2R]))) #EG R3 D2R
        rdx[0x04 + opad] = min(127, scalingshift + int(round(rateshift * R4[RR ]))) #EG R4 RR

        rdx[0x05 + opad] = 127 #EG L1
        l2 = L2[D1L] 
        rdx[0x06 + opad] = int((l2/127.) * (127-egshift) + egshift) #EG L2
        if D2R == 0:
            rdx[0x07 + opad] = rdx[0x06 + opad] #EG L3 = L2
        else:
            rdx[0x07 + opad] = 0 #EG L3
        rdx[0x08 + opad] = egshift #EG L4
        rdx[0x09 + opad] = (0, 43, 85, 127)[vcd[op4ad+6]&3] #Rate Scaling #TODO
        
        LS = vcd[5 + op4ad] #LEVEL SCALING
        C3shift = int(round(LS/6.25)) 

        #Reface breakpoint = C3, dx100 breakpoint = C0/C1 ?

        rdx[0x0b + opad] = int(round(0.85 * LS)) #LS Right Depth
        rdx[0x0a + opad] = int(round(0.22 * LS)) #LS Left Depth

        #LS Left/Right Curve -LIN, -EXP, +EXP, +LIN
        if (acd2[8]>>(3-op4)) & 1 == 1:
            rdx[0x0d + opad] = 2 #RC +EXP
            rdx[0x0c + opad] = 3 #LC -LIN
            C3shift *= -1
        else:
            rdx[0x0d + opad] = 1 #RC -EXP
            rdx[0x0c + opad] = 3 #LC +LIN
        rdx[0x0e + opad] = dxcommon.closeto(fourop.amd[vcd[57] * vcd[8 + op4ad]], amd)  #LFO AM depth

        '''
        if iscarrier:
            rdx[0x0f + opad] = 1 #LFO PM depth Off/On
        else:
            rdx[0x0f + opad] = 0
        '''
        rdx[0x0f + opad] = 1
        rdx[0x10 + opad] = 1 #PEG Off, On 
        kvs = vcd[9 + op4ad]
        if kvs > 7: #V50 negative KVS
            kvs = 0
        rdx[0x11 + opad] = (0, 37, 45, 53, 61, 69, 77, 86)[kvs] #KVS
        #rdx[0x11 + opad] = (0, 45, 54, 62, 69, 78, 86, 94)[kvs] #KVS
        
        #rdx[0x12 + opad] = out_4op_rdx[vcd[op4ad+10]] #OUT
        if iscarrier or vcd[op4ad+10] == 0:
            rdx[0x12 + opad] = out_4op_rdx[vcd[op4ad+10]] #OUT
            # kvslimit=(0,1,2,3,4,5,6,7,0,0,0,0,0,0,0,0)
            # rdx[0x12 + opad] = rdx[0x12 + opad] - kvslimit[kvs]
        else:
            rdx[0x12 + opad] = out_4op_rdx[vcd[op4ad+10] + 8]
            # kvslimit=(0,2,4,6,8,10,12,14,0,0,0,0,0,0,0,0)
            # rdx[0x12 + opad] = rdx[0x12 + opad] - kvslimit[kvs]
        rdx[0x12 + opad] = max(0, min(127, rdx[0x12 + opad] - C3shift))

        if op4 == 3: #FEEDBACK operator
            # rdx[0x13 + opad] = (0, 2,  3,  5, 9, 15, 26, 52)[vcd[53]]
            rdx[0x13 + opad] = (0, 1,  2,  4, 8, 16, 32, 64)[vcd[53]]
            # reduce FB level depending on operator OUT level ???
            rdx[0x13 + opad] = int(round(rdx[0x13 + opad] * rdx[0x12+opad] / 127))
            ## reduce FB level depending on EG sustain level L2 ???
            #rdx[0x13 + opad] = int(round(rdx[0x13 + opad] * rdx[0x06+opad] / 127))

        OSW = acd[(18, 13, 8, 3)[op4]]

        if OSW in (1, 6, 7):
            rdx[0x14 + opad] = 1
        else:
            rdx[0x14 + opad] = 0 #FEEDBACK TYPE
        rdx[0x13 + opad] = min(127, rdx[0x13 + opad] + (0, 16, 32, 32, 64, 64, 80, 80)[OSW])

        rdx[0x15 + opad] = acd[(15,5,10,0)[op4]] #FMODE
        if rdx[0x15 + opad] == 0:
            fr = float(fourop.vmm2freq(vmm, op4)[:-1])
            while fr>31.99:
                fr /= 2
            fr_crs = int(fr)
            if fr_crs > 0:
                fr_fine = int(round(100*(fr-fr_crs)))
            else:
                fr_fine = int(round(200*(fr-0.5)))
            rdx[0x16 + opad] = fr_crs #vced[op6ad+18] #FREQ CRS/FIX 0 ~ 31
            rdx[0x17 + opad] = fr_fine #vced[op6ad+19] #FREQ FINE 0 ~ 99
        else: #FIXED
            fr = float(fourop.vmm2freq(vmm, op4)[:-1]) + 0.00001
            dd = 40000
            CRS, FINE = 1, 0
            for crs in range(32):
                for fine in range(100):
                    fre = freq(crs, fine, 1)
                    d = max(fre, fr)/min(fre, fr)
                    if d < dd:
                        dd = d
                        CRS, FINE = crs, fine
                    if dd == 1:
                        break
                if dd == 1:
                    break
            crs, fine = CRS, FINE
            rdx[0x16 + opad] = crs
            rdx[0x17 + opad] = fine
        det = int(1.5 * (vcd[12 + op4ad] - 3))
        rdx[0x18 + opad] = det + 64 # DETUNE -64~+63 (center=64)
        rdx[0x19 + opad] = 0 #reserved
        

    if (ALG, rdx[0x12+38], rdx[0x12+38+28]) == (7, 0, 0): #PSS480 2-op FM
        rdx[38:38+28] = rdx[38+2*28:38+3*28]
        rdx[38+28:38+2*28] = rdx[38+3*28:38+4*28]

    '''
    RefaceFX = 0=THRU, 1=DIST, 2=TWAH, 3=CHO, 4=FLA, 5=PHA, 6=DLY, 7=REV
    '''
    if acd3[3] == 1: #STEREO MIX ON
        fxlevel = int(round(acd3[2]*acd3[1]/100))
    else:
        fxlevel = int(round(acd3[2]*acd3[1]/50))
    fxlevel = min(127, int(round(127*fxlevel/100)))
    # fxlevel = min(127, 2 * 127 * acd3[1] // 100)
    rdx[0x1d:0x23] = [0, fxlevel, 50, 0, fxlevel, 50]

    if acd3[0] == 0: #OFF
        rdx[0x1d] = 0
        rdx[0x20] = 0
    elif acd3[0] in (1, 2, 3, 16, 17, 18, 19, 20): #HALL
        #revtime = fourop.reverbtime[acd3[4]]
        rdx[0x20] = 7
        rdx[0x21] = fxlevel
        rdx[0x22] = min(127, 4*acd3[4])  #int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] == 4: #DELAY
        delaytime = fourop.delaytime[acd3[4]]
        rdx[0x20] = 6
        rdx[0x21] = int(round(fxlevel * acd3[6] / 99.))
        rdx[0x22] = rdx_dtime(delaytime)  #TIME
    elif acd3[0] == 5: #DELAY L/R
        delaytime = fourop.delaytime[acd3[4]]
        rdx[0x20] = 6
        rdx[0x21] = int(round(fxlevel * acd3[6] / 99.))
        rdx[0x22] = rdx_dtime(delaytime)  #TIME
    elif acd3[0] == 6: #STEREO ECHO
        delaytime = fourop.delaytime[acd3[4]]
        rdx[0x20] = 6
        rdx[0x21] = int(round(fxlevel * acd3[6] / 99.))
        rdx[0x22] = rdx_dtime(delaytime)  #TIME
    elif acd3[0] == 7: #DISTORTION REVERB
        #revtime = fourop.reverbtime[acd3[4]]
        rdx[0x1d] = 1
        rdx[0x1e] = int(round(127*acd3[5]/100))
        rdx[0x20] = 7
        rdx[0x21] = int(round(fxlevel * acd3[6]/100))
        rdx[0x22] = min(127, 4*acd3[4]) #int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] in (8, 15): #DISTORTION ECHO
        delaytime = fourop.delaytime[acd3[4]]
        rdx[0x1d] = 1
        rdx[0x1e] = int(round(127*acd3[6]/100))
        rdx[0x20] = 6
        rdx[0x21] = int(round(fxlevel * acd3[5]/100))
        rdx[0x22] = rdx_dtime(delaytime)  #TIME
    elif acd3[0] in (9, 10, 11): #GATE REVERB
        #revtime = fourop.reverbtime[acd3[6]] #???todo
        rdx[0x20] = 7
        rdx[0x21] = int(round(fxlevel * acd3[4]/100))
        rdx[0x22] = min(127, 4*acd3[6]) #int(round(127*acd3[6]/75)) #TIME
        #elif acd3[0] == 12: #TONE CONTROL 1
        #    pass
    elif acd3[0] == 13: #DELAY & REVERB
        #revtime = fourop.reverbtime[acd3[4]]
        delaytime = fourop.delaytime[acd3[5]]
        rdx[0x1d] = 6
        rdx[0x1e] = int(round(fxlevel * acd3[6]))
        rdx[0x1f] = rdx_dtime(delaytime)  #TIME
        rdx[0x20] = 7
        rdx[0x21] = int(round(fxlevel * acd3[6]))
        rdx[0x22] = min(127, 4 *acd3[4])  #int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] == 14: #DELAY L/R & REVERB
        #revtime = fourop.reverbtime[acd3[4]]
        delaytime = fourop.delaytime[max(acd3[5], acd3[6])]
        rdx[0x1d] = 6
        rdx[0x1e] = fxlevel
        rdx[0x1f] = rdx_dtime(delaytime) 
        rdx[0x20] = 7
        rdx[0x21] = fxlevel
        rdx[0x22] = min(127, 4*acd3[4])  #int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] == 21: #TUNNEL
        #revtime = fourop.reverbtime[acd3[4]]
        delaytime = fourop.delaytime[acd3[5]]
        rdx[0x1d] = 6
        rdx[0x1e] = fxlevel
        rdx[0x1f] = rdx_dtime(delaytime)
        rdx[0x20] = 7
        rdx[0x21] = int(round(fxlevel * acd3[6]))
        rdx[0x22] = min(127, 4*acd3[4]) # int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] == 22: #DOUBLER 1
        doublertime = fourop.doublertime[acd[4]]
        rdx[0x1d] = 6
        rdx[0x21] = fxlevel
        rdx[0x1f] = rdx_dtime(doublertime) #TIME
    elif acd3[0] == 23: #DOUBLER 2
        doublertime = fourop.doublertime[max(acd3[4], acd3[5])] 
        rdx[0x1d] = 6
        rdx[0x1e] = fxlevel
        rdx[0x1f] = rdx_dtime(doublertime) #TIME
    elif acd3[0] in (24, 25, 26): #FEED BACK GATE
        rdx[0x20] = 7
        rdx[0x21] = int(round(fxlevel * acd3[4]/100))
        rdx[0x22] = min(127, 4*acd3[4])   #int(round(127*acd3[4]/75)) #TIME
    elif acd3[0] in (27, 28, 30, 31): #DELAY & TONE1
        delaytime = fourop.delaytime[acd3[4]]
        rdx[0x20] = 6
        rdx[0x21] = int(round(fxlevel * acd3[6]))
        rdx[0x22] = rdx_dtime(delaytime)  #TIME
        #elif acd3[0] == 29: #TONE CONTROL 2
        #pass
    elif acd3[0] == 32: #DISTORTION
        rdx[0x1d] = 1
        rdx[0x1d] = int(round(fxlevel * acd3[4])/100.)
        rdx[0x1e] = int(round(127 * acd3[6] / 99.))
    if vcd[70] == 1: #DX21 chorus:
        if rdx[0x1d] == 0:
            rdx[0x1d:0x20] = [3, 90, 0]
        elif rdx[0x20] == 0:
            rdx[0x20:0x23] = [3, 90, 0]
    
    #set INIT values if effect = Off
    if rdx[0x1d] == 0:
        rdx[0x1e:0x20] = [64, 64]
    if rdx[0x20] == 0:
        rdx[0x21:0x23] = [64, 64]
    return cleanrdx(rdx)

def rdx2vmm(rdx, yamaha):
    vcd = fourop.initvcd()
    acd = fourop.initacd()
    acd2 = fourop.initacd2()
    acd3 = fourop.initacd3()
    efeds = fourop.initefeds()
    
    #TODO convert rdx to vcd/acd
    #COMMON
    vcd[52] = (0, 1, 2, 2, 2, 4, 4, 4, 5, 5, 6, 7)[rdx[0x10]] #ALG
    alg4 = vcd[52]
    vcd[53] = min(7, rdx[38 + 28*3 + 0x13] // 8) #FBL
    if rdx[0x11] < 5:
        lfspeed = lfs[rdx[0x12]]
        vcd[54] = dxcommon.closeto(lfspeed, fourop.lfs, True) #LFS
    elif rdx[0x11] == 6: #SH8
        lfspeed = lfs[rdx[0x12]+128]
        vcd[54] = dxcommon.closeto(rdx[0x12] + 128, fourop.lfs, True)   #LFS
    elif rdx[0x11] == 7: #SH
        lfospeed = lfs[rdx[0x12]]
        vcd[54] = dxcommon.closeto(lfspeed, fourop.lfs, True)   #LFS
    vcd[55] = fourop.lfd(lfdtime(rdx[0x13])) #LFD
    if rdx[0x14] == 0:
        pmdepth = 0
    else:
        pmdepth = 4800 * (4 ** (log(rdx[0x14], 2) -7))
    vcd[56] = dxcommon.closeto(pmdepth, (0, 9.3, 21.9, 45.7, 96.0, 195.2, 794.4, 1587.8), True) #0x14 PMD
    amdepth = 0
    for op in range(4):
        amdepth = max(amdepth, rdx[0x0e + 28*op + 38])
    vcd[57] = dxcommon.closeto(amd[amdepth], fourop.amd)
    # vcd[58] = #LFO SYNC
    vcd[59] = (2, 2, 0, 0, 1, 3, 3)[rdx[0x11]] #LFW
    vcd[60] = 99 #PMS
    vcd[61] = 99 #AMS
    vcd[62] = rdx[0x0c] - 0x28 #TRPS 0-24-48
    if rdx[0x0d] != 0:
        vcd[63] = 1 #MONO
    if rdx[0x0d] == 1: #FULL PORTAMENTO
        vcd[65] = 0
    if rdx[0x0d] == 2: #LEGATO PORTAMENTO
        vcd[65] = 1
    vcd[64] = min(12, abs(rdx[0x0f] - 0x40)) #PBR
    vcd[66] = rdx[0x0e] * 99 // 127 #PORTime
    '''
    vcd[67] #FC VOL
    vcd[68] #sus. (F.SW)
    vcd[69] #por.
    '''
    if rdx[0x1d] in (3,4,5) or rdx[0x20] in (3,4,5):
        vcd[70] = 1 #DX21 CHORUS
    '''
    vcd[71] #MW PITCH
    vcd[72] #MW AMPL
    vcd[73] #BC PITCH
    vcd[74] #BC AMPLI
    vcd[75] #BC P.BIAS
    vcd[76] #BC E.BIAS
    '''
    vcd[77:87] = rdx[:10] #VOICENAME
    vcd[87] = rdx[0x15] * 99 // 127 #PR1
    vcd[88] = rdx[0x16] * 99 // 127 #PR2
    vcd[89] = rdx[0x18] * 99 // 127 #PR3
    vcd[90] = rdx[0x19] - 14 #PL1
    vcd[91] = ((rdx[0x1a] + rdx[0x1b])//2) - 14 #PL2
    vcd[92] = rdx[0x1c] - 14 #PL3

    #OP1 2 3 4
    for op in range(4):
        opad = 28*op + 38
        op4ad = (39, 13, 26, 0)[op]
        opa4ad = (15, 5, 10, 0)[op]
        iscarrier = carrier(rdx[10], op)
        
        vcd[op4ad + 5] = 99 * rdx[0x0b + opad] // 127 #LS *TODO*
        vcd[op4ad + 6] = dxcommon.closeto(rdx[0x09 + opad], (0, 43, 85, 127)) #RS
        #vcd[op4ad + 7] = #EBS
        if rdx[0x0e + opad] > 8:
            vcd[8 + op4ad] = 1 #AME
        else:
            vcd[8 + op4ad] = 0
         
        rate1, rate2, rate3, rate4, level1, level2, level3, level4 = rdx[1+opad:9+opad]
        vcd[op4ad + 0] = dxcommon.closeto(rate1, R1) #AR
        vcd[op4ad + 3] = dxcommon.closeto(rate4, R4) #RR
        if level3 == 0:
            if rate2==99 and (level1==level2):
                vcd[op4ad + 1] = dxcommon.closeto(rate3, R3) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = 0 #D1L
            elif (rate2<99) and (level1==level2):
                vcd[op4ad + 1] = dxcommon.closeto(rate2, R2) #D1R
                vcd[op4ad + 2] = dxcommon.closeto(rate3, R3) #D2R
                vcd[op4ad + 4] = 15 #D1L
            elif (level1>level2):
                vcd[op4ad + 1] = dxcommon.closeto(rate2, R2) #D1R
                vcd[op4ad + 2] = dxcommon.closeto(rate3, R3) #D2R
                vcd[op4ad + 4] = dxcommon.closeto(level2, L2) #D1L
            elif (level1<level2):
                vcd[op4ad + 0] = (dxcommon.closeto(rate1, R1) + dxcommon.closeto(rate2, R1)) // 2 #AR
                vcd[op4ad + 1] = dxcommon.closeto(rate3, R2) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = dxcommon.closeto(level2, L2) #D1L
 
        else:
            if (level1>level2):
                vcd[op4ad + 1] = (dxcommon.closeto(rate2, R2)+dxcommon.closeto(rate3, R2))//2 #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = dxcommon.closeto(level2, L2) #D1L
            elif (level1==level2):
                vcd[op4ad + 1] = dxcommon.closeto(rate3, R2) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = dxcommon.closeto(level2, L2) #D1L
            elif (level1<level2):
                vcd[op4ad + 0] = (dxcommon.closeto(rate1, R1)+dxcommon.closeto(rate2, R1))//2 #AR
                vcd[op4ad + 1] = dxcommon.closeto(rate3, R2) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = dxcommon.closeto(level2, L2) #D1L

        vcd[op4ad + 9] = dxcommon.closeto(rdx[0x11+opad], (0, 37, 45, 53, 61, 69, 77, 86)) #KVS #0 ~ 7
        
        #OUTLEVEL
        if iscarrier:
            vcd[op4ad + 10] = out_rdx_4op[rdx[0x12 + opad]]
        else:
            vcd[op4ad + 10] = max(0, out_rdx_4op[rdx[0x12 + opad]] - 8)

        fr = freq(rdx[0x16 + opad], rdx[0x17 + opad], rdx[0x15 + opad])
        if rdx[0x15 + opad] == 0: #RATIO
            freq_4op = dxcommon.closeto(fr, fourop.freq_4op)
            crs4op = freq_4op // 16
            fine4op = freq_4op % 16
            vcd[op4ad + 11] = crs4op
            acd[opa4ad + 2] = fine4op
            acd[opa4ad] = 0
        else: #FIX
            fixd = 100000
            FIXED = 1
            acd[opa4ad] = 1
            v50 = 0
            if yamaha == "v50":
                v50 = 1
            for mode4op in range(1 + v50):
                for rng4op in range(8):
                    for crs4op in range(64):
                        for fine4op in range(16):
                            fix = fourop.fix_4op(mode4op, rng4op, crs4op, fine4op)
                            dfix = abs(fix - fr)
                            if dfix < fixd:
                                fixd = dfix
                                acd2[7 - op] = mode4op
                                acd[1 + opa4ad] = rng4op
                                vcd[11 + op4ad] = crs4op
                                acd[2 + opa4ad] = fine4op
                                FIXED = fix
        det = int(round(min(3, max(-3 , (rdx[opad + 0x18] - 64) / 1.5)))) #DETUNE
        vcd[12 + op4ad] = det + 3
        acd[3 + opa4ad] = rdx[0x13 + opad] // 16 #OSW

    # V50 YS200 Reface FX
    dlytime1, dlytime2, revtime1, revtime2, dist1, dist2 = 0, 0, 0, 0, 0, 0
    if rdx[0x1d] == 6:
        dlytime1 = dxcommon.closeto(rdx_dtimes[rdx[0x1f]], fourop.delaytime)
    if rdx[0x20] == 6:
        dlytime2 = dxcommon.closeto(rdx_dtimes[rdx[0x22]], fourop.delaytime)
    if rdx[0x1d] == 7:
        revtime1 = rdx[0x1f] // 4 #* 75 // 127
    if rdx[0x20] == 7:
        revtime2 = rdx[0x22] // 4 #* 75 // 127
    if rdx[0x1d] == 1:
        dist1 = rdx[0x1e] * 99 // 127
    if rdx[0x20] == 1:
        dist2 = rdx[0x21] * 99 // 127
    
    balance1 = rdx[0x1e] // 2
    balance2 = rdx[0x21] // 2
    if rdx[0x1d] in (0, 2, 3, 4, 5):
        balance1 = 0
    if rdx[0x20] in (0, 2, 3, 4, 5):
        balance2 = 0

    if (rdx[0x1d] in (0, 2, 3, 4, 5)) and (rdx[0x20] in (0, 2, 3, 4, 5)):
        acd3[0] = 0
    elif rdx[0x1d] == rdx[0x20]:
        acd3[0] = (0, 7, 0, 0, 0, 0, 4, 1)[rdx[0x1d]]
    elif rdx[0x1d] in (0, 2, 3, 4, 5):
        acd3[0] = (0, 7, 0, 0, 0, 0, 4, 1)[rdx[0x20]]
        balance1 = 0
    elif rdx[0x20] in (0, 2, 3, 4, 5):
        acd3[0] = (0, 7, 0, 0, 0, 0, 4, 1)[rdx[0x1d]]
        balance2 = 0
    else:
        if (rdx[0x1d] in (1, 6)) and (rdx[0x20] in (1, 6)):
            acd3[0] = 15  #dist + dly
        elif (rdx[0x1d] in (1, 7)) and (rdx[0x20] in (1, 7)):
            acd3[0] = 7 #dist + rev
        elif (rdx[0x1d] in (6, 7)) and (rdx[0x20] in (6, 7)):
            acd3[0] = 13 #dly + rev
    
    if acd3[0] == 1: #REV
        acd3[4] = max(revtime1, revtime2)
    elif acd3[0] == 4: #DELAY
        acd3[4] = max(dlytime1, dlytime2)
    elif acd3[0] == 7: #dist + rev
        acd3[4] == max(revtime1, revtime2)
        acd3[5] = max(dist1, dist2)
    elif acd3[0] == 15: #dist + delay
        acd3[4] = max(dlytime1, dlytime2)
        acd3[6] = max(dist1, dist2) 
    elif acd3[0] == 13: #delay + reverb
        acd3[4] = max(revtime1, revtime2)
        acd3[5] = max(dlytime1, dlytime2)

    acd3[1] = max(balance1, balance2)
    acd3[2] = 100
    acd3[3] = 0
    fxs = ("THRU", "DIST", "TWAH", "CHO", "FLA", "PHA", "DLY", "REV")

    '''
    # RefaceFX: 0=THRU, 1=DIST, 2=TWAH, 3=CHO, 4=FLA, 5=PHA, 6=DLY, 7=REV

    acd3[0] = #FX SELECT 0~32
    acd3[1] = #BALANCE
    acd3[2] = #OUT LEVEL
    acd3[3] = #MIX
    acd3[4] = #PARAM 1
    acd3[5] = #PARAM 2
    acd3[6] = #PARAM 3

    efeds[0] = #FX PRESET 0-10
    efeds[1] = #FX TIME
    efeds[2] = #FX BALANCE
    '''
    vmm = fourop.vcd2vmm(vcd, acd, acd2, acd3, efeds)
    vmm = fourop.v50_ys(vmm)
    return vmm


def rdx2vmem(rdx):
    #vced = dx7.initvced()
    #aced = dx7.initaced()

    #TODO: convert rdx to dx7
    vmm = rdx2vmm(rdx, "v50")
    vmem = fourop.vmm2vmem(vmm)[0]
    amem = fourop.vmm2vmem(vmm)[1]
    vced = dx7.vmem2vced(vmem)

    #aced = dx7.amem2aced(amem)
   
    #LFO
    if rdx[0x11] < 5:
        lfspeed = lfs[rdx[0x12]]
        vced[137] = dxcommon.closeto(lfspeed, dx7.lfs, True) #LFS
    elif rdx[0x11] == 6: #SH8
        lfspeed = lfs[rdx[0x12]+128]
        vced[137] = dxcommon.closeto(rdx[0x12] + 128, dx7.lfs, True)   #LFS
    elif rdx[0x11] == 7: #SH
        lfospeed = lfs[rdx[0x12]]
        vced[137] = dxcommon.closeto(lfspeed, dx7.lfs, True)   #LFS

    #PEG
    for i in range(4):
        vced[126+i] = fourop.pr[99 * rdx[0x15 + i] // 127]
        vced[130+i] = 50 + 99 * (rdx[0x19 + i] - 0x40) // 127 #PEG level

    #ALGO
    alg4 = (0, 1, 2, 2, 2, 4, 4, 4, 5, 5, 6, 7)[rdx[0x10]]
    for op in range(4):
        algo6, op6, op6ad = alg6(alg4, op)
        opad = 28*op + 38

        #if rdx[0x10] in (1,9,5):
        #algo6 = 12,24,27 

        [rdxR1, rdxR2, rdxR3, rdxR4, rdxL1, rdxL2, rdxL3, rdxL4]  = rdx[opad + 1:opad + 9]
        vced[0 + op6ad] = dxcommon.closeto(rdxR1, eg_up_dx9_reface)

        if rdxL2 > rdxL1:
            vced[1 + op6ad] = dxcommon.closeto(rdxR2, eg_up_dx9_reface)
        else:
            vced[1 + op6ad] = dxcommon.closeto(rdxR2, eg_down_dx9_reface)
        
        if rdxL3 > rdxL2:
            vced[2+ op6ad] = dxcommon.closeto(rdxR3, eg_up_dx9_reface)
        else:
            vced[2 + op6ad] = dxcommon.closeto(rdxR3, eg_down_dx9_reface)
        
        if rdxL4 > rdxL3:
            vced[3 + op6ad] = dxcommon.closeto(rdxR4, eg_up_dx9_reface)
        else:
            vced[3 + op6ad] = dxcommon.closeto(rdxR4, eg_down_dx9_reface)

        for i in range(4, 8):
            vced[op6ad + i] = int(round(99 * rdx[opad + i + 1] / 127))  #EG L1 L2 L3 L4
        
        vced[op6ad + 8] = 39 #BP = C3
        vced[op6ad + 9] = int(round(99 * rdx[0x0a + opad] / 127.)) #LS Left Depth
        vced[op6ad + 10] = int(round(99 * rdx[0x0b + opad] / 127.)) #LS Right Depth
        vced[op6ad + 11] = rdx[0x0c + opad] # LC
        vced[op6ad + 12] = rdx[0x0d + opad] # RC
        #vced[op6ad + 13] = #RS

        fr = freq(rdx[0x16 + opad], rdx[0x17 + opad], rdx[0x15 + opad])
        fix = rdx[0x15 + opad] 
        frdif = 40000
        for fc in range(32):
            for ff in range(100):
                fr7 = dx7.fr(fc, ff, fix)
                frd = abs(fr7 - fr)
                if frd < frdif:
                    frdif = frd
                    vced[op6ad + 17] = fix
                    vced[op6ad + 18] = fc
                    vmem[op6ad + 19] = ff
                if frd == 0:
                    break
        det = rdx[0x18 + opad] - 64
        det = min(7, max(-7, int(round(7*det/12))))
        vced[op6ad + 20] = det + 7

    vmem = dx7.vced2vmem(vced)
    #amem = dx7.aced2amem(aced)
    
    return vmem, amem

def rdx2syx(rdx, ch=0, p=0):
    if p==0:
        a=0x0f
    else:
        a=0x00
        p = (p - 1) % 32
    rdxhead = [0xf0, 0x43, ch, 0x7f, 0x1c, 0x00]

    #HEADER
    header = [0x05, 0x0e, a, p]
    syx = rdxhead + [0x04] + header + [dxcommon.checksum(header), 0xf7]
    #COMMON
    comm = [0x05, 0x30, 0x00, 0x00] + rdx[:38]
    syx +=  rdxhead + [0x2a] + comm + [dxcommon.checksum(comm), 0xf7]
    #OPERATORS
    op1 = [0x05, 0x31, 0x00, 0x00] + rdx[38:66]
    syx += rdxhead + [0x20] + op1 + [dxcommon.checksum(op1), 0xf7]
    op2 = [0x05, 0x31, 0x01, 0x00] + rdx[66:94]
    syx +=  rdxhead + [0x20] + op2 + [dxcommon.checksum(op2), 0xf7]
    op3 = [0x05, 0x31, 0x02, 0x00] + rdx[94:122]
    syx += rdxhead + [0x20] + op3 + [dxcommon.checksum(op3), 0xf7]
    op4 = [0x05, 0x31, 0x03, 0x00] + rdx[122:150]
    syx += rdxhead + [0x20] + op4 + [dxcommon.checksum(op4), 0xf7]
    #FOOTER
    footer = [0x05, 0x0f, a, p]
    syx += rdxhead + [0x04] + footer + [dxcommon.checksum(footer), 0xf7]
    return syx

def voicename(rdx):
    return dxcommon.list2string(rdx[:10])

def cleanrdx(rdx):
    if rdx == 150 * [rdx[0]]:
        return initrdx()

    for i in range(10):
        if rdx[i] not in range(32, 128):
            rdx[i] = 32

    for i in range(len(rdx)):
        rdx[i] = rdx[i] & 127

    rdx[0x0d] = min(rdx[0xd] & 3, 2) 
    rdx[0x0f] = max(0x58, min(0x28, rdx[0x0f]))
    rdx[0x10] = min(rdx[0x10] & 15, 11)
    rdx[0x11] = min(rdx[0x11] & 7, 6)
    for i in (0x19, 0x1a, 0x1b, 0x1c):
        rdx[i] = max(0x10, min(0x70, rdx[i]))
    rdx[0x1d] = rdx[0x1d] & 7
    rdx[0x20] = rdx[0x20] & 7
    for op in (38, 38+28, 38+2*28, 38+3*28):
        rdx[op + 0x00] = rdx[op + 0x00] & 1
        rdx[op + 0x0c] = rdx[op + 0x0c] & 3
        rdx[op + 0x0d] = rdx[op + 0x0d] & 3
        rdx[op + 0x0f] = rdx[op + 0x0f] & 1
        rdx[op + 0x10] = rdx[op + 0x10] & 1
        rdx[op + 0x14] = rdx[op + 0x14] & 1
        rdx[op + 0x15] = rdx[op + 0x15] & 1
        rdx[op + 0x16] = rdx[op + 0x16] & 31
        rdx[op + 0x17] = min(rdx[op + 0x17], 0x63) 
    return rdx

def rdx2txt(rdxdata): 
    paramCommon = ("VOICENAME 1", "VOICENAME 2", "VOICENAME 3", "VOICENAME 4", "VOICENAME 5",
            "VOICENAME 6", "VOICENAME 7", "VOICENAME 8", "VOICENAME 9", "VOICENAME 10",
            "reserved", "reserved", "TRANSPOSE", "MONO/POLY", "PORTA TIME", "PB RANGE", "ALGORITHM", 
            "LFO WAVE", "LFO SPEED", "LFO DELAY", "LFO PMD",
            "PEG RATE 1", "PEG RATE 2", "PEG RATE 3", "PEG RATE 4", "PEG LEVEL 1", "PEG LEVEL 2", "PEG LEVEL 3", "PEG LEVEL 4",
            "FX1 TYPE", "FX1 PARAM 1", "FX1 PARAM 2", "FX2 TYPE", "FX2 PARAM 1", "FX2 PARAM 2", "reserved", "reserved", "reserved")
    paramOp = ("OP Off/On", "EG RATE 1", "EG RATE 2", "EG RATE 3", "EG RATE 4", "EG LEVEL 1", "EG LEVEL 2", "EG LEVEL 3", "EG LEVEL 4", 
            "RATE SCALING",
            "SCALING LD", "SCALING RD", "SCALING LC", "SCALING RC",
            "LFO AMD", "LFO PMD Off/On", "PEG Off/On", "VELO SENS", "OUT LEVEL", "FEEDBACK", "FB TYPE",
            "FREQ MODE", "freq coarse", "freq fine  ", "FREQ DETUNE", "reserved", "reserved", "reserved")
    fxTypes = ("Thru", "Distortion", "Touch Wah", "Chorus", "Flanger", "Phaser", "Delay", "Reverb")
    fxP1 = ("---", "Drive", "Sensibility", "Depth", "Depth", "Depth", "Depth", "Depth")
    fxP2 = ("---", "Tone", "Rez", "Rate", "Rate", "Rate", "Time", "Time")
    n = len(rdxdata)//150
    dat = []
    if n == 1:
        s = "VOICE NAME     = {}\n".format(voicename(rdxdata))
        s += "============================\n"
        #for i in range(10):
        #    s += "{:14} = {:>8}\n".format(paramCommon[i], chr(rdxdata[i]))
        for i in range(10, 38):
            pname = paramCommon[i]
            if pname == "reserved":
                pass
            elif pname == "ALGORITHM":
                s += "{:14} = {:>8}\n".format(paramCommon[i], rdxdata[i] + 1)
            elif pname in ("TRANSPOSE", "PB RANGE", "PEG LEVEL 1", "PEG LEVEL 2", "PEG LEVEL 3", "PEG LEVEL 4"):
                s += "{:14} = {:>8}\n".format(paramCommon[i], rdxdata[i]-64)
            elif pname == "MONO/POLY":
                s += "{:14} = {:>8}\n".format(paramCommon[i], ("Poly", "Mono-Full", "Mono-Legato")[rdxdata[i]])
            elif pname == "LFO WAVE":
                s += "{:14} = {:>8}\n".format(paramCommon[i], ("Sine", "Triangle", "Sawtooth Up", "Sawtooth Down", "Square", "Sample & Hold 8", "Sample & Hold")[rdxdata[i]])
            elif pname == "FX1 TYPE" or pname == "FX2 TYPE":
                s += "{:14} = {:>8} ({})\n".format(paramCommon[i], rdxdata[i], fxTypes[rdxdata[i]])
            elif pname == "FX1 PARAM 1" or pname == "FX2 PARAM 1":
                s += "{:14} = {:>8} ({})\n".format(paramCommon[i], rdxdata[i], fxP1[rdxdata[i-1]])
            elif pname == "FX1 PARAM 2" or pname == "FX2 PARAM 2":
                s += "{:14} = {:>8} ({})\n".format(paramCommon[i], rdxdata[i], fxP2[rdxdata[i-2]])
            else:
                s += "{:14} = {:>8}\n".format(paramCommon[i], rdxdata[i])
        s += "\n"
        s += 22*" " + "{:8} {:8} {:8} {:8}\n".format("OP1", "OP2", "OP3", "OP4")
        s += "----------------------------------------------------\n"
        for i in range(28):
            pname = paramOp[i]
            if pname == "reserved":
                pass
            elif pname in ("OP Off/On", "LFO PMD Off/On", "PEG Off/On"):
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], 
                        ("Off", "On")[rdxdata[i+38]], 
                        ("Off", "On")[rdxdata[i+66]], 
                        ("Off", "On")[rdxdata[i+94]], 
                        ("Off", "On")[rdxdata[i+122]])
            elif pname in ("SCALING LC", "SCALING RC"):
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], 
                        ("-LIN", "-EXP", "+EXP", "+LIN")[rdxdata[i+38]], 
                        ("-LIN", "-EXP", "+EXP", "+LIN")[rdxdata[i+66]], 
                        ("-LIN", "-EXP", "+EXP", "+LIN")[rdxdata[i+94]], 
                        ("-LIN", "-EXP", "+EXP", "+LIN")[rdxdata[i+122]])
            elif pname == "FB TYPE":
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], 
                        ("Sawtooth", "Square")[rdxdata[i+38]], 
                        ("Sawtooth", "Square")[rdxdata[i+66]], 
                        ("Sawtooth", "Square")[rdxdata[i+94]], 
                        ("Sawtooth", "Square")[rdxdata[i+122]])
            elif pname == "FREQ MODE":
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], 
                        ("Ratio", "Fixed")[rdxdata[i+38]], 
                        ("Ratio", "Fixed")[rdxdata[i+66]], 
                        ("Ratio", "Fixed")[rdxdata[i+94]], 
                        ("Ratio", "Fixed")[rdxdata[i+122]])
            elif pname == "freq coarse":
                fcrs = "{:>14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], rdxdata[i+38], rdxdata[i+66], rdxdata[i+94], rdxdata[i+122])
            elif pname == "freq fine  ":
                ffine = "{:>14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], rdxdata[i+38], rdxdata[i+66], rdxdata[i+94], rdxdata[i+122])
                f1 = freq(rdxdata[22+38], rdxdata[23+38], rdxdata[21+38])
                f2 = freq(rdxdata[22+66], rdxdata[23+66], rdxdata[21+66])
                f3 = freq(rdxdata[22+94], rdxdata[23+94], rdxdata[21+94])
                f4 = freq(rdxdata[22+122], rdxdata[23+122], rdxdata[21+122])
                ffreq = "RATIO | FREQ   = {:>8} {:>8} {:>8} {:>8}\n".format(f1, f2, f3, f4)
                s += ffreq
                s += fcrs
                s += ffine
            elif pname == "FREQ DETUNE":
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], rdxdata[i+38]-64, rdxdata[i+66]-64, rdxdata[i+94]-64, rdxdata[i+122]-64)
            else:
                s += "{:14} = {:>8} {:>8} {:>8} {:>8}\n".format(paramOp[i], rdxdata[i+38], rdxdata[i+66], rdxdata[i+94], rdxdata[i+122])

    else:
        s = ""
        for i in range(n):
            s += "{}\t{}\n".format(i+1, voicename(rdxdata[150*i:150*(i+1)]))
    dat += dxcommon.string2list(s)
    return dat

def freq(crs, fine, mode=0):
    if mode == 0: #RATIO
        if crs > 0:
            freq = crs + fine/100.
        else: 
            freq = 0.5 + fine/200.
    else: #FIXED
        c = 10 ** min(3, crs>>3)
        #n = 10 ** (1/100)
        n = 9.772 ** (1/99.)
        freq = c * (n ** fine)
    return round(freq, 3)

