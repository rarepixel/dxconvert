#!/usr/bin/env python3
"""
txconvert-gui.py

(c)2020 Martin Tarenskeen <m.tarenskeenATkpnmailDOTnl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

__license__ = 'GPL v3'

import sys
import os

import tkinter
from tkinter.constants import *
from tkinter.scrolledtext import ScrolledText
import tkinter.filedialog 
import tkinter.messagebox

try:
    from idlelib.ToolTip import ToolTip
    WITH_TOOLTIP = True
except ImportError:
    WITH_TOOLTIP = False
from DXconvert import TXC
from DXconvert import dxcommon, dxcommongui

PROGRAMNAME=TXC.PROGRAMNAME
PROGRAMVERSION=dxcommon.PROGRAMVERSION
PROGRAMDATE=dxcommon.PROGRAMDATE

LOGO='DXconvert/txconvert.gif'
HELP='DXconvert/txconvert.help'
MIDILOGO='DXconvert/midi.gif'
for p in sys.path:
    _logo = os.path.join(p, 'DXconvert/txconvert.gif')
    if os.path.exists(_logo):
        LOGO=_logo
        break
for p in sys.path:
    _help = os.path.join(p, 'DXconvert/txconvert.help')
    if os.path.exists(_help):
        HELP=_help
        break
for p in sys.path:
    _midilogo = os.path.join(p, 'DXconvert/midi.gif')
    if os.path.exists(_midilogo):
        MIDILOGO=_midilogo
        break

############ GUI ##############

class txConvertDialog(tkinter.Frame):
    def __init__(self, root):
        tkinter.Frame.__init__(self, root, border=15)
        self.status = tkinter.Label(self, text='Select file(s) for conversion')
        self.status.pack(fill=X, expand=1)
        body = tkinter.Frame(self)
        body.pack(fill=X, expand=1)
        sticky = E + W
        body.grid_columnconfigure(1, weight=2)

        ROW=1
        COLUMN=1
        tkinter.Label(body, text='Input file(s):').grid(row=ROW, sticky=W)
        self.infile = tkinter.Entry(body, width=50)
        self.infile.grid(row=ROW, column=COLUMN, columnspan=5, sticky=W, padx=5, pady=5)
        self.tooltip(self.infile, "Enter input filename(s)")

        infile_button = tkinter.Button(body, text="...", command=self.get_infile)
        infile_button.grid(row=ROW, column=5, padx=5, pady=5)
        self.tooltip(infile_button, "Open fileselector")

        ROW+=1
        tkinter.Label(body, text='Output file:').grid(row=ROW, sticky=W)
        self.outfile = tkinter.Entry(body, width=50)
        self.outfile.grid(row=ROW, column=COLUMN, columnspan=5, sticky=W, pady=5, padx=5)
        self.tooltip(self.outfile, "Enter output filename")
        
        output_button = tkinter.Button(body, text="...", command=self.get_outfile)
        output_button.grid(row=ROW, column=5, padx=5, pady=5)
        self.tooltip(output_button, "Open fileselector")

        ROW+=1
        tkinter.Label(body, text='Target synth:').grid(row=ROW, sticky=W)
        SYNTHS = ('DX100', 'DX27', 'DX21', 'TX81Z', 'WT11', 'DX11', 'V2', 'FB01',
                    'YS100', 'YS200', 'TQ5', 'B200', 'DS55', 'V50', 'VOPM', 'RefaceDX')
        self.yamaha = tkinter.StringVar()
        self.yamaha.set('TX81Z')
        yamaha_om = tkinter.OptionMenu(body, self.yamaha, *SYNTHS)
        yamaha_om.grid(row=ROW, column=COLUMN, pady=5, padx=5, sticky=W)
        self.tooltip(yamaha_om, "Select target synth")

        ROW+=1
        tkinter.Label(body, text='Options:').grid(row=ROW, sticky=W)
       
        ROW = 4
        COLUMN = 1
        self.check=tkinter.BooleanVar()
        check_button = tkinter.Checkbutton(body, text="--check", variable=self.check)
        check_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(check_button, "Check SysEx checksum before import")

        ROW += 1
        self.sort=tkinter.BooleanVar()
        sort_button = tkinter.Checkbutton(body, text="--sort", variable=self.sort)
        sort_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(sort_button, "Sort patches by voicename (case-insensitive)")

        ROW += 1
        self.sort2 = tkinter.BooleanVar()
        sort2_button = tkinter.Checkbutton(body, text="--sort2", variable=self.sort2)
        sort2_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(sort2_button, "Sort patches by voicename (case-sensitive)")

        ROW += 1
        self.nodupes = tkinter.BooleanVar()
        nodupes_button = tkinter.Checkbutton(body, text="--nodupes", variable=self.nodupes)
        nodupes_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nodupes_button, "Remove duplicates")

        ROW += 1
        self.nodupes2 = tkinter.BooleanVar()
        nodupes2_button = tkinter.Checkbutton(body, text="--nodupes2", variable=self.nodupes2)
        nodupes2_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nodupes2_button, "Remove duplicates, but ignore voicenames")
 
        COLUMN = 2
        ROW = 4
        self.nosilence = tkinter.BooleanVar()
        nosilence_button = tkinter.Checkbutton(body, text="--nosilence", variable=self.nosilence)
        nosilence_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nosilence_button, "Remove patches that produce no sound")
        
        ROW += 1
        self.nosplit = tkinter.BooleanVar()
        nosplit_button = tkinter.Checkbutton(body, text="--nosplit", variable=self.nosplit)
        nosplit_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nosplit_button, "Save data in one single file")
        
        ROW += 1
        self.split = tkinter.BooleanVar()
        split_button = tkinter.Checkbutton(body, text="--split", variable=self.split)
        split_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(split_button, "Save each patch as a separate file")
        
        ROW += 1
        self.random = tkinter.BooleanVar()
        random_button = tkinter.Checkbutton(body, text="--random", variable=self.random)
        random_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(random_button, "Renata's Randomizer")
        
        ROW += 1
        self.bc2at = tkinter.BooleanVar()
        bc2at_button = tkinter.Checkbutton(body, text="--bc2at", variable=self.bc2at)
        bc2at_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(bc2at_button, "Copy BreathControl data to Aftertouch")
        
        ROW += 1
        self.bc = tkinter.BooleanVar()
        self.bc.set(True)
        bc_button = tkinter.Checkbutton(body, text="--breathcontrol", variable=self.bc)
        bc_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(bc_button, "Breathcontrol")
        
        ROW = 4
        COLUMN = 3

        select_label = tkinter.Label(body, text="--select RANGE:")
        select_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(select_label, 'Select patch RANGE to save (e.g. "2,4,7-12,18-32")')
        self.select = tkinter.Entry(body, width=8)
        self.select.grid(row=ROW, column=COLUMN+1, sticky=W)
        self.tooltip(self.select, 'Select patch RANGE to save (e.g. "2,4,7-12,18-32")')

        ROW += 1
        channel_label = tkinter.Label(body, text="--channel <1~16>:")
        channel_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(channel_label, "Midi channel in SysEx header")
        self.channel = tkinter.Entry(body, width=8)
        self.channel.grid(row=ROW, column=COLUMN+1, sticky=W)
        self.tooltip(self.channel, "Midi channel in SysEx header")
 
        ROW += 1
        offset_label = tkinter.Label(body, text="--offset <value>:")
        offset_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(offset_label, "Number of first or last bytes to ignore (+/-)")
        self.offset = tkinter.Entry(body, width=8)
        self.offset.grid(row=ROW, column=COLUMN+1, sticky=W)
        self.tooltip(self.offset, "Number of first or last bytes to ignore (+/-)")
         
        ROW += 1
        brightness_label = tkinter.Label(body, text='--brightness <value>: ')
        brightness_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(brightness_label, "Adjust global brightness (+/-VALUE)")
        self.txbrightness = tkinter.Entry(body, width=8)
        self.txbrightness.grid(row=ROW, column=COLUMN+1, columnspan=2, sticky=W)
        self.tooltip(self.txbrightness, "Adjust global brightness (+/-VALUE)")
       
        ROW += 1
        find_label = tkinter.Label(body, text='--find <string>: ')
        find_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(find_label, "Search for STRING in patchnames")
        self.txfind = tkinter.Entry(body, width=8)
        self.txfind.grid(row=ROW, column=COLUMN+1, columnspan=2, sticky=W)
        self.tooltip(self.txfind, "Search for STRING in patchnames")

        ROW += 1
        exclude_label = tkinter.Label(body, text='--exclude <string>: ')
        exclude_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(exclude_label, "Exclude if STRING is found in patchname")
        self.exclude = tkinter.Entry(body, width=8)
        self.exclude.grid(row=ROW, column=COLUMN+1, columnspan=2, sticky=W)
        self.tooltip(self.exclude, "Exclude if STRING is found in patchname")
 
        buttons = tkinter.Frame(self)
        buttons.pack()
        tkinter.Frame(buttons, width=15).pack(side=LEFT)

        help_button = tkinter.Button(
            buttons, text="Help?", width=8, activeforeground='blue', command=self.info)
        help_button.pack(side=LEFT, pady=15, padx=15)
        self.tooltip(help_button, "Show help")
        
        if os.path.exists(LOGO):
            picture = tkinter.PhotoImage(file=LOGO)
            convert_button = tkinter.Button(buttons, image=picture, width=100, height=45, command=self.convert)
            convert_button.picture = picture
            convert_button.pack(side=LEFT)
        else:
            convert_button = tkinter.Button(
                buttons, text="CONVERT!", width=8, fg='green', command=self.convert)
            convert_button.pack(side=LEFT, pady=15, padx=15)
        self.tooltip(convert_button, "Start txconvert!")

        if dxcommon.ENABLE_MIDI:
            self.mid_in = dxcommon.MID_IN
            self.mid_out = dxcommon.MID_OUT
            if os.getenv('MID_IN'):
                self.mid_in = os.getenv('MID_IN')
            self.mid_out = os.getenv('MID_OUT')
            if os.path.exists('dxtxmidi.cfg'):
                with open('dxtxmidi.cfg', 'r') as f:
                    for line in f.readlines():
                        l = line.split('=')
                        if l[0].strip() == 'MID_IN':
                            self.mid_in = l[1].strip()
                        if l[0].strip() == 'MID_OUT':
                            self.mid_out = l[1].strip()
        
            if os.path.exists(MIDILOGO):
                picture = tkinter.PhotoImage(file=MIDILOGO)
                midi_button = tkinter.Button(
                        buttons, image=picture, width=45, height=45, relief='flat', command=self.midiconf)
                midi_button.picture = picture
                midi_button.pack(side=LEFT, pady=15, padx=15)
            else:
                midi_button = tkinter.Button(
                        buttons, text="MIDI", width=8, command=self.midiconf)
                midi_button.pack(side=LEFT, pady=15, padx=15)
            self.tooltip(midi_button, "Configure MIDI")
        else:
            self.mid_in = None
            self.mid_out = None

        quit_button = tkinter.Button(
                buttons, text="Quit", width=8, activeforeground='red', command=self.quit)
        quit_button.pack(side=LEFT, pady=15, padx=15)
        self.tooltip(quit_button, "Quit program")
        return

    def tooltip(self, root, msg):
        if WITH_TOOLTIP:
            ToolTip(root, msg)
        else:
            pass
        
    def midiconf(self):
        dxcommongui.Midiconf()
        if os.path.exists('dxtxmidi.cfg'):
            with open('dxtxmidi.cfg', 'r') as f:
                for line in f.readlines():
                    l = line.split('=')
                    if l[0].strip() == 'MID_IN':
                        self.mid_in = l[1].strip()
                    if l[0].strip() == 'MID_OUT':
                        self.mid_out = l[1].strip()
        return


    def get_infile(self):
        infile = tkinter.filedialog.askopenfilenames(
            parent=None, title='Select file(s) to import')

        if infile:
            self.infile.delete(0, END)
            self.infile.insert(0, infile)
        return

    def get_outfile(self):
        outfile = tkinter.filedialog.asksaveasfilename(
            parent=None, title='Select filename/type to export') 


        if outfile:
            outfile = os.path.normpath(outfile)
            outfile_ext = os.path.splitext(outfile)[1]
            outfile_dir = os.path.split(outfile)[0]
            self.outfile.delete(0, END)
            self.outfile.insert(0, outfile)
        return

    def convert(self):
        self.status['text'] = '......'
        
        infile = self.infile.get()
        if not infile:
           message = 'No input file(s) selected'
           tkinter.messagebox.showerror("TXconvert-{}".format(PROGRAMVERSION), message)
           self.status['text'] = 'Select file(s) to import'
           return
       
        #Workaround for tkFileDialog.askopenfilesnames bug
        #Hopefully one day this will not be needed anymore
        if type(infile) == str:
            master = tkinter.Tk()
            master.withdraw()
            infile = master.tk.splitlist(infile)

        outfile = self.outfile.get()
        if not outfile:
            message = 'No output files selected'
            tkinter.messagebox.showerror("TXconvert-{}".format(PROGRAMVERSION), message)
            self.status['text'] = 'Select file(s) for conversion'
            return
        else:
            outfile_ext = os.path.splitext(outfile)[1]
            outfile_dir = os.path.split(outfile)[0]

        self.status['text'] = 'Reading ...'
        self.update()
        txdata = []
        channel = 0
        if self.offset.get():
            offset = offset.get()
        else:
            offset = '0'

        FB01 = False
        REFACE = False
        if self.yamaha.get():
            yamaha = self.yamaha.get().lower()
        if yamaha in ('dx100', 'dx27', 'dx27s'):
            split = 24
        elif yamaha in ('ds55', 'ys100', 'ys200', 'tq5', 'b200', 'v50'):
            split = 25
        elif yamaha == 'fb01':
            split = 48
            FB01 = True
        elif yamaha == 'vopm':
            split = 128
            FB01 = True
        elif yamaha == 'refacedx':
            REFACE = True
            split = 1
        else:
            split = 32
        if self.split.get():
            split = 1
        if self.nosplit.get() or (outfile == "MIDI"):
            split = sys.maxsize


        for inp in infile:
            inp = os.path.normpath(inp)
            if os.path.isfile(inp):
                txdat, channel = TXC.read(inp, offset, self.check.get(), yamaha, self.mid_in, self.mid_out)
                txdata += txdat
                self.status['text'] = 'Read {}'.format(inp)
                self.update()

        if self.channel.get():
            channel = min(15, max(0, int(self.channel.get())-1))

        if self.nodupes2.get() == True:
            nodupes2 = True
        else:
            nodupes2 = False


        if self.select.get():
            txdat = []
            for i in dxcommon.range2list(self.select.get()):
                if FB01:
                    txdat += txdata[64*(i-1):64*i]
                elif REFACE:
                    txdat += txdata[150*(i-1):150*i]
                else:
                    txdat += txdata[128*(i-1):128*i]
            txdata = txdat

        if self.txfind.get():
            self.status['text'] = 'Searching names ...'
            self.update()
            if FB01:
                txdata = TXC.fbfind(txdata, self.txfind.get())
            elif REFACE:
                txdata = TXC.rdxfind(txdata, self.txfind.get())
            else:
                txdata = TXC.txfind(txdata, self.txfind.get())

        if self.exclude.get():
            self.status['text'] = 'Excluding names ...'
            self.update()
            if FB01:
                txdata = TXC.exclude(txdata, self.exclude.get())
            elif REFACE:
                txdata = TXC.exclude(txdata, self.exclude.get())
            else:
                txdata = TXC.exclude(txdata, self.exclude.get())

        if self.txbrightness.get():
            self.status['text'] = 'Adjusting brightness ...'
            self.update()
            if FB01:
                txdata = TXC.fbbrightness(txdata, int(self.txbrightness.get()))
            elif REFACE:
                txdata = TXC.rdxbrightness(txdata, int(self.txbrightness.get()))
            else:
                txdata = TXC.txbrightness(txdata, int(self.txbrightness.get()))

        if self.random.get():
            self.status['text'] = 'Randomizing voices ...'
            self.update()
            if FB01:
                txdata = dxcommon.dxrandom(txdata, 64)
            elif REFACE:
                txdata = dxcommon.dxrandom(txdata, 150)
            else:
                txdata = dxcommon.dxrandom(txdata, 128)

        if self.bc2at.get():
            if (FB01 == False) and (REFACE == False):
                for i in range(len(txdata)//128):
                    txdata[128*i+84:128*i+88] = txdata[128*i+53:128*i+57]
                    if txdata[128*i+86]>50:
                        txdata[128*i+86] -= 51
                    else:
                        txdata[128*i+86] += 50

        if self.bc.get() == False:
            if (FB01 == False) and (REFACE == False):
                for i in range(len(txdata)//128):
                    txdata[128*i+53:128*i+57] = [0,0,50,0]

        if (self.nodupes.get() == True) or (self.nodupes2.get() == True):
            self.status['text'] = "Removing duplicates ..."
            self.update()
            if FB01:
                txdata = TXC.fbnodupes(txdata, nodupes2)
            elif REFACE:
                txdata = TXC.rdxnodupes(txdata, nodupes2)
            else:
                txdata = TXC.txnodupes(txdata, nodupes2)
        
        if self.nosilence.get() == True:
            if FB01:
                txdata = TXC.fbnosilence(txdata)
            if REFACE:
                txdata = TXC.rdxnosilence(txdata)
            else:
                txdata = TXC.txnosilence(txdata)
        
        if self.sort.get() == True:
            self.status['text'] = "Sorting voices by name ..."
            self.update()
            if FB01:
                txdata = TXC.fbsort(txdata)
            elif REFACE:
                txdata = TXC.rdxsort(txdata)
            else:
                txdata = TXC.txsort(txdata)

        elif self.sort2.get() == True:
            self.status['text'] = "Sorting voices by name ..."
            self.update()
            if FB01:
                txdata = TXC.fbsort(txdata, True)
            elif REFACE:
                txdata = TXC.rdxsort(txdata, True)
            else:
                txdata = TXC.txsort(txdata, True)
        if FB01:
            n = len(txdata)//64
        elif REFACE:
            n = len(txdata)//150
        else:
            n = len(txdata)//128
        if (split == 1) and (n > 1):
            if FB01:
                for i in range(len(txdata)//64):
                    outfile_name = dxcommon.list2string(txdata[64*i:64*i+7])
                    outfile_name = dxcommon.validfname(outfile_name)
                    Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
                
                    count = 0
                    while os.path.exists(Outfile):
                        count += 1
                        if count>1:
                            Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)
 
                    TXC.write(Outfile, txdata[64*i:64*(i+1)], channel, self.nosplit.get(), 1, yamaha, self.mid_out)
                message = "Ready. {} Patches written.".format(len(txdata)//64)
            elif REFACE:
                for i in range(len(txdata)//150):
                    outfile_name = dxcommon.list2string(txdata[150*i:150*i+10])
                    outfile_name = dxcommon.validfname(outfile_name)
                    Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
 
                    count = 0
                    while os.path.exists(Outfile):
                        count += 1
                        if count>1:
                            Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)
 
                    TXC.write(Outfile, txdata[150*i:150*(i+1)], channel, self.nosplit.get(), 1, yamaha, self.mid_out)
                message = "Ready. {} Patches written.".format(len(txdata)//150)
 
            else:
                for i in range(len(txdata)//128):
                    outfile_name = dxcommon.list2string(txdata[128*i+57:128*i+67])
                    outfile_name = dxcommon.validfname(outfile_name)
                    Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
 
                    count = 0
                    while os.path.exists(Outfile):
                        count += 1
                        if count>1:
                            Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)
 
                    TXC.write(Outfile, txdata[128*i:128*(i+1)], channel, self.nosplit.get(), 1, yamaha, self.mid_out)
                message = "Ready. {} Patches written.".format(len(txdata)//128)
        else:
            message = TXC.write(outfile, txdata, channel, self.nosplit.get(), split, yamaha, self.mid_out)


        self.status['text'] = 'Converting ...'
        self.update()

        tkinter.messagebox.showinfo("TXconvert-{}".format(PROGRAMVERSION), message)
        self.status['text'] = 'Select file(s) for conversion'
        self.update()
        return

    def info(self):
        mw = tkinter.Tk()
        mw.title('HELP') 
        txt = ScrolledText(mw, width=90, height=34)
        txt.pack()
        with open(HELP) as f:
            txt.insert(END, '\n    TXconvert-{} ({})\n'.format(PROGRAMVERSION, PROGRAMDATE))
            for line in f:
                txt.insert(END, line)
        txt.config(state=DISABLED)
        return

def gui_main():
    root = tkinter.Tk()
    root.title("{}-{}".format(PROGRAMNAME, PROGRAMVERSION))
    root.resizable(True, False)
    root.minsize(300, 0)
    txConvertDialog(root).pack(fill=X, expand=1)
    root.mainloop()
    return 0


################### MAIN #####################

if __name__ == '__main__':
    sys.exit(gui_main())
    

