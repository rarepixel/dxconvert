from . import dx7
from . import fourop
from . import dxcommon

try:
    range = xrange
except NameError:
    pass

alg4 = (0, 0, 0, 0, 4, 0, 3, 2, 
        0, 0, 0, 0, 0, 1, 0, 0, 
        0, 0, 0, 0, 0, 5, 0, 0, 
        0, 0, 0, 0, 0, 0, 6, 7) 

out4 = (0, 0, 0, 1, 2, 3, 4, 4, 5, 5, 
        6, 7, 8, 9, 10, 11, 12, 12, 13, 14, 
        15, 15, 16, 17, 18, 18, 19, 20, 20, 21, 
        22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
        32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 
        42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 
        52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 
        62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 
        72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 
        82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 
        91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 
        91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 
        91, 91, 91, 91, 91, 91, 91, 91)

def AR(r):
    #R1 = 3*AR + 10
    AR = (r - 10)/3
    return min(31, max(0, int(round(AR))))

def D1R(r):
    #R2 = 3*D1R + 6
    D1R = (r - 6)/3
    return min(31, max(0, int(round(D1R))))

def D2R(r):
    return D1R(r)

def RR(r):
    #R4 = 6*RR + 10
    RR = (r - 10) / 6
    return min(15, max(1, int(round(RR))))

def D1L(l):
    #L2 = 4*D2L + 40
    if l == 0:
        return 0
    else:
        D1L = (l -40) / 4
    return min(15, max(0, int(round(D1L))))

pms_factor = fourop.pms_factor

def freq9to4(crs9, fin9, octavide=True):
    f = fourop.dx7_freq(crs9, fin9)
    if octavide:
        f /= 2
    if f in fourop.freq_4op:
        crs4 = fourop.freq_4op.index(f) // 16
        fin4 = fourop.freq_4op.index(f) % 16
        return crs4, fin4
    
    f0 = 0.5
    d0 = 200
    for n in range(1024):
        f1 = fourop.freq_4op[n]
        d1 = abs(1-f/f1)
        #d1 = abs(f-f1)
        if d1 < d0:
            f0 = f1
            d0 = d1

    crs4 = fourop.freq_4op.index(f0) // 16
    fin4 = fourop.freq_4op.index(f0) % 16
    return crs4, fin4

