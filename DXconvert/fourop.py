
from . import dx7
from . import dxcommon
from math import log
try:
    range = xrange
except NameError:
    pass

maxvmm = (31, 31, 31, 15, 15, 99, 127, 99, 63, 126,
        31, 31, 31, 15, 15, 99, 127, 99, 63, 126,
        31, 31, 31, 15, 15, 99, 127, 99, 63, 126,
        31, 31, 31, 15, 15, 99, 127, 99, 63, 126,
        127, 99, 99, 99, 99, 127, 48, 12, 31,
        99, 99, 99, 99, 99, 99, 100, 99,
        127, 127, 127, 127, 127, 127, 127, 127, 127, 127,
        99, 99, 99, 99, 99, 99,
        127, 127, 127, 127, 127, 127, 127, 127,
        7, 99, 99, 99, 99, 100, 99, 0, 0, 3, 
        10, 40, 99, 32, 100, 100, 1, 75, 99, 99,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0)

#INIT VOICE
def initvcd():
    return [31, 31, 0, 15, 15, 0, 0, 0, 0, 0, 0, 4, 3, 
           31, 31, 0, 15, 15, 0, 0, 0, 0, 0, 0, 4, 3, 
           31, 31, 0, 15, 15, 0, 0, 0, 0, 0, 0, 4, 3, 
           31, 31, 0, 15, 15, 0, 0, 0, 0, 0, 90, 4, 3, 
           0, 0, 35, 0, 0, 0, 0, 2, 6, 0, 24, 
           0, 4, 0, 0, 40, 1, 0, 0, 50, 0, 0, 0, 50, 0, 
           73, 78, 73, 84, 32, 86, 79, 73, 67, 69,
           99, 99, 99, 50, 50, 50]

def initacd():
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def initacd2():
    return [0, 0, 50, 0, 0, 0, 0, 0, 0, 0]

