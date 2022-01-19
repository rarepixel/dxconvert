#!/usr/bin/env python3
import array
import os
import sys
from shutil import copy
from glob import glob
from argparse import ArgumentParser
try:
    range = xrange
except NameError:
    pass
VERSION = '20170419'

'''
#### V50 disk fileformat *.Ixx (SYN) ####
Address data    blocksize   Address_V50SYN_*Cxx
0x00    null    32          0x00
0x20    SYS     27          0x20
0x3b    SYS2    16          0x3b
0x4b    SYS3    32          0x4b
0x6b    null    149

0x100   PC      256         0x100
0x200   MCTOCT  24          0x200
0x218   MCTFULL 256         0x218
0x318   EFG1    55          x
0x34f   EFG2    55          x
0x386   EFG3    55          x
0x3bd   EFG4    55          x
0x3f4   null    12          x

0x400   PMEM    12800 = 100 * 128 (76 bytes PMEM1 + 25 bytes PMEM2 + 27 nullbytes) 
(CARD V50SYN: PMEM starts at 0x700)

0x3600  VMEM    12800 = 100 * 128
(CARD V50SYN: VMEM starts at 0x3900)
=====================
0x6800  26624 bytes

VMEM[86] parameter AT Pitch Bias:
V50 Display  : -50 ... -01, 00, +01 ... +50
MIDI SYSEX   :  51 ... 100, 00, 01 ...  50
V50 DISK     :  00 ...  49, 50, 51 ... 100

#### V50 *.Rxx fileformat (RHY) ####
RHY (*.Rxx) ALL (*.Vxx)    blocksize
0x00
0x20        0x6820  SYSR
0x100       0x6900  RINST
0x200       0x6a00  RKAT1
0x23d       0x6a3d  RKAT2
0x400       0x6c00  RSEQ

'''        

########## CONSTANTS and INIT values ###############