def dx9to4op(vmem):
    vced = dx7.vmem2vced(vmem)

    vcd = fourop.initvcd()
    acd = fourop.initacd()

    #conversion start
    vcd[52] = alg4[vced[134]] #ALGO
    for op in range(4):
        op9ad = (63, 42, 21, 0)[op]
        if vcd[52] == 2:
            op4ad = (39, 0, 13, 26)[op]
            op4add = (15, 0, 5, 10)[op]
        else:
            op4ad = (39, 13, 26, 0)[op]
            op4add = (15, 5, 10, 0)[op]
        
        rate1, rate2, rate3, rate4, level1, level2, level3, level4 = vced[op9ad:op9ad+8]
        vcd[op4ad + 0] = AR(rate1) #AR
        vcd[op4ad + 3] = RR(rate4) #RR
        if level3 == 0:
            if rate2==99 and (level1==level2):
                vcd[op4ad + 1] = D1R(rate3) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = 0 #D1L
            elif (rate2<99) and (level1==level2):
                vcd[op4ad + 1] = D1R(rate2) #D1R
                vcd[op4ad + 2] = D2R(rate3) #D2R
                vcd[op4ad + 4] = 15 #D1L
            elif (level1>level2):
                vcd[op4ad + 1] = D1R(rate2) #D1R
                vcd[op4ad + 2] = D2R(rate3) #D2R
                vcd[op4ad + 4] = D1L(level2) #D1L
            elif (level1<level2):
                vcd[op4ad + 0] = (AR(rate1)+AR(rate2))//2 #AR
                vcd[op4ad + 1] = D1R(rate3) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = D1L(level2) #D1L
 
        else:
            if (level1>level2):
                vcd[op4ad + 1] = (D1R(rate2)+D1R(rate3))//2 #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = D1L(level2) #D1L
            elif (level1==level2):
                vcd[op4ad + 1] = D1R(rate3) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = D1L(level2) #D1L
            elif (level1<level2):
                vcd[op4ad + 0] = (AR(rate1)+AR(rate2))//2 #AR
                vcd[op4ad + 1] = D1R(rate3) #D1R
                vcd[op4ad + 2] = 0 #D2R
                vcd[op4ad + 4] = D1L(level2) #D1L
 
        if vced[op9ad + 6] == 0:
            vcd[op4ad + 0] = AR(vced[op9ad + 0]) #AR
            vcd[op4ad + 1] = D1R(vced[op9ad + 1]) #D1R
            vcd[op4ad + 2] = D2R(vced[op9ad + 2]) #D2R
            vcd[op4ad + 3] = RR(vced[op9ad + 3]) #RR
            vcd[op4ad + 4] = D1L(vced[op9ad + 5]) #D1L
        else:
            vcd[op4ad + 0] = AR(vced[op9ad + 0]) #AR
            vcd[op4ad + 1] = D1R(vced[op9ad + 1]) #D1R
            vcd[op4ad + 2] = 0 #r3[vced[op9ad + 2]] #D2R
            vcd[op4ad + 3] = RR(vced[op9ad + 3]) #RR
            vcd[op4ad + 4] = D1L(vced[op9ad + 5]) #D1L
        '''
        #LEVEL SCALING
        #vced[8] BP = 15 (C1)
        #vced[9] LD = 0 
        #vced[10] RD = 0 ~ 99 
        #vced[11] LC = 0 (-LIN)
        #vced[12] RC = 1 (-EXP)
        '''
        vcd[op4ad + 5] = vced[op9ad + 10] #LS
        vcd[op4ad + 6] = int(round(vced[op9ad + 13]*0.4))  #RS
        #vcd[op4ad + 7] = EBS
        vcd[op4ad + 8] = vced[op9ad + 14]//2 # if AMS>1: AME=1
        #vcd[op4ad + 9] = KVS
        vcd[op4ad + 10] = out4[vced[op9ad + 16]] #OUT
        octavide = True
        for n in (18+63, 18+42, 18+21, 18+13):
            if vced[n] == 0:  # crs = 0.5
                octavide = False
                break
        CRS, FINE = freq9to4(vced[op9ad + 18], vced[op9ad + 19], octavide)
        vcd[op4ad + 11] = CRS
        vcd[op4ad + 12] = min(6, vced[op9ad + 20] // 2)  #DET

        #acd[op4add + 0] = FIX
        #acd[op4add + 1] = FIXRG
        acd[op4add + 2] = FINE
        #acd[op4add + 3] = EGSFT
    
    vcd[53] = vced[135] #FBL
    lfspeed = dx7.lfs[vced[137]]
    vcd[54] = dxcommon.closeto(lfspeed, fourop.lfs)  #LFS
    lfdtime = dx7.lfdtime(vced[138])
    vcd[55] = fourop.lfd(lfdtime) #LFD
    if vced[143] != 0:
        vcd[56] = min(99, int(round(vced[139] / pms_factor[vced[143]])))  #PMD
    amdepth = dx7.amd[vced[140]]
    vcd[57] = dxcommon.closeto(amdepth, fourop.amd) #AMD
    vcd[58] = vced[136] #SYNC
    vcd[59] = (2, 2, 0, 1, 2, 3, 2, 2)[vced[142]] #LFW tri, tri(sawdown), sawup, sqr, tri(sin), s/h 
    vcd[60] = vced[143] #PMS
    vcd[61] = max(vced[14], vced[35], vced[56], vced[77]) #AMS
    vcd[62] = vced[144] #TRPS
    if octavide and vcd[62]<=36:
        vcd[62] += 12
    #vcd[63] = MONO
    #vcd[64] = PBR
    #vcd[65] = PORMOD
    #vcd[66] = PORT
    # vcd[67] = FCvol
    # vcd[68] = SUSW
    # vcd[69] = reserved
    # vcd[70] = CHOR
    #vcd[71] = MWpitch
    #vcd[72] = MWampli
    #vcd[73] = BCpitch
    #vcd[74] = BCampli
    #vcd[75] = BCpbias
    #vcd[76] = BCebias
    vcd[77:87] = vced[145:155] #VOICENAME
    
    # acd[20] = REV
    # acd[21] = FCpitch
    # acd[22] = FCampli
 
    #acd2[0] = ATpitch
    #acd2[1] = ATampli
    #acd2[2] = ATpbias
    #acd2[3] = ATebias
    # acd2[4] = FIXRM4
    # acd2[5] = FIXRM3
    # acd2[6] = FIXRM2
    # acd2[7] = FIXRM1
    # acd2[8] = LS SiGN
    #acd2[9] = reserved

    #conversion end
    vmm = fourop.vcd2vmm(vcd, acd)
    return vmm

