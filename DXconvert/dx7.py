from . import dxcommon
from math import log

try:
    range = xrange
except NameError:
    pass

lfs = (0.0625, 0.1248, 0.3115, 0.4354, 0.6198,
        0.7444, 0.9305, 1.1164, 1.2842, 1.4969,
        1.5678, 1.7390, 1.9102, 2.0813, 2.2525,
        2.4237, 2.5807, 2.7377, 2.8947, 3.0517,
        3.2087, 3.3668, 3.5249, 3.6830, 3.8411,
        3.9991, 4.1594, 4.3197, 4.4800, 4.6403,
        4.8005, 4.9536, 5.1066, 5.2597, 5.4127,
        5.5658, 5.7249, 5.8841, 6.0432, 6.2024,
        6.3616, 6.5200, 6.6785, 6.8370, 6.9955,
        7.1540, 7.3005, 7.4470, 7.5935, 7.7399,
        7.8864, 8.0206, 8.1548, 8.2889, 8.4231,
        8.5573, 8.7126, 8.8680, 9.0234, 9.1787,
        9.3341, 9.6696,10.0052, 10.3408, 10.6763,
        11.0119, 11.9637, 12.9155, 13.8672, 14.8190,
        15.7708, 16.6402, 17.5097, 18.3791, 19.2486,
        20.1180, 21.0407, 21.9634, 22.8861, 23.8088,
        24.7315, 25.7597, 26.7880, 27.8162, 28.8445,
        29.8727, 31.2282, 32.5837, 33.9392, 35.2947,
        36.6502, 37.8125, 38.9748, 40.1370, 41.2993,
        42.4616, 43.6398, 44.8180, 45.9962, 47.1744,
        47.1744, 47.1744, 47.1744, 47.1744, 47.1744,
        47.1744, 47.1744, 47.1744, 47.1744, 47.1744,
        47.1744, 47.1744, 47.1744, 47.1744, 47.1744,
        47.1744, 47.1744, 47.1744, 47.1744, 47.1744,
        47.1744, 47.1744, 47.1744, 47.1744, 47.1744,
        47.1744, 47.1744, 47.1744)

amd_dexed = (0.00, 0.10, 0.10, 0.20, 0.20, 0.30, 0.35, 0.40, 0.50, 0.60, 
    0.60, 0.70, 0.80, 0.90, 1.00, 1.00, 1.10, 1.20, 1.40, 1.40, 
    1.60, 1.70, 1.80, 2.00, 2.10, 2.20, 2.40, 2.50, 2.70, 2.90, 
    3.10, 3.20, 3.50, 3.70, 3.90, 4.10, 4.30, 4.60, 4.80, 5.10, 
    5.40, 5.70, 6.00, 6.30, 6.70, 7.10, 7.40, 7.80, 8.20, 8.70, 
    9.00, 9.50, 10.10, 10.50, 11.10, 11.60, 12.30, 12.70, 13.50, 14.30, 
    14.80, 15.60, 16.20, 17.20, 18.20, 18.80, 19.90, 20.70, 21.80, 22.60, 
    23.90, 25.30, 26.20, 27.70, 28.70, 30.30, 31.40, 33.10, 34.90, 36.20, 
    38.20, 39.60, 41.75, 43.30, 45.70, 48.30, 49.80, 52.40, 54.50, 57.60, 
    59.80, 62.40, 66.40, 66.60, 74.40, 74.40, 74.40, 74.40, 74.40, 75.00) 

amd_tx7 = (0.00, 0.02, 0.03, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60,
    0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 1.60,
    1.70, 1.90, 2.00, 2.10, 2.20, 2.40, 2.50, 2.60, 2.70, 2.80,
    2.90, 3.00, 3.10, 3.20, 3.30, 3.50, 3.80, 3.90, 4.00, 4.20,
    4.30, 4.50, 4.60, 4.70, 4.90, 5.15, 5.20, 5.30, 5.40, 5.60,
    5.80, 6.00, 6.20, 6.40, 6.50, 6.70, 6.90, 7.10, 7.30, 7.70,
    7.90, 8.10, 8.20, 8.40, 8.80, 9.00, 9.20, 9.40, 9.80, 9.90,
    10.30, 10.70, 10.90, 11.20, 11.40, 12.00, 12.20, 12.60, 13.10, 13.30,
    13.80, 14.30, 14.80, 15.10, 15.70, 16.40, 16.80, 17.50, 18.10, 19.10,
    20.10, 20.80, 21.90, 22.90, 24.40, 25.70, 27.90, 31.10, 33.90, 41.40)