initvmem = (31, 31, 0, 15, 15, 0, 0, 0, 4, 3, 31, 31, 0, 15, 15, 0,
           0, 0, 4, 3, 31, 31, 0, 15, 15, 0, 0, 0, 4, 3, 31, 31, 
           0, 15, 15, 0, 0, 90, 4, 3, 0, 35, 0, 0, 0, 98, 24, 4, 
           4, 0, 40, 50, 0, 0, 0, 50, 0, 73, 78, 73, 84, 32, 86, 79, 
           73, 67, 69, 99, 99, 99, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 0, 50, 
           100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

### INIT PERFORMANCE (modified)
initperf = (96, 0, 32, 0, 127, 7, 24, 99, #1 #PMEM
            96, 1, 64, 0, 127, 7, 24, 99, #2
            96, 2, 96, 0, 127, 7, 24, 99, #3
            96, 3, 96, 0, 127, 7, 24, 99, #4
            96, 4, 96, 0, 127, 7, 24, 99, #5
            96, 5, 96, 0, 127, 7, 24, 99, #6
            96, 6, 96, 0, 127, 7, 24, 99, #7
            96, 7, 96, 0, 127, 7, 24, 99, #8
            2, 0, 
            73, 110, 105, 116, 32, 112, 101, 114, 102, 32, #NAME
            0, 0, 0, 0, 0, 0, 0, 0, #PMEM2
            0, 100, 80, 1, 0, 0, 0, #FX
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0) 

##############################


initsys1 = (0x40, 0x10, 0x00, 0x01, 0x01, 0x01, 0x00, 0x01, 0x01, 0x01, 0x00, 
            0x3e, 0x3e, 0x3e, 0x3e, 0x20, 0x20, 0x20, 0x20, 
            0x20, 0x20, 0x20, 0x4e, 0x69, 0x63, 0x65, 0x20)
initsys2 = (0x01, 0x01, 0x01, 0x07, 0x00, 0x01, 0x01, 0x00,
            0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
initsys3 = (0x74, 0x6F, 0x20, 0x6D, 0x65, 0x65, 0x74, 0x20,
            0x79, 0x6F, 0x75, 0x20, 0x21, 0x21, 0x20, 0x20,
            0x20, 0x20, 0x20, 0x20, 0x3C, 0x3C, 0x3C, 0x3C,
            0x50, 0x00, 0x00, 0x01, 0x0A, 0x00, 0x00, 0x00)

initefg1 = (0x16, 0x18, 0x07, 0x63, 0x02, 0x00, 0x63, 0x1c, 0x1f, 0x21, 
        0x24, 0x1c, 0x1f, 0x22, 0x24, 0x1b, 0x1f, 0x22, 0x24, 0x1b, 
        0x1f, 0x22, 0x24, 0x1b, 0x1d, 0x20, 0x24, 0x1c, 0x1f, 0x21, 
        0x24, 0x1c, 0x1f, 0x21, 0x24, 0x1c, 0x1f, 0x21, 0x24, 0x1c, 
        0x1f, 0x21, 0x24, 0x1b, 0x1d, 0x20, 0x24, 0x1b, 0x1d, 0x20, 
        0x24, 0x1b, 0x1e, 0x20, 0x24)
        
initefg2 = (0x0b, 0x18, 0x07, 0x63, 0x01, 0x00, 0x63, 0x1e, 0x21, 0x24, 
        0x1b, 0x1b, 0x21, 0x24, 0x1e, 0x1e, 0x21, 0x1b, 0x24, 0x1b, 
        0x1e, 0x21, 0x24, 0x1b, 0x1e, 0x21, 0x24, 0x1e, 0x21, 0x1b, 
        0x24, 0x21, 0x1b, 0x24, 0x1e, 0x1e, 0x21, 0x1b, 0x24, 0x21, 
        0x1e, 0x24, 0x1b, 0x21, 0x1e, 0x1b, 0x24, 0x1e, 0x21, 0x24, 
        0x1b, 0x24, 0x1e, 0x1b, 0x21) 
        
initefg3 = (0x06, 0x14, 0x07, 0x63, 0x00, 0x01, 0x49, 0x21, 0x18, 0x1c, 
        0x26, 0x21, 0x18, 0x26, 0x1c, 0x1c, 0x21, 0x26, 0x18, 0x18, 
        0x1c, 0x21, 0x26, 0x18, 0x21, 0x26, 0x1c, 0x18, 0x21, 0x1c, 
        0x26, 0x18, 0x21, 0x26, 0x1c, 0x21, 0x1c, 0x26, 0x18, 0x26, 
        0x21, 0x1c, 0x18, 0x26, 0x21, 0x1c, 0x18, 0x18, 0x26, 0x21, 
        0x1c, 0x26, 0x21, 0x18, 0x1c) 
        
initefg4 = (0x02, 0x1b, 0x07, 0x60, 0x00, 0x01, 0x32, 0x18, 0x22, 0x28, 
        0x2d, 0x18, 0x28, 0x2d, 0x22, 0x28, 0x2d, 0x18, 0x22, 0x2d, 
        0x22, 0x28, 0x18, 0x18, 0x28, 0x2d, 0x22, 0x22, 0x28, 0x18, 
        0x2d, 0x28, 0x2d, 0x22, 0x18, 0x28, 0x18, 0x2d, 0x22, 0x18, 
        0x2d, 0x28, 0x22, 0x2d, 0x18, 0x28, 0x22, 0x2d, 0x22, 0x28, 
        0x18, 0x2d, 0x18, 0x28, 0x22) 

initmctoct = (0x3c, 0x00, 0x3d, 0x00, 0x3e, 0x00, 0x3f, 0x00, 0x40, 0x00, 0x41, 0x00,
        0x42, 0x00, 0x43, 0x00, 0x44, 0x00, 0x45, 0x00, 0x46, 0x00, 0x47, 0x00)

initmctfull = []
for i in range(128):
    k = (i + 12)
    while k<13:
        k += 12
    while k>107:
        k -= 12
    initmctfull += [k, 0]
initmctfull = tuple(initmctfull)

initpc = []
for i in range(100):
    initpc += [0, i]
for i in range(100, 128):
    initpc += [2, i-100]
initpc = tuple(initpc)

initsysr = []
initrinst = []
initrkat1 = []
initrkat2 = []

VMEMHEAD = [0xf0, 0x43, 0x00, 0x04, 0x20, 0x00]
LM = [0x4c, 0x4d, 0x20,  0x20]
PMEM1HEAD = LM__8976PM = LM + [0x38, 0x39, 0x37, 0x36, 0x50, 0x4d]
PMEM2HEAD = LM__8073PM = LM + [0x38, 0x30, 0x37, 0x33, 0x50, 0x4d]
SYS1HEAD = LM__8976S0 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x30]
SYS2HEAD = LM__8023S0 = LM + [0x38, 0x30, 0x32, 0x33, 0x53, 0x30]
SYS3HEAD = LM__8073S0 = LM + [0x38, 0x30, 0x37, 0x33, 0x53, 0x30]
PCHEAD =   LM__8976S1 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x31]
EFG1HEAD = LM__8976S2 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x32]
EFG2HEAD = LM__8976S3 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x33]
EFG3HEAD = LM__8976S4 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x34]
EFG4HEAD = LM__8976S5 = LM + [0x38, 0x39, 0x37, 0x36, 0x53, 0x35]
MCTOCTHEAD = LM__MCRTE0 = LM + [0x4d, 0x43, 0x52, 0x54, 0x45, 0x30]
MCTFULLHEAD = LM__MCRTE1 = LM + [0x4d, 0x43, 0x52, 0x54, 0x45, 0x31]
SYSQHEAD = LM__8073SS = LM + [0x38, 0x30, 0x37, 0x33, 0x53, 0x53]
NSEQHEAD = LM__NSEQ__ = LM + [0x4e, 0x53, 0x45, 0x51, 0x20, 0x20]
SSONGHEAD = LM__8073SQ = LM + [0x38, 0x30, 0x37, 0x33, 0x53, 0x51]
SYSRHEAD = LM__8073RS = LM + [0x38, 0x30, 0x37, 0x33, 0x52, 0x53]
RINSTHEAD = LM__8073RI = LM + [0x38, 0x30, 0x37, 0x33, 0x52, 0x49]
RKAT1HEAD = LM__8073K0 = LM + [0x38, 0x30, 0x37, 0x33, 0x4b, 0x30]
RKAT2HEAD = LM__8073K1 = LM + [0x38, 0x30, 0x37, 0x33, 0x4b, 0x31]
RSEQHEAD = LM__8073RY = LM + [0x38, 0x30, 0x37, 0x33, 0x52, 0x59]

