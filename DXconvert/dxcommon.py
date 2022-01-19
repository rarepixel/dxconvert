import os
import sys
import random

#these are just initial values
MID_OUT = "MIDI" 
MID_IN = "MIDI"

# Don't change anything below this line
PROGRAMVERSION = "3.1.6"
PROGRAMDATE = "20210618"

try:
    import rtmidi
    import time
    ENABLE_MIDI = True
except ImportError:
    ENABLE_MIDI = False

CFG = 'dxtxmidi.cfg'
for pth in sys.path:
    s = os.path.join(pth, CFG)
    if os.path.exists(s):
        CFG = s
        break

LINUX = False
if ENABLE_MIDI and rtmidi.API_LINUX_ALSA in rtmidi.get_compiled_api():
    LINUX = True

def validfname(fn):
    ALLOWED_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
    newname = ''
    for k in fn:
        if k in ALLOWED_CHARACTERS:
            newname += k
        else:
            newname += '_'
    if newname in ('CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'):
        newname += '_'
    return newname


def list2string(l):
    s = ''
    for k in l:
        if k not in range(32, 128):
            k = 32
        s += chr(k)
    return s

def string2list(s):
    l = []
    for k in s:
        l.append(ord(k))
    return l

def range2list(s):
    l = []
    s = s.split(',')
    for k in s:
        if '-' in k:
            start = max(1, int(k.split('-')[0]))
            end = int(k.split('-')[1]) + 1
            l += range(start, end)
        else:
            l.append(max(1, int(k)))
    return l

def tl2out(tl):
    out = []
    for i in range(80):
        out.append(99-i)
    out += [20, 19, 18, 18, 17, 16, 15, 15, 14, 14,
            13, 13, 12, 12, 11, 11, 10, 10, 9, 9,
            8, 8, 7, 7, 6, 6, 5, 5, 5, 4,
            4, 4, 4, 3, 3, 3, 3, 2, 2, 2,
            2, 1, 1, 1, 1, 0, 0, 0]
    return out[tl]

def out2tl(out):
    tl = [127,122,118,114,110,107,104,102,100,98,96,94,92,90,88,86,85,84,82,81]
    for i in range(20, 100):
        tl.append(99-i)
    return tl[out]

def checksum(data):
    return (128-sum(data)&127)%128

def dxrandom(data, size=128):
    # thanks Renata Dokmanovic
    print ("Randomizing data")
    random.seed()
    n = len(data)//size
    newdata = []
    for v in range(n):
        for p in range(size):
            newdata.append(data[size * random.randrange(n) + p])
    return newdata

def file2names(infile, len=10):
    names = []
    with open(infile, 'r') as f:
        lines = f.readlines()
    for l in lines:
        if l.strip() != '':
            name = l.ljust(10)
            names += string2list(name)
    return names

def nr2note(nr, C3 = 60):
    scl = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    n = (nr - C3) % 12
    i = (nr - C3) // 12 
    return scl[n] + str(i + 3) 


def id_mid_out(mid_out=MID_OUT):
    mid_out_id = -1
    midi_out = rtmidi.MidiOut()
    for i in range(midi_out.get_port_count()):
        n = midi_out.get_port_name(i)
        if mid_out.lower() in n.lower():
            mid_out_id = i
            break
    del midi_out
    return mid_out_id

def id_mid_in(mid_in = MID_IN):
    mid_in_id = -1
    midi_in = rtmidi.MidiIn()
    for i in range(midi_in.get_port_count()):
        n = midi_in.get_port_name(i)
        if mid_in.lower() in n.lower():
            mid_in_id = i
            break
    del midi_in
    return mid_in_id

def data2midi(data, mid_out = MID_OUT, buffersize=512, buffertime=0.1, syxtime=1.0):
    midiout = rtmidi.MidiOut()
    mid_out_id = id_mid_out(mid_out)
    if mid_out_id == -1:
        midiout.close_port()
        del midiout
        print ("No MIDI Out")
        return False
    else:
        midiout.open_port(mid_out_id)
    
    dd = []
    if LINUX:
        for i in range(len(data)):
            midiout.send_message([data[i]])
            if data[i] == 0xf7:
                time.sleep(syxtime)
            elif (i % buffersize) == (buffersize - 1):
                time.sleep(buffertime)

    else:
        for i in range(len(data)):
            dd.append(data[i])
            if (data[i] == 0xf7):
                midiout.send_message(dd)
                time.sleep(syxtime)
                dd = []
    
    midiout.close_port()
    del midiout
    return True

def req2data(req, mid_in = MID_IN, mid_out = MID_OUT):
    mid_in_id = id_mid_in(mid_in)
    mid_out_id = id_mid_out(mid_out)
    midiin = rtmidi.MidiIn()
    midiin.ignore_types(False, True, True)
    if mid_in_id == -1:
        midiin.close_port()
        del midiin
        print ("No MIDI In")
        return [], 0
    else:
        midiin.open_port(mid_in_id)
    
    requests=[]
    rq=[]
    for i in req:
        rq.append(i)
        if i==0xf7:
            requests.append(rq)
            rq=[]
    
    data = []
    for req in requests:
        if requests.index(req) != 0: 
            if req[:3] == [0xf0, 0x43, 0x10]:
                # Bankselect messages for DX7II, TX802, YS200
                time.sleep(5)
        data2midi(req, mid_out)
        if req[:3] != [0xf0, 0x43, 0x10]:
            # try to fetch data
            print ("Requesting data")
            t0 = time.time()
            while time.time()-t0 < 5:
                d = midiin.get_message()
                if d != None:
                    data += d[0]
                    t0 = time.time()

    midiin.close_port()
    del midiin
    return data, len(data)

def read_cfg(cfg = CFG):
    IN = ''
    OUT = ''
    if os.getenv('MID_IN'):
        IN = os.getenv('MID_IN')
    if os.getenv('MID_OUT'):
        OUT = os.getenv('MID_OUT')
    if os.path.exists(cfg):
        if os.path.exists(CFG):
            with open(CFG, 'r') as f:
                for line in f.readlines():
                    if 'MID_IN' in line:
                        try: IN = line.split('=')[1].strip()
                        except: pass
                    if 'MID_OUT' in line:
                        try: OUT = line.split('=')[1].strip()
                        except: pass
    return IN, OUT

def closeto(value, table, expo=False):
    if value in table:
        return table.index(value)
    minval = min(table)
    if value < minval:
        return table.index(minval)
    maxval = max(table)
    if value > maxval:
        return table.index(maxval)
    srtable = sorted(table)
    for i in range(len(table) - 1):
        hi = srtable[i+1]
        lo = srtable[i]
        if lo < value < hi:
            if expo:
                center = (hi * lo) ** 0.5
            else:
                center = (hi + lo) / 2.
            if value <= center:
                return table.index(lo)
            elif value > center:
                return table.index(hi)
    return 0