#amd = amd_dexed
amd = amd_tx7

def lfdtime(lfd):
    if lfd == 0:
        return 0
    step = 1.0448752
    start = 0.0346823
    return step**lfd * start

def lfd(t):
    if t == 0:
        return 0
    step = 1.0448752
    start = 0.0346823
    return int(round(max(0, min(99, log(t/start, step)))))

def initvced():
    return [99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 
            99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 
            99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 
            99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 
            99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 
            99, 99, 99, 99, 99, 99, 99, 00, 39, 0, 0, 0, 0, 0, 0, 0, 99, 0, 1, 0, 7, 
            99, 99, 99, 99, 50, 50, 50, 50, 0, 0, 1, 35, 0, 0, 0, 1, 0, 3, 24, 
            73, 78, 73, 84, 32, 86, 79, 73, 67, 69] # 'INIT VOICE'

def initvmem():
    return [99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0, 0, 56, 0, 0, 2, 
            0, 99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0, 0, 56, 0, 0, 
            2, 0, 99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0, 0, 56, 0, 
            0, 2, 0, 99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0, 0, 56, 
            0, 0, 2, 0, 99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0, 0,
            56, 0, 0, 2, 0, 99, 99, 99, 99, 99, 99, 99, 0, 39, 0, 0,
            0, 56, 0, 99, 2, 0, 99, 99, 99, 99, 50, 50, 50, 50, 0, 8, 
            35, 0, 0, 0, 49, 24, 73, 78, 73, 84, 32, 86, 79, 73, 67, 69]

def initaced():
    return [0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 50, 0,
            0, 0, 50, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0]