WELCOMEMESSAGE = '>>>>       Nice to meet you !!      <<<<'

############ FUNCTIONS ##########

def initdisk(mode="ixx"):
    '''
    Ixx = SYN
    Vxx = ALL
    Rxx = RHY
    Axx = SEQ
    Bxx = MDF
    Cxx = CRD

    '''
    #SYN
    if mode in ("ixx", "vxx"):
        initdisk = 32 * [0]
        initdisk += list(initsys1)
        initdisk += list(initsys2)
        initdisk += list(initsys3)
        initdisk += 149 * [0]
        initdisk += list(initpc)
        initdisk += list(initmctoct)
        initdisk += list(initmctfull)
        initdisk += list(initefg1)
        initdisk += list(initefg2)
        initdisk += list(initefg3)
        initdisk += list(initefg4)
        initdisk += 12 * [0]
        initdisk += 100 * (list(initperf) + 27*[0])
        initvmeml = list(initvmem)
        initvmeml[86] = 50
        initdisk += 100 * initvmeml
    
    #RHY
    if mode in ("rxx"):
        initdisk = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                #SYSR
                99, 2, 0, 4, 8, 8, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 
                #
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                #RINST
                15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 
                15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 
                15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 2, 4, 5, 
                1, 2, 4, 5, 1, 2, 4, 5, 1, 1, 1, 1, 5, 4, 0, 1, 
                2, 4, 3, 3, 1, 5, 3, 3, 3, 1, 5, 0, 6, 1, 1, 5, 
                2, 4, 3, 3, 2, 4, 3, 3, 3, 3, 45, 44, 39, 36, 37, 38, 
                52, 49, 87, 86, 85, 84, 61, 51, 46, 53, 50, 48, 47, 93, 92, 91, 
                90, 43, 42, 41, 40, 57, 59, 89, 88, 62, 63, 60, 94, 95, 96, 83, 
                80, 82, 76, 54, 56, 55, 70, 69, 78, 77, 66, 65, 64, 68, 67, 72, 
                71, 75, 74, 58, 73, 79, 81, 
                #
                0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                #RKAT1
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
                48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 
                #RKAT2
                3, 4, 5,
                2, 26, 25, 24, 23, 1, 0, 14, 18, 17, 7, 16, 13, 6, 15, 41, 
                43, 42, 27, 57, 28, 33, 12, 31, 32, 50, 49, 48, 52, 51, 45, 44, 
                54, 53, 58, 56, 55, 40, 47, 46, 59, 38, 60, 39, 37, 11, 10, 9, 
                8, 30, 29, 22, 21, 20, 19, 34, 35, 36, 
                #                
                0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 78, 101, 119, 83, 111, 110, 103, 32, 78, 101, 119, 83, 111, 110, 
                103, 32, 78, 101, 119, 83, 111, 110, 103, 32, 78, 101, 119, 83, 111, 110, 
                103, 32, 78, 101, 119, 83, 111, 110, 103, 32, 78, 101, 119, 83, 111, 110, 
                103, 32, 78, 101, 119, 83, 111, 110, 103, 32, 78, 101, 119, 83, 111, 110, 
                103, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 2048 bytes
    return initdisk

