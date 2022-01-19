#!/usr/bin/env python3
import os
import sys

import tkinter
from tkinter.constants import W

CFG='dxtxmidi.cfg'
IN = os.getenv('MID_IN')
OUT = os.getenv('MID_OUT')

if os.path.exists(CFG):
    with open(CFG, 'r') as f:
        for line in f.readlines():
            if 'MID_IN' in line:
                try: IN = line.split('=')[1].strip()
                except: pass
            if 'MID_OUT' in line:
                try: OUT = line.split('=')[1].strip()
                except: pass

import rtmidi
class Midiconf:
    def __init__(self):
        midiout = rtmidi.MidiOut()
        midiin = rtmidi.MidiIn()

        self.master = tkinter.Tk()
        self.master.title('MIDI I/O port selection')

        label1 = tkinter.Label(self.master, text="MID_IN:")
        label1.grid(row=1, column=1, padx=4, pady=4, sticky=W)
        self.mi = tkinter.Spinbox(self.master, values=[IN]+midiin.get_ports(), wrap=True)
        self.mi.grid(row=1, column=2, columnspan=2, padx=4, pady=4)

        label2 = tkinter.Label(self.master, text="MID_OUT:")
        label2.grid(row=2, column=1, padx=4, pady=4, sticky=W)
        self.mo = tkinter.Spinbox(self.master, values=[OUT]+midiout.get_ports(), wrap=True)
        self.mo.grid(row=2, column=2, columnspan=2, padx=4, pady=4)
        
        button = tkinter.Button(self.master, text='OK', width=6, command=self.get_ok)
        button.grid(row=3, column=2, padx=4, pady=4)
        
        button = tkinter.Button(self.master, text='Cancel', width=6, command=self.master.destroy)
        button.grid(row=3, column=3, padx=4, pady=4)
        return

    def get_ok(self):
        mid_in_msg = 'MID_IN = {}\n'.format(self.mi.get())
        mid_out_msg = 'MID_OUT = {}\n'.format(self.mo.get())
        with open('dxtxmidi.cfg', 'w') as f:
            f.write(mid_in_msg)
            f.write(mid_out_msg)
        self.master.destroy()
        print (mid_in_msg.strip())
        print (mid_out_msg.strip())
        print ('written to file "dxtxmidi.cfg"')
        return

    def get_cancel(self):
        self.master.destroy()
        return

Midiconf()
tkinter.mainloop()
sys.exit(0)