def initamem():
    return [0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 50, 0, 0, 0, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def vced2vmem(vced):
    if vced == [vced[0]]*155:
        return initvmem()
    vmem = [0]*128
    vced = cleanvced(vced)
    for op in range(6):
        for p in range(11):
            vmem[p+17*op] = vced[p+21*op] 
        vmem[11+17*op] = (vced[12+21*op]<<2) + vced[11+21*op] 
        vmem[12+17*op] = (vced[20+21*op]<<3) + vced[13+21*op] 
        vmem[13+17*op] = (vced[15+21*op]<<2) + vced[14+21*op]
        vmem[14+17*op] = vced[16+21*op]
        vmem[15+17*op] = (vced[18+21*op]<<1) + vced[17+21*op] 
        vmem[16+17*op] = vced[19+21*op]

    for p in range(102, 111):
        vmem[p] = vced[p+24]
    vmem[111] = vced[135] + (vced[136]<<3)
    for p in range(112, 116):
        vmem[p] = vced[p+25]
    vmem[116] = vced[141] + (vced[142]<<1) + (vced[143]<<4)
    for i in range(117, 128):
        vmem[i] = vced[i+27]
    for i in range(len(vmem)):
        vmem[i] = vmem[i]&127
    return vmem

def vmem2vced(vmem):
    if vmem == [vmem[0]] * 128:
        return initvced()

    vced=[0]*155
    for op in range(6):
        for p in range(11):
            vced[p+21*op] = vmem[p+17*op]&127
        vced[11+21*op] = vmem[11+17*op]&0b11
        vced[12+21*op] = (vmem[11+17*op]&0b1100)>>2
        vced[13+21*op] = vmem[12+17*op]&0b111
        vced[20+21*op] = (vmem[12+17*op]&0b1111000)>>3
        vced[14+21*op] = vmem[13+17*op]&0b11
        vced[15+21*op] = (vmem[13+17*op]&0b11100)>>2
        vced[16+21*op] = vmem[14+17*op]&127
        vced[17+21*op] = vmem[15+17*op]&1
        vced[18+21*op] = (vmem[15+17*op]&0b111110)>>1
        vced[19+21*op] = vmem[16+17*op]&127
    for p in range(102, 110):
        vced[p+24] = vmem[p]&127
    vced[134] = vmem[110]&0b11111
    vced[135] = vmem[111]&0b0111
    vced[136] = (vmem[111]&0b1000)>>3
    for p in range(112, 116):
        vced[p+25] = vmem[p]&127
    vced[141] = vmem[116]&1
    vced[142] = (vmem[116]&0b1110)>>1
    vced[143] = (vmem[116]&0b1110000)>>4
    for p in range(117, 128):
        vced[p+27] = vmem[p]
    for i in range(len(vced)):
        vced[i] = vced[i]&127
    return vced

def aced2amem(aced):
    amem = [0]*35
    amem[0] = aced[0] + (aced[1]<<1) + (aced[2]<<2) + (aced[3]<<3) + (aced[4]<<4) + (aced[5]<<5)
    amem[1] = (aced[7]<<3) + aced[6]
    amem[2] = (aced[9]<<3) + aced[8]
    amem[3] = (aced[11]<<3) + aced[10]
    amem[4] = aced[12] + (aced[13]<<2) + (aced[14]<<3) + (aced[19]<<4)
    amem[5] = (aced[16]<<2) + aced[15]
    amem[6] = (aced[18]<<4) + aced[17]
    amem[7] = (aced[21]<<1) + aced[20]
    for p in range(8, 25):
        amem[p] = aced[p+14]
    for p in range(26, 34):
        amem[p] = aced[p+13]
    amem[34] = (aced[48]<<3) + aced[47]
    for i in range(len(amem)):
        amem[i] = amem[i]&127
    return amem

def amem2aced(amem):
    aced = [0]*49
    aced[0] = amem[0]&1
    aced[1] = (amem[0]&2)>>1
    aced[2] = (amem[0]&4)>>2
    aced[3] = (amem[0]&8)>>3
    aced[4] = (amem[0]&16)>>4
    aced[5] = (amem[0]&32)>>5
    aced[6] = amem[1]&0b111
    aced[7] = (amem[1]&0b111000)>>3
    aced[8] = amem[2]&0b111
    aced[9] = (amem[2]&0b111000)>>3
    aced[10] = amem[3]&0b111
    aced[11] = (amem[3]&0b111000)>>3
    aced[12] = amem[4]&0b11
    aced[13] = (amem[4]&0b100)>>2
    aced[14] = (amem[4]&0b1000)>>3
    aced[19] = (amem[4]&0b1110000)>>4
    aced[15] = amem[5]&0b11 
    aced[16] = (amem[5]&0b111100)>>2
    aced[17] = amem[6]&0b1111
    aced[18] = (amem[6]&0b110000)>>4
    aced[20] = amem[7]&1
    aced[21] = (amem[7]&0b11110)>>1
    for p in range(8, 24):
        aced[p+14] = amem[p]
    aced[38] = amem[24]&0b111
    for p in range(26, 34):
        aced[p+13] = amem[p]
    aced[47] = amem[34]&0b111
    aced[48] = (amem[34]&0b1000)>>3
    for i in range(len(aced)):
        aced[i] = aced[i]&127
    return aced

def cleanvced(vced):
    if vced == [vced[0]]*155:
        return initvced()

    #VOICE NAME
    for i in range(145, 155):
        if vced[i] not in range(32,128):
            vced[i] = 32
    if vced[145:155] == 10*[32]:
        return initvced()

    maxvced=[]
    for i in range(6):
        maxvced=maxvced+[100]*11+[4, 4, 8, 4, 8, 128, 2, 32, 100, 15]
    maxvced=maxvced+[100]*8+[32, 8, 2, 100, 100, 100, 100, 2, 6, 8, 128]+[128]*10
 
    for op in range(6):
        #BP
        if vced[8+21*op] > 99:
            if vced[8+21*op] == 127:
                vced[8+21*op] = 0
            else:
                vced[8+21*op] = 198-vced[8+21*op]
        #FF
        if vced[19+21*op] > 99:
            vced[19+21*op] = 0

    #PEGR
    for i in (126, 127, 128, 129):
        vced[i] = min(99, vced[i])
    
    #PEGL
    for i in (130, 131, 132, 133):
        if vced[i] > 99:
            vced[i] = 50

    for i in range(145):
        vced[i] = vced[i] % maxvced[i]

    return vced

def cleanvmem(vmem):
    vced = vmem2vced(vmem)
    vced = cleanvced(vced)
    return vced2vmem(vced)

def cleanaced(aced):
    if aced==[0]*49:
        aced = initaced()
    else:
        maxaced=[99]*49
        for i in [0, 1, 2, 3, 4, 5, 13, 14, 20, 48]:
            maxaced[i] = 1
        for i in [12, 15]:
            maxaced[i] = 3
        for i in [6, 7, 8, 9, 10, 11, 19, 38, 47]:
            maxaced[i] = 7
        for i in [16, 17]:
            maxaced[i] = 12
        maxaced[33] = 100
        for i in range(49):
            aced[i] = min(aced[i], maxaced[i])&127
    return aced

def cleanamem(amem):
    aced=amem2aced(amem)
    aced=cleanaced(aced)
    return aced2amem(aced)

def checksum(data):
    return (128-sum(data)&127)%128

def voicename(vmem):
    voicename = ''
    for i in range(118, 128):
        voicename += chr(vmem[i])
    return voicename

def sign(val):
    if val >= 0:
        return '+' + str(val)
    else:
        return str(val)

def dx7_freq(coarse, fine):
    f = max(0.5, float(coarse))
    f += f * fine / 100.0
    return round(f, 3)

def fix_dx7(crs, fine):
    a = 9.772 ** (1/99.0)
    f = a ** fine
    f = (10 ** (crs%4)) * f
    return round(f, 3) #+ 0.0001

def fr(pc, pf, pm):
    if pm == 0:
        fr = dx7_freq(pc, pf)
    else:
        fr = fix_dx7(pc, pf)
    return fr

def vmem2txt(vmem):
    pname = ['R1', 'R2', 'R3', 'R4', 'L1', 'L2', 'L3', 'L4', 
            'BP', 'LD', 'RD', 'LC', 'RC', 'RS', 'AMS', 'TS', 'TL', 'PM', 'PC', 'PF', 'PD']*6
    pname += ['PR1', 'PR2', 'PR3', 'PR4', 'PL1', 'PL2', 'PL3', 'PL4', 
            'ALS', 'FBL', 'OPI', 'LFS', 'LFD', 'LPMD', 'LAMD', 'LFKS', 'LFW', 'LPMS', 'TRNP', 
            'VNAM1', 'VNAM2', 'VNAM3', 'VNAM4', 'VNAM5', 'VNAM6', 'VNAM7', 'VNAM8', 'VNAM9', 'VNAM10']
    
    v = vmem2vced(vmem)
    t =  'VOICENAME   :      "{}"\n'.format(voicename(vmem))
    t += '========================================================================\n'
    t += 'VCED param. :      OP1       OP2       OP3       OP4       OP5       OP6\n'
    curve = ('-LIN', '-EXP', '+EXP', '+LIN')
    pm = ('Ratio', 'Fixed')

    for i in range(21):
        if pname[i] == 'PD':
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i], sign(v[i+5*21]-7),
                    sign(v[i+4*21]-7),
                    sign(v[i+3*21]-7),
                    sign(v[i+2*21]-7),
                    sign(v[i+21]-7),
                    sign(v[i]-7)) 
        elif pname[i] == 'BP':
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i],
                    dxcommon.nr2note(v[i+5*21], 39), dxcommon.nr2note(v[i+4*21], 39), 
                    dxcommon.nr2note(v[i+3*21], 39), dxcommon.nr2note(v[i+2*21], 39), 
                    dxcommon.nr2note(v[i+21], 39), dxcommon.nr2note(v[i], 39))
        elif pname[i] in ('LC', 'RC'):
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i],
                    curve[v[i+5*21]], curve[v[i+4*21]], curve[v[i+3*21]], curve[v[i+2*21]], curve[v[i+21]], curve[v[i]]) 
        elif pname[i] == 'PM':
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i],
                    pm[v[i+5*21]], pm[v[i+4*21]], pm[v[i+3*21]], pm[v[i+2*21]], pm[v[i+21]], pm[v[i]]) 

        elif pname[i] == 'PF':
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i],
                    v[i+5*21], v[i+4*21], v[i+3*21], v[i+2*21], v[i+21], v[i]) 
            t += "Frequency   : {:8}  {:8}  {:8}  {:8}  {:8}  {:8}\n".format(fr(v[i+104], v[i+105], v[i+103]),
                    fr(v[i+83], v[i+84], v[i+82]), 
                    fr(v[i+62], v[i+63], v[i+61]), 
                    fr(v[i+41], v[i+42], v[i+40]), 
                    fr(v[i+20], v[i+21], v[i+19]), 
                    fr(v[i-1], v[i], v[i-2])) 
        else:
            t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i],
                    v[i+5*21], v[i+4*21], v[i+3*21], v[i+2*21], v[i+21], v[i]) 

    t += '\n'
    for i in range(126, 145):
        if pname[i] == 'ALS':
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], v[i]+1)
        elif pname[i] in ('OPI', 'LFKS'):
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], ('OFF', 'ON')[v[i]])
        elif pname[i] == 'TRNP':
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], sign(v[i] - 24))
        elif pname[i] == 'LFW':
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], ('Triangle', 'Saw Down', 'Saw Up', 'Square', 'Sine', 'S/Hold')[v[i]])
        else:
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], v[i])
    
    t += '\n'
    k = []
    for i in t:
        k.append(ord(i))
    return k