def syx2disk(syx, welcomedata, select="VPCETY", layer=0):
    select = select.upper()
    disk = initdisk()
    disk[0x2b:0x2b+16] = welcomedata[:16]
    disk[0x4b:0x4b+24] = welcomedata[16:40]
    p1block = -1
    p2block = -1
    vblock = -1

    for i in range(len(syx)-12):
        if syx[i:i+2] == [0xf0, 0x43]:
            syx[i+2] = syx[i+2] & 0b01110000 #set channelnibble to 0
        ''' TODO:
        if syx[i:i+10] == RINSTHEAD and ("R" in select):
            pass
        elif syx[i:i+10] == RKAT1HEAD and ("R" in select):
            pass
        elif syx[i:i+10] == RKAT2HEAD and ("R" in select):
            pass
        elif syx[i:i+10] == RSEQHEAD and ("R" in select):
            pass
        elif syx[i:i+10] == SYSQHEAD and ("S" in select):
            pass
        elif syx[i:i+10] == NSEQHEAD and ("S" in select):
            pass
        elif syx[i:i+10] == SSONGHEAD and ("S" in select):
            pass
        elif syx[i:i+10] == SYSRHEAD and ("S" in select):
            pass
        '''
        if syx[i:i+10] == SYS1HEAD and ("Y" in select):
            disk[0x20:0x20+27] = syx[i+10:i+37]
        elif syx[i:i+10] == SYS2HEAD and ("Y" in select):
            disk[0x3b:0x3b+16] = syx[i+10:i+26]
        elif syx[i:i+10] == SYS3HEAD and ("Y" in select):
            disk[0x4b:0x4b+32] = syx[i+10:i+42]
        elif syx[i:i+10] == PCHEAD and ("C" in select):
            disk[0x100:0x100+256] = syx[i+10:i+266]
        elif syx[i:i+10] == MCTOCTHEAD and ("T" in select):
            disk[0x200:0x200+24] = syx[i+10:i+34]
        elif syx[i:i+1] == MCTFULLHEAD and ("T" in select):
            disk[0x218:0x218+256] = syx[i+10:i+266]
        elif syx[i:i+10] == EFG1HEAD and ("E" in select):
            disk[0x318:0x318+55] = syx[i+10:i+65]
        elif syx[i:i+10] == EFG2HEAD and ("E" in select):
            disk[0x34f:0x34f+55] = syx[i+10:i+65]
        elif syx[i:i+10] == EFG3HEAD and ("E" in select):
            disk[0x386:0x386+55] = syx[i+10:i+65]
        elif syx[i:i+10] == EFG4HEAD and ("E" in select):
            disk[0x3bd:0x3bd+55] = syx[i+10:i+65]
        elif syx[i:i+10] == PMEM1HEAD and ("P" in select) and (p1block<3):
            p1block += 1
            if p1block == 3:
                vv = 25
            else:
                vv = 32
            for v in range(vv):
                disk[0x400+3200*p1block+128*v:0x400+3200*p1block+128*v+76] = syx[i+10+76*v:i+10+76*(v+1)]
        elif syx[i:i+10] == PMEM2HEAD and ("P" in select) and (p2block<3):
            p2block += 1
            if p2block == 3:
                vv = 25
            else:
                vv = 32
            for v in range(vv):
                disk[0x400+3200*p2block+128*v+76:0x400+3200*p2block+128*v+101] = syx[i+10+25*v:i+10+25*(v+1)]
        elif syx[i:i+6] == VMEMHEAD and ("V" in select) and (vblock<3):
            vblock += 1
            if vblock == 3:
                disk[0x3600+3200*vblock:0x3600+3200*vblock+3200] = syx[i+6:i+6+3200]
            else:
                disk[0x3600+3200*vblock:0x3600+3200*vblock+4096] = syx[i+6:i+6+4096]

            for v in range(25): #AT PBIAS correction
                if disk[0x3600 + 3200*vblock + 128*v + 86] > 50:
                    disk[0x3600 + 3200*vblock + 128*v + 86] -= 51
                else:
                    disk[0x3600 + 3200*vblock + 128*v + 86] += 50
        elif select == "R" and disk[i:i+10] == SYSRHEAD:
            pass
        elif select == "R" and disk[i:i+10] == RINSTHEAD:
            pass
        elif select == "R" and disk[i:i+10] == RKAT1HEAD:
            pass
        elif select == "R" and disk[i:i+10] == RKAT2HEAD:
            pass
        elif select == "R" and disk[i:i+10] == RSEQHEAD:
            pass

    if layer > 0:
        # RE-INITIALIZE PFM DATA 
        for v in range(100):
            disk[0x400 + 128*v:0x400 + 128*(v+1)] = v2p(disk[0x3600 + 128*v:0x3600 + 128*(v+1)], v, layer)

    return disk