def initacd3():
    return [0, 50, 100, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def initefeds():
    return [0, 0, 50]

def initdelay():
    return [0, 0]

def initvmm():
    return [31, 31, 0, 15, 15, 0, 0, 0, 4, 3, 31, 31, 0, 15, 15, 0,
           0, 0, 4, 3, 31, 31, 0, 15, 15, 0, 0, 0, 4, 3, 31, 31, 
           0, 15, 15, 0, 0, 90, 4, 3, 0, 35, 0, 0, 0, 98, 24, 4, 
           4, 0, 40, 50, 0, 0, 0, 50, 0, 73, 78, 73, 84, 32, 86, 79, 
           73, 67, 69, 99, 99, 99, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 0, 50, 
           100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# SysEx ID strings
ACED  = LM__8976AE = [0x4c, 0x4d, 0x20, 0x20, 0x38, 0x39, 0x37, 0x36, 0x41, 0x45]
ACED2 = LM__8023AE = [0x4c, 0x4d, 0x20, 0x20, 0x38, 0x30, 0x32, 0x33, 0x41, 0x45]
ACED3 = LM__8073AE = [0x4c, 0x4d, 0x20, 0x20, 0x38, 0x30, 0x37, 0x33, 0x41, 0x45]
DELAY = LM__8054DL = [0x4c, 0x4d, 0x20, 0x20, 0x38, 0x30, 0x35, 0x34, 0x44, 0x4C]
EFEDS = LM__8036EF = [0x4c, 0x4d, 0x20, 0x20, 0x38, 0x30, 0x33, 0x36, 0x45, 0x46]

# ALGO conversion (alg_dx7, op4, op2, op3, op1)
# watch DX7/DX9 algorithm 8(3) vs TX81z algorithm 3 Feedback position!
algo = ((0, 5, 3, 4, 2, ), 
        (13, 5, 3, 4, 2, ), 
        (7, 3, 4, 5, 2, ), 
        (6, 5, 3, 4, 2, ), 
        (4, 5, 3, 4, 2, ), 
        (21, 5, 3, 4, 2, ), 
        (30, 5, 3, 4, 2, ), 
        (31, 5, 3, 4, 2))

# EG and TL conversion tables inspired by
# http://www.angelfire.com/in2/yala/t2dx-fm.htm

# OUTPUT LEVEL conversion table 4op->dx7
out = (0, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 
        21, 22, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 
        39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 
        55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 
        71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 
        87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 99, 99, 99, 
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99)

# EG conversion tables

#AR = 3*R1 + 10
r1 = (13, 13, 16, 19, 22, 25, 28, 31, 
        34, 37, 41, 44, 47, 50, 53, 56, 
        59, 62, 65, 68, 71, 74, 77, 80, 
        83, 86, 89, 91, 94, 97, 98, 99)

#D1R = 3*R2 + 6
r2 = (9, 9, 12, 15, 18, 21, 24, 27,
        30, 33, 36, 39, 42, 45, 48, 51, 
        54, 57, 60, 63, 66, 69, 72, 75, 
        78, 81, 84, 87, 90, 93, 96, 99)

r3 = r2

r4 = (16, 16, 21, 28, 34, 40, 46, 52, 
        58, 64, 70, 76, 82, 88, 94, 99)

l1 = 99

l2 = (0, 44, 48, 52, 56, 60, 63, 66, 
        71, 75, 79, 82, 87, 92, 95, 99)
l3 = 0
l4 = 0

# 4op frequencies (16*CRS+FINE)
freq_4op = (0.50, 0.56, 0.62, 0.68, 0.75, 0.81, 0.87, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 0.93, 
        0.71, 0.79, 0.88, 0.96, 1.05, 1.14, 1.23, 1.32, 1.32, 1.32, 1.32, 1.32, 1.32, 1.32, 1.32, 1.32, 
        0.78, 0.88, 0.98, 1.07, 1.17, 1.27, 1.37, 1.47, 1.47, 1.47, 1.47, 1.47, 1.47, 1.47, 1.47, 1.47, 
        0.87, 0.97, 1.08, 1.18, 1.29, 1.40, 1.51, 1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 
        1.00, 1.06, 1.12, 1.18, 1.25, 1.31, 1.37, 1.43, 1.50, 1.56, 1.62, 1.68, 1.75, 1.81, 1.87, 1.93, 
        1.41, 1.49, 1.58, 1.67, 1.76, 1.85, 1.93, 2.02, 2.11, 2.20, 2.29, 2.37, 2.46, 2.55, 2.64, 2.73, 
        1.57, 1.66, 1.76, 1.86, 1.96, 2.06, 2.15, 2.25, 2.35, 2.45, 2.55, 2.64, 2.74, 2.84, 2.94, 3.04, 
        1.73, 1.83, 1.94, 2.05, 2.16, 2.27, 2.37, 2.48, 2.59, 2.70, 2.81, 2.91, 3.02, 3.13, 3.24, 3.35, 
        2.00, 2.06, 2.12, 2.18, 2.25, 2.31, 2.37, 2.43, 2.50, 2.56, 2.62, 2.68, 2.75, 2.81, 2.87, 2.93, 
        2.82, 2.90, 2.99, 3.08, 3.17, 3.26, 3.34, 3.43, 3.52, 3.61, 3.70, 3.78, 3.87, 3.96, 4.05, 4.14, 
        3.00, 3.06, 3.12, 3.18, 3.25, 3.31, 3.37, 3.43, 3.50, 3.56, 3.62, 3.68, 3.75, 3.81, 3.87, 3.93, 
        3.14, 3.23, 3.33, 3.43, 3.53, 3.63, 3.72, 3.82, 3.92, 4.02, 4.12, 4.21, 4.31, 4.41, 4.51, 4.61, 
        3.46, 3.56, 3.67, 3.78, 3.89, 4.00, 4.10, 4.21, 4.32, 4.43, 4.54, 4.64, 4.75, 4.86, 4.97, 5.08, 
        4.00, 4.06, 4.12, 4.18, 4.25, 4.31, 4.37, 4.43, 4.50, 4.56, 4.62, 4.68, 4.75, 4.81, 4.87, 4.93, 
        4.24, 4.31, 4.40, 4.49, 4.58, 4.67, 4.75, 4.84, 4.93, 5.02, 5.11, 5.19, 5.28, 5.37, 5.46, 5.55, 
        4.71, 4.80, 4.90, 5.00, 5.10, 5.20, 5.29, 5.39, 5.49, 5.59, 5.69, 5.78, 5.88, 5.98, 6.08, 6.18, 
        5.00, 5.06, 5.12, 5.18, 5.25, 5.31, 5.37, 5.43, 5.50, 5.56, 5.62, 5.68, 5.75, 5.81, 5.87, 5.93, 
        5.19, 5.29, 5.40, 5.51, 5.62, 5.73, 5.83, 5.94, 6.05, 6.16, 6.27, 6.37, 6.48, 6.59, 6.70, 6.81, 
        5.65, 5.72, 5.81, 5.90, 5.99, 6.08, 6.16, 6.25, 6.34, 6.43, 6.52, 6.60, 6.69, 6.78, 6.87, 6.96, 
        6.00, 6.06, 6.12, 6.18, 6.25, 6.31, 6.37, 6.43, 6.50, 6.56, 6.62, 6.68, 6.75, 6.81, 6.87, 6.93, 
        6.28, 6.37, 6.47, 6.57, 6.67, 6.77, 6.86, 6.96, 7.06, 7.16, 7.26, 7.35, 7.45, 7.55, 7.65, 7.75, 
        6.92, 7.02, 7.13, 7.24, 7.35, 7.46, 7.56, 7.67, 7.78, 7.89, 8.00, 8.10, 8.21, 8.32, 8.43, 8.54, 
        7.00, 7.06, 7.12, 7.18, 7.25, 7.31, 7.37, 7.43, 7.50, 7.56, 7.62, 7.68, 7.75, 7.81, 7.87, 7.93, 
        7.07, 7.13, 7.22, 7.31, 7.40, 7.49, 7.57, 7.66, 7.75, 7.84, 7.93, 8.01, 8.10, 8.19, 8.28, 8.37, 
        7.85, 7.94, 8.04, 8.14, 8.24, 8.34, 8.43, 8.53, 8.63, 8.73, 8.83, 8.92, 9.02, 9.12, 9.22, 9.32, 
        8.00, 8.06, 8.12, 8.18, 8.25, 8.31, 8.37, 8.43, 8.50, 8.56, 8.62, 8.68, 8.75, 8.81, 8.87, 8.93, 
        8.48, 8.54, 8.63, 8.72, 8.81, 8.90, 8.98, 9.07, 9.16, 9.25, 9.34, 9.42, 9.51, 9.60, 9.69, 9.78, 
        8.65, 8.75, 8.86, 8.97, 9.08, 9.19, 9.29, 9.40, 9.51, 9.62, 9.73, 9.83, 9.94, 10.05, 10.16, 10.27, 
        9.00, 9.06, 9.12, 9.18, 9.25, 9.31, 9.37, 9.43, 9.50, 9.56, 9.62, 9.68, 9.75, 9.81, 9.87, 9.93, 
        9.42, 9.51, 9.61, 9.71, 9.81, 9.91, 10.00, 10.10, 10.20, 10.30, 10.40, 10.49, 10.59, 10.69, 10.79, 10.89, 
        9.89, 9.95, 10.04, 10.13, 10.22, 10.31, 10.39, 10.48, 10.57, 10.66, 10.75, 10.83, 10.92, 11.01, 11.10, 11.19, 
        10.00, 10.06, 10.12, 10.18, 10.25, 10.31, 10.37, 10.43, 10.50, 10.56, 10.62, 10.68, 10.75, 10.81, 10.87, 10.93, 
        10.38, 10.48, 10.59, 10.70, 10.81, 10.92, 11.02, 11.13, 11.24, 11.35, 11.46, 11.56, 11.67, 11.78, 11.89, 12.00, 
        10.99, 11.08, 11.18, 11.28, 11.38, 11.48, 11.57, 11.67, 11.77, 11.87, 11.97, 12.06, 12.16, 12.26, 12.36, 12.46, 
        11.00, 11.06, 11.12, 11.18, 11.25, 11.31, 11.37, 11.43, 11.50, 11.56, 11.62, 11.68, 11.75, 11.81, 11.87, 11.93, 
        11.30, 11.36, 11.45, 11.54, 11.63, 11.72, 11.80, 11.89, 11.98, 12.07, 12.16, 12.24, 12.33, 12.42, 12.51, 12.60, 
        12.00, 12.06, 12.12, 12.18, 12.25, 12.31, 12.37, 12.43, 12.50, 12.56, 12.62, 12.68, 12.75, 12.81, 12.87, 12.93, 
        12.11, 12.21, 12.32, 12.43, 12.54, 12.65, 12.75, 12.86, 12.97, 13.08, 13.19, 13.29, 13.40, 13.51, 13.62, 13.73, 
        12.56, 12.65, 12.75, 12.85, 12.95, 13.05, 13.14, 13.24, 13.34, 13.44, 13.54, 13.63, 13.37, 13.83, 13.93, 14.03, 
        12.72, 12.77, 12.86, 12.95, 13.04, 13.13, 13.21, 13.30, 13.39, 13.48, 13.57, 13.65, 13.74, 13.83, 13.92, 14.01, 
        13.00, 13.06, 13.12, 13.18, 13.25, 13.31, 13.37, 13.43, 13.50, 13.56, 13.62, 13.68, 13.75, 13.81, 13.87, 13.93, 
        13.84, 13.94, 14.05, 14.16, 14.27, 14.38, 14.48, 14.59, 14.70, 14.81, 14.92, 15.02, 15.13, 15.24, 15.35, 15.46, 
        14.00, 14.06, 14.12, 14.18, 14.25, 14.31, 14.37, 14.43, 14.50, 14.56, 14.62, 14.68, 14.75, 14.81, 14.87, 14.93, 
        14.10, 14.18, 14.27, 14.36, 14.45, 14.54, 14.62, 14.71, 14.80, 14.89, 14.98, 15.06, 15.15, 15.24, 15.33, 15.42, 
        14.13, 14.22, 14.32, 14.42, 14.52, 14.62, 14.71, 14.81, 14.91, 15.01, 15.11, 15.20, 15.30, 15.40, 15.50, 15.60, 
        15.00, 15.06, 15.12, 15.18, 15.25, 15.31, 15.37, 15.43, 15.50, 15.56, 15.62, 15.68, 15.75, 15.81, 15.87, 15.93, 
        15.55, 15.59, 15.68, 15.77, 15.86, 15.95, 16.03, 16.12, 16.21, 16.30, 16.39, 16.47, 16.56, 16.65, 16.74, 16.83, 
        15.57, 15.67, 15.78, 15.89, 16.00, 16.11, 16.21, 16.32, 16.43, 16.54, 16.65, 16.75, 16.86, 16.97, 17.08, 17.19, 
        15.70, 15.79, 15.89, 15.99, 16.09, 16.19, 16.28, 16.38, 16.48, 16.58, 16.68, 16.77, 16.87, 16.97, 17.07, 17.17, 
        16.96, 17.00, 17.09, 17.18, 17.27, 17.36, 17.44, 17.53, 17.62, 17.71, 17.80, 17.88, 17.97, 18.06, 18.15, 18.24, 
        17.27, 17.36, 17.46, 17.56, 17.66, 17.76, 17.85, 17.95, 18.05, 18.15, 18.25, 18.35, 18.44, 18.54, 18.64, 18.74, 
        17.30, 17.40, 17.51, 17.62, 17.73, 17.84, 17.94, 18.05, 18.16, 18.27, 18.38, 18.48, 18.59, 18.70, 18.81, 18.92, 
        18.37, 18.41, 18.50, 18.59, 18.68, 18.77, 18.85, 18.94, 19.03, 19.12, 19.21, 19.29, 19.38, 19.47, 19.56, 19.65, 
        18.84, 18.93, 19.03, 19.13, 19.23, 19.33, 19.42, 19.52, 19.62, 19.72, 19.82, 19.91, 20.01, 20.11, 20.21, 20.31, 
        19.03, 19.13, 19.24, 19.35, 19.46, 19.57, 19.67, 19.78, 19.89, 20.00, 20.11, 20.21, 20.32, 20.43, 20.54, 20.65, 
        19.78, 19.82, 19.91, 20.00, 20.09, 20.18, 20.26, 20.35, 20.44, 20.53, 20.62, 20.70, 20.79, 20.88, 20.97, 21.06, 
        20.41, 20.50, 20.60, 20.70, 20.80, 20.90, 20.99, 21.09, 21.19, 21.29, 21.39, 21.48, 21.58, 21.68, 21.78, 21.88, 
        20.76, 20.86, 20.97, 21.08, 21.19, 21.30, 21.40, 21.51, 21.62, 21.73, 21.48, 21.94, 22.05, 22.16, 22.27, 22.38, 
        21.20, 21.23, 21.32, 21.41, 21.50, 21.59, 21.67, 21.76, 21.85, 21.94, 22.03, 22.11, 22.20, 22.29, 22.38, 22.47, 
        21.98, 22.07, 22.17, 22.27, 22.37, 22.47, 22.56, 22.66, 22.76, 22.86, 22.96, 23.05, 23.15, 23.25, 23.35, 23.45, 
        22.49, 22.59, 22.70, 22.81, 22.92, 23.03, 23.13, 23.24, 23.35, 23.46, 23.57, 23.67, 23.78, 23.89, 24.00, 24.11, 
        23.55, 23.64, 23.74, 23.84, 23.94, 24.04, 24.13, 24.23, 24.33, 24.43, 24.53, 24.62, 24.72, 24.82, 24.92, 25.02, 
        24.22, 24.32, 24.43, 24.54, 24.65, 24.76, 24.86, 24.97, 25.08, 25.19, 25.30, 25.40, 25.51, 25.62, 25.73, 25.84, 
        25.95, 26.05, 26.16, 26.27, 26.38, 26.49, 26.59, 26.70, 26.81, 26.92, 27.03, 27.13, 27.24, 27.35, 27.46, 27.57)

freq_dx21 = (0.50, 0.71, 0.78, 0.87, 1.00, 1.41, 1.57, 1.73,
        2.00, 2.82, 3.00, 3.14, 3.46, 4.00, 4.24, 4.71,
        5.00, 5.19, 5.65, 6.00, 6.28, 6.92, 7.00, 7.07, 
        7.85, 8.00, 8.48, 8.65, 9.00, 9.42, 9.89, 10.00,
        10.38, 10.99, 11.00, 11.30, 12.00, 12.11, 12.56, 12.72,
        13.00, 13.84, 14.00, 14.10, 14.13, 15.00, 15.55, 15.57,
        15.70, 16.96, 17.27, 17.30, 18.37, 18.84, 19.03, 19.78,
        20.41, 20.76, 21.20, 21.98, 22.49, 23.55, 24.22, 25.95)

# LFO frequency
lfs = (0.001, 0.007, 0.021, 0.042, 0.086, 
        0.120, 0.193, 0.280, 0.346, 0.426, 
        0.533, 0.667, 0.773, 0.907, 1.121, 
        1.226, 1.440, 1.547, 1.709, 1.923, 
        2.242, 2.564, 2.666, 2.994, 3.095, 
        3.322, 3.861, 4.065, 4.504, 4.694, 
        5.128, 5.347, 5.780, 6.211, 6.451, 
        6.666, 6.849, 7.692, 8.130, 8.547, 
        9.009, 9.433, 10.309, 10.752, 11.111, 
        11.627, 12.048, 12.500, 12.820, 13.227, 
        13.227, 14.513, 15.384, 15.384, 16.339, 
        17.123, 18.018, 18.903, 19.646, 19.646, 
        20.618, 21.505, 22.222, 22.321, 23.041, 
        23.980, 24.752, 24.752, 25.641, 25.641, 
        26.455, 27.397, 27.548, 29.325, 30.769, 
        30.769, 32.573, 34.129, 34.129, 36.363, 
        38.022, 38.022, 39.370, 39.370, 41.152, 
        43.290, 43.290, 44.444, 45.248, 46.082, 
        46.082, 47.846, 47.846, 49.504, 49.504, 
        49.504, 51.282, 52.910, 52.910, 52.910)

#AMD range measured from DX100 both and V50 and then averaged
amd = ( 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.50, 0.50, 0.50, 1.25,
        1.25, 1.25, 1.25, 1.95, 1.95, 1.95, 2.35, 2.35, 2.75, 2.75,
        3.10, 3.50, 3.50, 3.90, 4.25, 4.25, 4.60, 5.00, 5.00, 5.40,
        5.75, 5.75, 5.75, 6.50, 6.50, 6.50, 7.25, 7.25, 7.25, 8.00,
        8.00, 8.35, 8.75, 8.75, 9.50, 9.50, 10.25, 10.60, 11.00, 11.00,
        11.75, 11.75, 12.50, 12.50, 13.25, 13.25, 14.00, 14.00, 14.75, 14.75,
        15.50, 15.50, 16.25, 17.00, 17.00, 17.70, 18.50, 18.50, 19.25, 20.00,
        20.70, 20.70, 21.50, 22.20, 22.95, 23.70, 24.40, 25.15, 25.85, 26.60,
        27.30, 28.10, 29.55, 30.25, 31.00, 32.45, 33.15, 35.25, 35.95, 37.30,
        39.35, 40.80, 43.20, 44.40, 47.50, 48.95, 52.90, 54.30, 57.75, 60.00)

def lfdtime(lfd):
    if lfd == 0:
        return 0
    step = 1.04355264
    start = 0.16199306
    return step**lfd * start

def lfd(t):
    if t == 0:
        return 0
    step = 1.04355264
    start = 0.16199306
    return int(round(max(0, min(99, log(t/start, step)))))

#PMS conversion factor
pms_factor = (0, 0.103, 0.122, 0.155, 0.186, 0.231, 0.569, 0.662)

#PEG rate conversion table
pr = (1, 2, 4, 5, 6, 7, 8, 10, 12, 13, 
        14, 16, 18, 19, 20, 22, 24, 25, 26, 27, 
        28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 
        38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
        48, 49, 50, 52, 54, 55, 56, 57, 58, 59, 
        60, 61, 62, 63, 64, 65, 66, 68, 70, 71, 
        72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 
        82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 
        92, 93, 94, 95, 96, 97, 98, 98, 98, 98, 
        98, 98, 98, 98, 98, 98, 98, 98, 98, 99, 
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 
        99, 99, 99, 99, 99, 99, 99, 99) 

#FX V50 YS200
#reverbtime seconds
reverbtime = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
        2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8,
        4.0, 4.5, 5.0, 5.5, 6.0, 6.5,
        7.0, 8.0, 9.0, 10)

#delaytime milliseconds
delaytime = [0.1]
for i in range(1, 76):
    delaytime.append(4*i)
delaytime = tuple(delaytime)    

#dblrtime milliseconds
doublertime = [0.1]
for i in range(1, 101):
    doublertime.append(0.5*i)
doublertime = tuple(doublertime)

def vcd2vmm(vcd=initvcd(), acd=initacd(), acd2=initacd2(), acd3=initacd3(), efeds=initefeds(), delay=initdelay()):
    vmm = [0]*128
    acd[19] = 0
    for op in range(4): #op=0, 1, 2, 3 --> operator=4, 2, 3, 1
        vmm[0+10*op:5+10*op] = vcd[0+13*op:5+13*op] #EG
        vmm[5+10*op] = vcd[5+13*op]&127
        
        AME=vcd[8+13*op]&1
        EBS=vcd[7+13*op]&7
        KVS=vcd[9+13*op]&7
        vmm[6+10*op] = (AME<<6)+(EBS<<3)+(KVS)
        vmm[7+10*op] = vcd[10+13*op] #OUT
        vmm[8+10*op] = vcd[11+13*op] #CRS
        
        LS2=(acd2[8]>>(0, 2, 1, 3)[op])&1
        KVS2=(vcd[9+13*op]>>3)&1
        RS=vcd[6+13*op]&3 
        DET=vcd[12+13*op]&7
        vmm[9+10*op] = (LS2<<6)+(KVS2<<5)+(RS<<3)+DET
        
        FIXRM = acd2[4+op]&1
        EGSFT = acd[4+5*op]&3
        FIX = acd[5*op]&1
        FIXRG = acd[1+5*op]&7
        vmm[73+2*op] = (FIXRM<<6)+(EGSFT<<5)+(FIX<<3)+FIXRG
        
        OSW = acd[3+5*op]&7
        FINE = acd[2+5*op]&15
        vmm[74+2*op] = (OSW<<4)+FINE
    
    SY = vcd[58]&1
    FBL = vcd[53]&7
    ALG = vcd[52]&7
    vmm[40] = (SY<<6)+(FBL<<3)+ALG
   
    vmm[41] = vcd[54]&127 #LFS
    vmm[42] = vcd[55]&127 #LFD
    vmm[43] = vcd[56]&127 #PMD
    vmm[44] = vcd[57]&127 #AMD

    PMS = vcd[60]&7
    AMS = vcd[61]&3
    LFW = vcd[59]&3
    vmm[45] = (PMS<<4)+(AMS<<2)+LFW
    
    vmm[46] = vcd[62]&63 #TRPS
    vmm[47] = vcd[64]&15 #PBR

    CH = vcd[70]&1
    MO = vcd[63]&1
    SU = vcd[68]&1
    PO = vcd[69]&1
    PM = vcd[65]&1
    vmm[48] = (CH<<4)+(MO<<3)+(SU<<2)+(PO<<1)+PM
    vmm[49] = vcd[66]&127 #PORT
    vmm[50] = vcd[67]&127 #FCVOLUM
    vmm[51] = vcd[71]&127 #MWPITCH
    vmm[52] = vcd[72]&127 #MWAMPLI
    vmm[53] = vcd[73]&127 #BCPITCH
    vmm[54] = vcd[74]&127 #BCAMPLI
    vmm[55] = vcd[75]&127 #BCPBIAS
    vmm[56] = vcd[76]&127 #BCEBIAS
    vmm[57:67] = vcd[77:87] #VOICENAME
    vmm[67:73] = vcd[87:93] #PEG

    vmm[81] = acd[20]&127 #REV
    vmm[82] = acd[21]&127 #FCPITCH
    vmm[83] = acd[22]&127 #FCAMPLI

    vmm[84] = acd2[0]&127 #ATPITCH
    vmm[85] = acd2[1]&127 #ATAMPLI
    if acd2[2] < 50:
        ATPBIAS = acd2[2] + 51
    else:
        ATPBIAS = acd2[2] - 50
    vmm[86] = ATPBIAS&127
    vmm[87] = acd[3]&127 #ATEBIAS

    vmm[88] = 0
    vmm[89] = 0
    vmm[90] = ((delay[0]<<1)&2) + (delay[1]&1) #DS55_delay sw + long/short

    vmm[91] = efeds[0]&15 #YS_FXpreset
    vmm[92] = efeds[1]&63 #YS_FXtime
    vmm[93] = efeds[2]&127 #YS_FXbalance

    vmm[94] = acd3[0]&63 #V50_FXselect
    vmm[95] = acd3[1]&127 #V50_FXbalance
    vmm[96] = acd3[2]&127 #V50_FXlevel
    vmm[97] = acd3[3]&1 #V50_FXmix
    vmm[98] = acd3[4]&127 #V50_FXpar1
    vmm[99] = acd3[5]&127 #V50_FXpar2
    vmm[100] = acd3[6]&127 #V50_FXpar3
    vmm[101:128] = [0]*27
    return vmm


# convert TX81Z to DX21/27/100 frequencies
def freq_4op_dx21(coarse4op, fine4op):
    f = freq_4op[16*coarse4op + fine4op]
    return dxcommon.closeto(f, freq_dx21, True)

def tx81z_dx21(vmm):
    vcd, acd, acd2, acd3, efeds, delay = vmm2vcd(vmm)
    if (acd[17] + acd[7] + acd[12] + acd[2] + acd[15] + acd[5] + acd[10] + acd[0]) == 0:
        return vmm, 0
    
    transpose = vcd[62] - 24
    f = [1.0, 1.0, 1.0, 1.0]

    for op in range(4):
        if acd[(15, 5, 10, 0)[op]]:
            f[op] = 0.0001 + fix_4op(acd2[7-op], acd[1+5*op], vcd[11+13*op], acd[2+5*op]) / 440.   #A3
        else:
            f[op] = freq_4op[16*vcd[(50, 24, 37, 11)[op]] + acd[(17, 7, 12, 2)[op]]]

    if (f[0]<6.49) & (f[1]<6.49) & (f[2]<6.49) & (f[3]<6.49):
        transpose -= 24
        for i in range(4):
            f[i] *= 4
    elif (f[0]<12.98) & (f[1]<12.98) & (f[2]<12.98) & (f[3]<12.98) :
        transpose -= 12
        for i in range(4):
            f[i] *= 2

    for op in range(4):
        if acd[(18, 8, 13, 3)[op]] > 3:  #OSW = 5,6,7,8
            if carrier(vcd[52], op) == False:
                if f[op] < 12.98:
                    f[op] *= 2

    for op in range(4):
        vcad = (39, 13, 26, 0)[op]
        acad = (15, 5, 10, 0)[op]
        vcd[11+vcad] = freq_4op_dx21(vcd[11+vcad], acd[2+acad])

    #freq ratio calc
    for op in range(4):
        vcd[(50, 24, 37, 11)[op]] = dxcommon.closeto(f[op], freq_dx21)

    #undo unnecessary transpositions & finetune detuning 
    n = 2**(3.74/1200/6) 
    det = (n**-3, n**-2, n**-1, 1, n, n**2, n**3, 1)
 
    for z in range(2):
        if (freq_4op[16*vcd[11]]/2 in freq_dx21) & (freq_4op[16*vcd[11+26]]/2 in freq_dx21) & (freq_4op[16*vcd[11+13]]/2 in freq_dx21) & (freq_4op[16*vcd[11+39]]/2 in freq_dx21):
            f[0] /= 2
            f[1] /= 2
            f[2] /= 2
            f[3] /= 2
            transpose += 12
            for op in range(4):
                det_in = det[vcd[(51, 25, 38, 12)[op]]]
                dd = 64
                ii = 0
                for i in range(64):
                    for dt in range(7):
                        d = max(f[op]*det_in, freq_4op[16*i]*det[dt]) / min(f[op]*det_in, freq_4op[16*i]*det[dt])
                        if d < dd:
                            dd = d
                            ii = i
                            detune = dt
                        else:
                            break
                vcd[(50, 24, 37, 11)[op]] = ii
                vcd[(51, 25, 38, 12)[op]] = detune

   
    #undo out-of-range transpositions
    transposed = 0
    while transpose < -24:
        transpose += 12
        transposed += 12
    while transpose > 24:
        transpose -= 12
        transposed -= 12
    if transposed != 0:
        naam = dxcommon.list2string(vcd[77:87])

    vcd[62] = transpose + 24
    vmm = vcd2vmm(vcd, initacd(), initacd2(), initacd3(), initefeds(), initdelay())
    return vmm, transposed
   

# DX7 frequencies
def dx7_freq(coarse, fine):
    f = max(0.5, float(coarse))
    f += f * fine / 100.0
    return f

def fix_dx7(crs, fine):
    a = 9.772 ** (1/99.0)
    f = a ** fine
    f = (10 ** (crs%4)) * f
    return 0.00001 + round(f, 3)


def freq_4op_dx7(coarse4op, fine4op):
    f = freq_4op[16*coarse4op + fine4op]
    if f in range(1,32):
        return int(f), 0
    dd = 32
    for c in range(32):
        for fin in range(100):
            d = max(dx7_freq(c, fin), f)/min(dx7_freq(c, fin), f)
            if d < dd:
                dd = d
                coarse = c
                fine = fin
            if dd == 1:
                break
        if dd == 1:
            break
    return coarse, fine

def fix_4op(mode4op, rng4op, crs4op, fine4op):
    crs4op = crs4op>>2
    fixfreq = (max(crs4op, 0.5)*16 + fine4op) * (2**rng4op)
    #fixfreq2 = fixhi[crs4op+16*rng4op] + fine4op*(2**rng4op)
    if mode4op == 1:
        fixfreq /= 300
    return round(fixfreq, 3)

def fix_4op_dx7(mode4op, rng4op, crs4op, fine4op):
    f = fix_4op(mode4op, rng4op, crs4op, fine4op) + 0.00001
    dd = 80000
    coarse = 0
    fine = 0
    for c in range(4):
        for fin in range(100):
            d = max(fix_dx7(c, fin), f)/min(fix_dx7(c, fin), f)
            if d < dd:
                dd = d
                coarse = c
                fine = fin
            if dd == 1:
                break
        if dd == 1:
            break
    return coarse, fine

def vmm2vmem(vmm):
    vmm = cleanvmm(vmm)
    vced = dx7.initvced()
    aced = dx7.initaced()
    vced[121] = 0

    alg4 = vmm[40]&7
    alg = algo[alg4]
    for op4 in range(4):
        op = alg[op4+1]
        egshift = (0, 35, 67, 83)[(vmm[2*op4+73]>>4)&3]
        rateshift = (99-egshift)/99.0
        vced[21*(5-op)+0] = int(r1[vmm[10*op4+0]&31]*rateshift) #R1
        vced[21*(5-op)+1] = int(r2[vmm[10*op4+1]&31]*rateshift) #R2
        vced[21*(5-op)+2] = int(r3[vmm[10*op4+2]&31]*rateshift) #R3
        vced[21*(5-op)+3] = int(r4[vmm[10*op4+3]&15]*rateshift) #R4
        vced[21*(5-op)+4] = 99 #L1
        L2 = l2[vmm[10*op4+4]&15]
        vced[21*(5-op)+5] = int((L2/99.0) * (99-egshift) + egshift) #L2
        D2R = vmm[10*op4+2]&31
        if D2R == 0:
            L3 = L2
        else:
            L3 = 0
        # L3 = int(L2 * ((31-D2R)/31.0))
        vced[21*(5-op)+6] = int((L3/99.0) * (99-egshift) + egshift) #L3
        vced[21*(5-op)+7] = egshift #L4
        vced[21*(5-op)+8] = 15 # BP=C1
        vced[21*(5-op)+9] = 0 #LD
        vced[21*(5-op)+10] = vmm[10*op4+5]&127 #RD
        vced[21*(5-op)+11] = 0 #LC
        vced[21*(5-op)+12] = 1 #RC -EXP
        if vmm[10*op4+9]>>6 == 1: #LS sign V50
            vced[21*(5-op)+12] = 3 #RC +EXP
        krs=(1, 2, 4, 7)[(vmm[10*op4+9]&0b0011000)>>3]
        vced[21*(5-op)+13] = krs
        for n in range(4):
            if krs == 2:
                vced[21*(5-op)+n] = min(99, vced[21*(5-op)+n] + 2)
                #r += 2
            elif krs == 3:
                vced[21*(5-op)+n] = min(99, vced[21*(5-op)+n] + 6)
                #r += 3
        ams = ((vmm[10*op4+6]>>6)&1) * ((vmm[45]>>2)&3) #AME * AMS
        vced[21*(5-op)+14] = ams #AMS

        if (vmm[10*op4+9]>>5)&1 == 1: #reversed KVS
            kvs = 0
        else:
            kvs = vmm[10*op4+6]&7 #TS
        vced[21*(5-op)+15] = kvs #TS
        vced[21*(5-op)] = min(99, vced[21*(5-op)] + (0,1,1,2,2,2,2,2)[kvs]) #R1 correction
 
        vced[21*(5-op)+16] = out[vmm[10*op4+7]&127] #TL
        vced[21*(5-op)+17] = (vmm[2*op4+73]>>3)&1 #PM (crs/fix)

        coarse4op = vmm[10*op4+8]&63
        fine4op = vmm[2*op4+74]&15
        mode4op = (vmm[2*op4+73]>>6)&1
        rng4op = vmm[2*op4+73]&7

        if (vmm[2*op4+73]>>3)&1 == 1:
            #FIXED FREQUENCY MODE
            vced[21*(5-op)+18] = fix_4op_dx7(mode4op, rng4op, coarse4op, fine4op)[0]
            vced[21*(5-op)+19] = fix_4op_dx7(mode4op, rng4op, coarse4op, fine4op)[1]
        else:
            vced[21*(5-op)+18] = freq_4op_dx7(coarse4op, fine4op)[0] #PC
            vced[21*(5-op)+19] = freq_4op_dx7(coarse4op, fine4op)[1] #PF
        

        PD = 4 + (vmm[10*op4+9]&7) #PD
        vced[21*(5-op)+20] = PD

        # aced[5-op] = SCM
        # ams = ((vmm[10*op4+6]>>6)&1) * ((vmm[45]>>2)&3) #AMS
        # ams = (0, 2, 4, 7)[ams]
        aced[11-op] = ams #AMS (DX7II)

    vced[126] = pr[vmm[67]&127] #PR1
    vced[127] = min(98, pr[vmm[68]&127]) #PR2
    vced[128] = 99 #PR3
    vced[129] = pr[vmm[69]&127] #PR4
    vced[130] = vmm[70]&127 #PL1
    vced[131] = vmm[71]&127 #PL2
    vced[132] = vmm[71]&127 #PL3
    vced[133] = vmm[72]&127 #PL4
    vced[134] = alg[0] #ALS
    vced[135] = (vmm[40]>>3)&7 #FBL
    vced[136] = (vmm[4]>>6)&1 #OPI (op sync)
    lfspeed = lfs[vmm[41]&127]
    vced[137] = dxcommon.closeto(lfspeed, dx7.lfs, True) #LFS
    vced[138] = lfd(lfdtime(vmm[42] & 127)) #LFD
    vced[139] = vmm[43]&127 #LPMD
    vced[140] = dxcommon.closeto(amd[vmm[44]&127], dx7.amd, True)  #LAMD
    vced[141] = (vmm[40]>>6)&1 #LFKS
    vced[142] = (2, 3, 0, 5)[vmm[45]&3] #LFW Saw-up, Sqr, Tri, S/H
    vced[143] = ((vmm[45]>>4)&7) #LPMS
    PMS_FACTOR = pms_factor[vced[143]]
    vced[139] = int(vced[139] * PMS_FACTOR)
    vced[144] = vmm[46]&63 #TRNP
    for i in range(10): #VOICENAME
        vced[145+i] = max(32, vmm[57+i]&127)

    #aced[12] = PEGR
    #aced[13] = LTGR
    #aced[14] = VPSW
    
    #aced[15] = PMOD+UNISON
    
    aced[16] = vmm[47]&15 #PBR
    #aced[17] = PBS
    #aced[18] = PBM
    
    #aced[19] = RNDP
    
    #aced[20] = PQRM
    #aced[21] = PQNT
    #aced[22] = POS
    
    aced[23] = int((vmm[51]&127) * PMS_FACTOR) #MWPM
    aced[24] = vmm[52]&127 #MWAM
    #aced[25] = MWEB
    
    aced[26] = int((vmm[82]&127) * PMS_FACTOR) # FC1PM
    aced[27] = vmm[83]&127 # FC1AM
    #aced[28] = FC1EB
    aced[29] = vmm[50]&127 #FC1VL

    aced[39] = int((vmm[82]&127) * PMS_FACTOR) #FC2PM 
    aced[40] = vmm[83]&127 #FC2AM
    #aced[41] = FC2EB
    aced[42] = vmm[50]&127 #FC2VL
   
    aced[30] = int((vmm[53]&127) * PMS_FACTOR) #BCPM
    aced[31] = vmm[54]&127 #BCAM
    aced[32] = vmm[56]&127 #BCEB
    aced[33] = vmm[55]&127 #BCPB

    aced[34] = int((vmm[84]&127) * PMS_FACTOR) #ATPM
    aced[35] = vmm[85]&127 #ATAM
    aced[36] = vmm[87]&127 #ATEB
    if vmm[86]<51:
        atpb=(vmm[86]&127)+50
    else:
        atpb=(vmm[86]&127)-51
    aced[37] = atpb #ATPB
    
    #aced[38] = PGRS
    
    aced[43] = int((aced[43]&127) * PMS_FACTOR) #MCPM
    #aced[44] = MCAM
    #aced[45] = MCEB
    #aced[46] = MCVL

    #aced[47] = UDTN

    #aced[48] = FCCS1

    return dx7.vced2vmem(vced), dx7.aced2amem(aced)

def cleanvmm(vmm):
    if vmm == 128*[vmm[0]]:
        return initvmm()
    for i in range(57, 67):
        if vmm[i] not in range(32, 128):
            vmm[i] = 32

    if vmm[57:67] == 10*[32]:
        return initvmm()

    for i in range(128):
        vmm[i] = min(maxvmm[i], vmm[i])

    for i in (3, 13, 23, 33):
        vmm[i] = max(1, vmm[i])
    return vmm

def vmm2vcd(vmm):
    for i in range(256):  #this will clean up some empty or corrupted patches
        if vmm == 128*[i]:
            vmm = 128*[0]
            break
    vmm = cleanvmm(vmm)
    vcd = initvcd()
    acd = initacd()
    acd2 = initacd2()
    acd3 = initacd3()
    efeds = initefeds()
    delay = initdelay()

    for op in range(4):
        vcd[0+13*op] = vmm[0+10*op]&31
        vcd[1+13*op] = vmm[1+10*op]&31
        vcd[2+13*op] = vmm[2+10*op]&31
        vcd[3+13*op] = max(1, vmm[3+10*op]&15)
        vcd[4+13*op] = vmm[4+10*op]&15
        vcd[5+13*op] = vmm[5+10*op]&127
        vcd[6+13*op] = (vmm[9+10*op]>>3)&3
        vcd[7+13*op] = (vmm[6+10*op]>>3)&7
        vcd[8+13*op] = (vmm[6+10*op]>>6)&1
        KVS1 = vmm[6+10*op]&7
        KVS2 = (vmm[9+10*op]>>5)&1
        vcd[9+13*op] = KVS1 + 8*KVS2
        vcd[10+13*op] = vmm[7+10*op]&127
        vcd[11+13*op] = vmm[8+10*op]&63
        vcd[12+13*op] = vmm[9+10*op]&7
        
        acd[0+5*op] = (vmm[73+2*op]>>3)&1
        acd[1+5*op] = vmm[73+2*op]&7
        acd[2+5*op] = vmm[74+2*op]&15
        acd[3+5*op] = (vmm[74+2*op]>>4)&7
        acd[4+5*op] = (vmm[73+2*op]>>4)&3
        
        acd2[4+op] = (vmm[73+2*op]>>6)&1

    vcd[52] = vmm[40]&7
    vcd[53] = (vmm[40]>>3)&7
    vcd[54:58] = vmm[41:45]
    vcd[58] = (vmm[40]>>6)&1
    vcd[59] = vmm[45]&3
    vcd[60] = (vmm[45]>>4)&7
    vcd[61] = (vmm[45]>>2)&7
    vcd[62] = vmm[46]&63
    vcd[63] = (vmm[48]>>3)&1
    vcd[64] = vmm[47]&15
    vcd[65] = vmm[48]&1
    vcd[66] = vmm[49]&127
    vcd[67] = vmm[50]&127
    vcd[68] = (vmm[48]>>2)&1
    vcd[69] = (vmm[48]>>1)&1
    vcd[70] = (vmm[48]>>4)&1
    vcd[71:93] = vmm[51:73]

    acd[19] = 0
    acd[20] = vmm[81]&7
    acd[21] = vmm[82]&127
    acd[22] = vmm[83]&127

    acd2[:4] = vmm[84:88]
    if vmm[86]>50:
        acd2[2] -= 51
    else:
        acd2[2] += 50
    
    b0 = (vmm[9]>>6)&1
    b1 = (vmm[29]>>5)&2
    b2 = (vmm[19]>>4)&4
    b3 = (vmm[39]>>3)&8
    acd2[8] = b0+b1+b2+b3

    acd3[:7] = vmm[94:101]

    efeds[:3] = vmm[91:94]

    delay[0] = (vmm[90]>>1)&1
    delay[1] = vmm[90]&1

    return vcd, acd, acd2, acd3, efeds, delay

def voicename(vmm):
    voicename = ''
    for i in range(57, 67):
        voicename += chr(vmm[i])
    return voicename

def signed(i):
    if i<0:
        return str(i)
    else:
        return '+' + str(i)

def vmm2freq(vmm, op):
    vcd, acd, acd2, acd3, efeds, delay = vmm2vcd(vmm)
    crs = vcd[(50,24,37,11)[op]]
    fin = acd[(17,7,12,2)[op]]
    fix = acd[(15,5,10,0)[op]]
    fixrg = acd[(16,6,11,1)[op]]
    fixrgm = acd2[7-op]
    if fix:
        f = "{}f".format(round(fix_4op(fixrgm, fixrg, crs, fin), 2))
    else:
        f = "{}r".format(round(freq_4op[16*crs + fin], 2))
    return f

def vmm2txt(vmm, yamaha='tx81z'):
    vcd, acd, acd2, acd3, efeds, delay = vmm2vcd(vmm)
    
    vcdn = ('AR', 'D1R', 'D2R', 'RR', 'D1L', 'LS', 'RS', 'EBS', 'AME', 'KVS', 'OUT', 'CRS', 'DET')*4
    vcdn += ('ALG', 'FBL', 'LFS', 'LFD', 'PMD', 'AMD', 'SYNC', 'LFW', 'PMS', 'AMS', 'TRPS', 
            'MONO', 'PBR', 'PORMOD', 'PORT', 'FC VOL', 'SUS', 'POR', 'CHORUS (dx21)', 
            'MW PITCH', 'MW AMPLI', 'BC PITCH', 'BC AMPLI', 'BC P.BIAS', 'BC E.BIAS', 
            'VOICE NAME 1', 'VOICE NAME 2', 'VOICE NAME 3', 'VOICE NAME 4', 'VOICE NAME 5', 
            'VOICE NAME 6', 'VOICE NAME 7', 'VOICE NAME 8', 'VOICE NAME 9', 'VOICE NAME 10', 
            'PR1', 'PR2', 'PR3', 'PL1', 'PL2', 'PL3')

    s = 'VCED parameters:      VOICE NAME = "{}"\n'.format(voicename(vmm))
    s += '====================================================\n'
    s += 'OP1      OP2      OP3      OP4'.rjust(52)+'\n'
    #s += 'Frequency      : {:>8} {:>8} {:>8} {:>8}\n'.format(vmm2freq(vmm, 0), vmm2freq(vmm, 1), vmm2freq(vmm, 2), vmm2freq(vmm, 3))
    Oo = ('Off', 'On')
    for i in range(13):
        if vcdn[i] == 'DET':
            s += 'Frequency      : {:>8} {:>8} {:>8} {:>8}\n'.format(vmm2freq(vmm, 0), vmm2freq(vmm, 1), vmm2freq(vmm, 2), vmm2freq(vmm, 3))
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(vcdn[i], signed(vcd[i+39]-3), signed(vcd[i+13]-3), signed(vcd[i+26]-3), signed(vcd[i]-3))
        elif vcdn[i] == 'KVS':
            for n in (0, 13, 26, 39):
                if vcd[i+n] > 7: vcd[i+n]-=15
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(vcdn[i], signed(vcd[i+39]), signed(vcd[i+13]), signed(vcd[i+26]), signed(vcd[i]))
        elif vcdn[i] in ('AME'):
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(vcdn[i], 
                    Oo[vcd[i+39]], Oo[vcd[i+13]], Oo[vcd[i+26]], Oo[vcd[i]])
        else:
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(vcdn[i], vcd[i+39], vcd[i+13], vcd[i+26], vcd[i])
    s += '\n'
    for i in range(52, 87):
        if vcdn[i] == 'TRPS':
            s += '{:14} : {:>8}\n'.format(vcdn[i], signed(vcd[i] - 24))
        elif vcdn[i] == 'ALG':
            s += '{:14} : {:>8}\n'.format(vcdn[i], vcd[i] + 1 )
        elif vcdn[i] == 'LFW':
            s += '{:14} : {:>8}\n'.format(vcdn[i], ('Saw Up', 'Square', 'Triangle', 'S/Hold')[vcd[i]])
        elif vcdn[i] in ('SYN', 'CHORUS (dx21)'):
            s += '{:14} : {:>8}\n'.format(vcdn[i], Oo[vcd[i]])
        elif vcdn[i] == 'MONO':
            mono = ('Poly', 'Mono')
            s += '{:14} : {:>8}\n'.format(vcdn[i], mono[vcd[i]])
        elif vcdn[i] == 'PORMOD':
            pormod = ('Full', 'Fing')
            s += '{:14} : {:>8}\n'.format(vcdn[i], pormod[vcd[i]])
        elif vcdn[i] in ('BC P.BIAS', 'PL1', 'PL2', 'PL3'):
            s += '{:14} : {:>8}\n'.format(vcdn[i], signed(vcd[i] - 50))
        elif 'VOICE NAME' in vcdn[i]:
            pass
        else:
            s += '{:14} : {:>8}\n'.format(vcdn[i], vcd[i])

    if yamaha in ('all', 'v50', 'dx11', 'v2', 'wt11', 'dx21'):
        for i in range(87, 93):
            s += '{:14} : {:8}\n'.format(vcdn[i], vcd[i])
    s += '\n'

    acdn = ('FREQ MODE', 'FREQ FIXRG', 'FREQ FINE', 'OSW', 'EGSFT')*4
    acdn += ('REV', 'FC PITCH', 'FC AMPLI')

    if yamaha not in ('dx100', 'dx27', 'dx27s', 'dx21'):
        s += 'ACED parameters\n'
        s += '===============\n'
        for i in range(5):
            if acdn[i] == 'OSW':
                s += '{:14} :       W{}       W{}       W{}       W{}\n'.format(acdn[i], acd[i+15]+1, acd[i+5]+1, acd[i+10]+1, acd[i]+1)
            elif acdn[i] == 'FREQ MODE':
                fix = ('Ratio', 'Fix')
                s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(acdn[i], 
                        fix[acd[i+15]], fix[acd[i+5]], fix[acd[i+10]], fix[acd[i]])
            elif acdn[i] == 'EGSFT':
                egsft = ('Off', '48dB', '24dB', '12dB')
                s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(acdn[i], 
                        egsft[acd[i+15]], egsft[acd[i+5]], egsft[acd[i+10]], egsft[acd[i]])
            elif acdn[i] == "FREQ FIXRG":
                rng = ('255Hz', '510Hz', '1KHz', '2kHz', '4KHz', '8KHz', '16KHz', '32KHz'), ('1Hz', '2Hz', '4Hz', '7Hz', '14Hz', '25Hz', '50Hz', '100Hz') 
                s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(acdn[i], rng[acd2[7]][acd[i+15]], rng[acd2[5]][acd[i+5]], rng[acd2[6]][acd[i+10]], rng[acd2[4]][acd[i]])
            else:
                s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format(acdn[i], acd[i+15], acd[i+5], acd[i+10], acd[i])
        for i in range(20, 23):
            s += '{:14} : {:>8}\n'.format(acdn[i], acd[i])
        s += '\n'

    if yamaha in ('dx11', 'v2', 'v50', 'ys100', 'ys200', 'tq5', 'b200', 'wt11', 'all'):
        s += 'ACED2 parameters\n'
        s += '================\n'
        acd2n = ('AT PITCH', 'AT AMPLI', 'AT P.BIAS', 'AT EG.BIAS')
        for i in range(4):
            if acd2n[i] == 'AT P.BIAS':
                s += '{:14} : {:>8}\n'.format(acd2n[i], signed(acd2[i] - 50))
            else:
                s += '{:14} : {:>8}\n'.format(acd2n[i], acd2[i])
        if yamaha in ('v50', 'all'):
            hilo = ('Hi', 'Lo')
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format('FIX RANGE MODE', hilo[acd2[7]], hilo[acd2[5]], hilo[acd2[6]], hilo[acd2[4]])
            lss = ('Normal', 'Invert')
            s += '{:14} : {:>8} {:>8} {:>8} {:>8}\n'.format('LS SIGN', lss[(acd2[8]>>3)&1], lss[(acd2[8]>>2)&1], lss[(acd2[8]>>1)&1], lss[acd2[8]&1])
        s += '\n'

    fx = ('Off', 'Reverb Hall', 'Reverb Room', 'Reverb Plate',
            'Delay', 'Delay L/R', 'Stereo Echo', 'Distortion Rev.', 
            'Distortion Echo', 'Gate Reverb', 'Reverse Gate', 'Early Ref',
            'Tone Control', 'Delay & Reverb', 'Delay L/R & Rev.', 'Dist. & Delay',
            'Church', 'Club', 'Stage', 'Bath Room',
            'Metal', 'Tunnel', 'Doubler 1', 'Doubler 2',
            'Feed Back Gate', 'F. Back Reverse', 'Feed Back E/R', 'Delay & Tone1',
            'Dly L/R & Tone1', 'Tone Control 2', 'Delay & Tone2', 'Dly L/R & Tone2')

    if yamaha in ('v50', 'all'):
        s += 'ACED3 parameters\n'
        s += '================\n'
        acd3n = ('EFCT SEL', 'BALANCE', 'OUT LEVEL', 'STEREO MIX', 'EFCT param1', 'EFCT param2', 'EFCT param3')
        for i in range(7):
            if acd3n[i] == 'EFCT SEL':
                s += '{:14} : {:>8}\n'.format(acd3n[i], fx[acd3[i]])
            elif acd3n[i] in ('BALANCE', 'OUT LEVEL'):
                s += '{:14} : {:>7}%\n'.format(acd3n[i], acd3[i])
            else:
                s += '{:14} : {:>8}\n'.format(acd3n[i], acd3[i])
        s += '\n'

    if yamaha in ('ys100', 'ys200', 'tq5', 'b200', 'all'):
        s += 'EFEDS parameters\n'
        s += '================\n'
        efedsn = ('EFFECT PRESET', 'EFFECT TIME', 'EFFECT BALANCE')
        for i in range(len(efeds)):
            if efedsn[i] == 'EFFECT PRESET':
                s += '{:14} : {:>8}\n'.format(efedsn[i], fx[efeds[i]])
            elif efedsn[i] == 'EFFECT BALANCE':
                s += '{:14} : {:>7}%\n'.format(efedsn[i], efeds[i])
            else:
                s += '{:14} : {:>8}\n'.format(efedsn[i], efeds[i])
        s += '\n'

    if yamaha in ('ds55', 'all'):
        s += 'DELAY parameters\n'
        s += '================\n'
        s += 'Dly Off/On     : {:>8}\n'.format(Oo[delay[0]])
        s += 'Dly Short/Long : {:>8}\n'.format(('Short', 'Long')[delay[1]])
    S=[]
    for k in s:
        S.append(ord(k))
    return S

def v50_ys(vmm):
    if (vmm[91] == 0) and (vmm[94] != 0):
        if vmm[94] in range(1, 11):
            vmm[91] = vmm[94]
        else:
            vmm[91] = 0
        vmm[92] = vmm[98]
        if vmm[97] == 1:
            vmm[93] = int(vmm[96]*vmm[95]/(100.+vmm[96]))
        else:
            vmm[93] = min(99, vmm[95])
    return vmm

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

def carrier(alg, op):
    mc = ((1,0,0,0), (1,0,0,0), (1,0,0,0), (1,0,0,0),
            (1,0,1,0), (1,1,1,0), (1,1,1,0), (1,1,1,1))
    return (mc[alg][op] == 1)

def steinb2vmm(namedata, data):
    txdat = initvmm()
    for op in range(4):
        txdat[0+10*op:6+10*op] = data[13*op:13*op+6]
        txdat[6+10*op:9+10*op] = data[13*op+8:13*op+11]
        txdat[9+10*op] = ((data[13*op+11]&3)<<3) + (data[13*op+12]&7)

        EGSFT = data[5*op+83]&3
        FIX = data[5*op+84]&1
        FIXRG = data[5*op+85]&7
        OSW = data[5*op+86]&7
        FINE = data[5*op+87]&15
        txdat[73+2*op] = (EGSFT<<4)+(FIX<<3)+FIXRG
        txdat[74+2*op] = (OSW<<4)+FINE

    SY = data[52]&1
    FBL = data[53]&7
    ALG = data[54]&7
    txdat[40] = (SY<<6)+(FBL<<3)+ALG

    txdat[41:45] = data[55:59]

    PMS = data[59]&7
    AMS = data[60]&3
    LFW = data[61]&3
    txdat[45] = (PMS<<4)+(AMS<<2)+LFW

    txdat[46:48] = data[62:64]

    CH = data[64]&1
    MO = data[65]&1
    SU = data[66]&1
    PO = data[67]&1
    PM = data[68]&1
    txdat[48] = (CH<<4)+(MO<<3)+(SU<<2)+(PO<<1)+PM

    txdat[49:57] = data[69:77]
    txdat[57:67] = namedata[:10]
    txdat[67:73] = data[77:83]
            
    txdat[81:84] = data[103:106] #REV, FC PITCH/AMPLI

    txdat[84:88] = data[110:114] #AT PITCH/AMPLI/P.BIAS/EG.BIAS
    if txdat[86]<50:
        txdat[86] += 51
    else:
        txdat[86] -= 50
            
    return txdat

def raw_check(vmm):
    for k in range(57, 67):
        if 31 < vmm[k] < 128:
            return True
        else:
            return False