def amem2txt(amem):
    pname = ['SCM']*6 + ['AMS']*6 
    pname += ['PEGR', 'LTRG', 'VPSW', 'PMOD', 
            'PBR', 'PBS', 'PBM', 'RNDP', 
            'PORM', 'PQNT', 'POS', 
            'MWPM', 'MWAM', 'MWEB', 
            'FC1PM', 'FC1AM', 'FC1EB', 'FC1VL', 
            'BCPM', 'BCAM', 'BCEB', 'BCPB', 
            'ATPM', 'ATAM', 'ATEB', 'ATPB', 
            'PGRS', 
            'FC2PM', 'FC2AM', 'FC2EB', 'FC2VL', 
            'MCPM', 'MCAM', 'MCEB', 'MCVL', 
            'UDTN', 'FCCS1']

    a=amem2aced(amem)
    t = 'ACED param. :      OP1       OP2       OP3       OP4       OP5       OP6\n'
    for i in (0, 6):
        t += "{:<3}: {:<7}: {:>8}  {:>8}  {:>8}  {:>8}  {:>8}  {:>8}\n".format(i, pname[i], a[i+5], a[i+4], a[i+3], a[i+2], a[i+1], a[i])
    for i in range(12, 49):
        if pname[i] == 'PEGR':
            pegr = ('8va', '4va', '1va', '1/2va')
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], pegr[a[i]])
        elif pname[i] == 'LTRG':
            ltrg = ('Single', 'Multi')
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], ltrg[a[i]])
        elif pname[i] in ('VPSW', 'FCCS1'):
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], ('Off', 'On')[a[i]])
        elif pname[i] == 'PMOD':
            pmod = ('Polyphonic',
                    'Monophonic',
                    'Unison Poly',
                    'Unison Mono')
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], pmod[a[i]])
        elif pname[i] == 'PBM':
            pbm = ('Normal', 'Low', 'High', 'Key On')
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], pbm[a[i]])
        elif pname[i] == 'PORM':
            porm = ('Retain / Fingered', 'Follow / Fulltime')
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], porm[a[i]])
        elif pname[i] in ('BCPB', 'ATPB'):
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], sign(a[i] - 50))
        else:
            t += "{:<3}: {:<7}: {:>8}\n".format(i, pname[i], a[i])

    t += '\n'
    k = []
    for i in t:
        k.append(ord(i))
    return k

def carrier(alg, op):
    op+=1
    alg+=1
    if op == 1:
        return True
    if op == 2:
        if alg in (20, 21, 23, 24, 25, 26, 27, 29, 30, 31, 32):
            return True
    if op == 3:
        if alg in (1, 2, 5, 6, 7, 8, 9, 12, 13, 14, 15, 22, 24, 25, 28, 29, 30, 31, 32):
            return True
    if op == 4:
        if alg in (3, 4, 10, 11, 19, 20, 21, 22, 23, 24, 25, 26, 27, 31, 32):
            return True
    if op == 5:
        if alg in (5, 6, 19, 21, 22, 23, 24, 25, 29, 31, 32):
            return True
    if op == 6:
        if alg in (28, 30, 32):
            return True
    return False

def raw_check(vmem):
    for k in range(118, 128):
        if 32 < vmem[k] < 128:
            return True
        else:
            return False

def dx7todx9(vmem, n):
    if n > 20:
        return 20*[0x2e]
    dx9name = []
    #VOICENAME
    for i in range(1,32):
        s = "DX9.{:>2}    ".format(n)
    for k in range(10):
        vmem[k+118] = ord(s[k])
    return vmem