def disk2syx(disk, welcomedata=WELCOMEMESSAGE, select="VP", layer=0):
    select = select.upper()
    if layer > 0:
        # RE-INITIALIZE PFM DATA 
        for v in range(100):
            disk[0x400 + 128*v:0x400 + 128*(v+1)] = v2p(disk[0x3600 + 128*v:0x3600 + 128*(v+1)], v, layer)

    syx = []
    if "V" in select:
        #VMEM
        syx += vdata2syx(disk[0x3600:0x3600+12800])

    if "P" in select or "D" in select:        
        #PMEM2
        #PMEM
        syx += pdata2syx(disk[0x400:0x400+12800])

    if "C" in select:
        #PC
        size = 266
        dat = PCHEAD + disk[0x100:0x100+256]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]

    if "E" in select:
        #EFG1
        size = 65
        dat = EFG1HEAD + disk[0x318:0x318+55]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #EFG2
        size = 65
        dat = EFG2HEAD + disk[0x34f:0x34f+55]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #EFG3
        size = 65
        dat = EFG3HEAD + disk[0x386:0x386+55]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #EFG4
        size = 65
        dat = EFG4HEAD + disk[0x3bd:0x3bd+55]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]

    if "T" in select:
        #MCTFULL
        size = 266
        dat = MCTFULLHEAD + disk[0x218:0x218+256]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #MCTOCT
        size = 34
        dat = MCTOCTHEAD + disk[0x200:0x200+24]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]

    if "Y" in select:   
        disk[0x2b:0x2b+16] = welcomedata[:16]
        disk[0x4b:0x4b+24] = welcomedata[16:40]
        #SYS3
        size = 33
        dat = SYS3HEAD + disk[0x4b:0x4b+32]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #SYS2
        size = 26
        dat = SYS2HEAD + disk[0x3b:0x3b+16]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
        #SYS1
        size = 37
        dat = SYS1HEAD + disk[0x20:0x20+27]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
    
    if "S" in select:
        pass #TODO: SEQUENCER DATA
        # SYSQ
        # NSEQ
        # SSONG 

    if "R" in select:
        #TODO: RHYTHM DATA
        #SYSR
        size =26
        dat = SYSRHEAD + disk[0x20:0x20+16]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
 
        #RINST
        size = 193
        dat = RINSTHEAD + disk[0x100:0x100+183]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
 
        #RKAT1
        size = 71
        dat = RKAT1HEAD + disk[0x200:0x200+61]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
 
        #RKAT2
        size = 71
        dat = RKAT2HEAD + disk[0x23d:0x23d+61]
        syx += [0xf0, 0x43, 0x00, 0x7e, size>>7, size&127]
        syx += dat
        syx += [checksum(dat), 0xf7]
 
        #RSEQ
        #TODO
    return syx

#VMEM BANK * 4
def vdata2syx(vdata):
    syx = []
    for v in range(100):
        if vdata[128*v+86]<50:
            vdata[128*v+86] += 51
        else:
            vdata[128*v+86] -= 50

    for i in range(4):
        #BLOCK HEADER
        syx += [0xf0, 0x43, 0x10, 0x24, 0x07, i+1, 0xf7]

        #VMEM
        syx += [0xf0, 0x43, 0x00, 0x04, 0x20, 0x00]
        vmem = vdata[3200*i:3200*(i+1)] + 7*list(initvmem)
        syx += vmem
        syx += [checksum(vmem), 0xf7]
    return syx

#PMEM BANK * 4
def pdata2syx(pdata):
    #pdata = 100 * (76 bytes PMEM1 + 25 bytes PMEM2 + 27*null) 
    syx = []
    for i in range(4):
        pmem1 = []
        pmem2 = []
        for p in range(25):
            pmem1 += pdata[3200*i+128*p:3200*i+128*p+76]
            pmem2 += pdata[3200*i+128*p+76:3200*i+128*p+101]
        pmem1 += 7*list(initperf[:76])
        pmem2 += 7*list(initperf[76:])

        #BLOCK HEADER
        syx += [0xf0, 0x43, 0x10, 0x10, 0x75, 0x01, i, 0xf7]

        #PMEM2
        syx += [0xf0, 0x43, 0x00, 0x7e, 0x06, 0x2a]
        syx += LM__8073PM + pmem2
        syx += [checksum(LM__8073PM + pmem2), 0xf7]
        
        #PMEM
        syx += [0xf0, 0x43, 0x00, 0x7e, 0x13, 0x0a]
        syx += LM__8976PM + pmem1
        syx += [checksum(LM__8976PM + pmem1), 0xf7]
    return syx

def checksum(data):
    return (128 - (sum(data) % 128)) % 128

def v2p(vdata, i, layer=0):
    pdata = list(initperf) + 27*[0]
    vdata = ys_v50(vdata)
    for v in range(8):
        if v < layer:
            pdata[1 + 8*v] = i #Voice No.
            pdata[5 + 8*v] = ( #Detune
                    [7],
                    [7],
                    [6,8],
                    [7,6,8],
                    [6,8,5,9],
                    [7,6,8,5,9],
                    [6,8,5,9,4,10],
                    [7,6,8,5,9,4,10],
                    [7,7,6,8,5,9,3,11])[layer][v] 
            pdata[7 + 8*v] = (99, 99, 98, 97, 95, 94, 93, 93, 92)[layer] #Volume
            pdata[76 + v] = 65 #FX enable
    pdata[66:76] = vdata[57:67] #NAME
    pdata[76+8:76+15] = vdata[94:101] #FX
    return pdata

def ys_v50(vmm):
    if (vmm[94] == 0) and (vmm[91] != 0):
        vmm[94] = vmm[91]
        vmm[95] = vmm[93]
        vmm[96] = 100
        vmm[97] = 0
        vmm[98] = vmm[92]
        if vmm[94] in (5, 6):
            vmm[99] = vmm[92]
        else:
            vmm[99] = 0
    return vmm

def voicename(v):
    s = ''
    for k in range(57, 67):
        s += chr(v[k])
    return s

def newname(fn):
    ext = os.path.splitext(fn)[1]
    if ext == '':
        ext = '.syx'
    fn = os.path.splitext(fn)[0] + ext
    if os.path.exists(fn):
        nm = os.path.splitext(fn)[0]
        count = 0
        while os.path.exists(fn):
            count += 1
            fn = nm + "({}){}".format(count, ext)
        return fn
    else:
        return fn

def outname(fname, outpath=os.getcwd()):
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'()-@^_`{}"
    extlist = []
    for nm in glob(os.path.join(outpath, "*.*")):
        extlist.append(os.path.splitext(nm)[1])
    fn = os.path.split(fname)[1]
    fn = os.path.splitext(fn)[0][:8].upper()
    for k in range(len(fn)):
        if fn[k] not in allowed:
            fn = fn[:k] + "_" + fn[k+1:]
    for i in range(101,200):
        ext = ".I" + str(i)[-2:]
        outname = os.path.join(outpath, fn) + ext
        if not os.path.exists(outname):
            if not (ext in extlist): 
                return outname
    return outname

def doit(infiles, outfile, outtype='syx', welcome=WELCOMEMESSAGE, select="VP", layer=0):
    welcome = welcome.ljust(40)[:40]
    welcomedata = []
    for k in welcome:
        welcomedata.append(ord(k))

    #INFILE
    indata = array.array('B')
    for i in infiles:
        for infile in glob(i):
            if os.path.exists(infile):
                size = os.path.getsize(infile)
                with open(infile, 'rb') as f:
                    indata.fromfile(f, size)
                print ("Read data from: {}".format(infile))
    
    indata = indata.tolist()
    infile = glob(infiles[0])[0]
    in_ext = os.path.splitext(infile)[1].lower()
    if in_ext[:2] in (".i", ".v", ".c") and (in_ext[2].isdigit()) and (size in (26624, 17729, 32768) or size>35000):
        intype = "ixx"
        if in_ext[:2] == ".c" and indata[4:10] == [0x56, 0x35, 0x30, 0x53, 0x59, 0x4e]:
            #convert V50SYN *.Cxx to *.Ixx format
            indata[0x318:0x34f] = list(initefg1)
            indata[0x34f:0x386] = list(initefg1)
            indata[0x386:0x3bd] = list(initefg1)
            indata[0x3bd:0x3f4] = list(initefg1)
            indata[0x3f4:0x400] = 12*[0]
            vp = indata[0x700:0x700+25600]
            indata[0x400:0x400+25600] = vp
    else:
        intype = "syx"

    #OUTFILE
    if os.path.isdir(outfile):
        if outtype == "ixx":
            outfile = outname(os.path.basename(infile), outfile)
        else:
            outtype = "syx"
            fn = os.path.basename(infile)
            fn = os.path.splitext(fn)[0]
            outfile = os.path.join(outfile, fn)
            outfile = newname(outfile)

    else:
        out_ext = os.path.splitext(outfile)[1].lower()
        if outtype == 'ixx':
            outfile = outname(os.path.basename(outfile), os.path.split(outfile)[0])
        else: #outtype == 'syx'
            if out_ext[:2] == '.i' and out_ext[2:].isdigit():
                outtype = 'ixx'
                outfile = outname(os.path.basename(outfile), os.path.split(outfile)[0])
            else:
                outtype = 'syx'
                outfile = newname(outfile)

    if len(indata) != 0:
        size = len(indata)

        if intype == "ixx":
            outdata = disk2syx(indata, welcomedata, select, layer)
            if outtype == "ixx":
                out = syx2disk(outdata, welcomedata, select, layer)
                outdata = out
        else:
            outdata = syx2disk(indata, welcomedata, select, layer)
            if outtype == "syx":
                out = disk2syx(outdata, welcomedata, select, layer)
                outdata = out
        
        outdat = array.array('B')
        outdat.fromlist(outdata)
        with open(outfile, 'wb') as f:
            outdat.tofile(f)
        print ("Saved as: {}".format(outfile))
    else:
        print ("No data found")
    return 

########################################

if __name__ == '__main__':
    parser = ArgumentParser(description = "A Yamaha V50 file conversion utility", epilog="http://dxconvert.martintarenskeen.nl") 
    parser.add_argument('-l', '--layer', type=int, default=0, help="LAYER = 0 to 8 (0=from source, or Initperf)")
    parser.add_argument('-o', '--outtype', help='OUTTYPE=[Ixx|syx]', default='syx')
    parser.add_argument('-s', '--select', default='VP', help = 'SELECT = [VPCETYR] (V=Voices(default), P=Performances(default), C=Program Change Table, E=Pfm Effect Generators, T=Microtuning Tables, Y=System, R=Rhythm') 
    parser.add_argument('-v', '--version', action = 'version', version = VERSION)
    parser.add_argument('-w', '--welcome', help='V50 welcome message', default=WELCOMEMESSAGE)
    parser.add_argument('infile', nargs = '+', help = 'Read data from INFILE(s)')
    parser.add_argument('outfile', help = "Save as OUTFILE (*.syx, *.Ixx)")
    args = parser.parse_args()
    infiles = args.infile
    outfile = args.outfile
    welcome = args.welcome
    select = args.select
    layer = min(8, args.layer)
    outtype = args.outtype.lower()
    if welcome != WELCOMEMESSAGE and "Y" not in select:
        select += "Y"

    doit(infiles, outfile, outtype, welcome, select, layer)
    sys.exit(0)

