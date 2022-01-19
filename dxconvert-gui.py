#!/usr/bin/env python3
"""
dxconvert-gui.py

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
except:
    WITH_TOOLTIP = False
from DXconvert import DXC
from DXconvert import dxcommon, dxcommongui

PROGRAMNAME=DXC.PROGRAMNAME
PROGRAMVERSION=dxcommon.PROGRAMVERSION
PROGRAMDATE=dxcommon.PROGRAMDATE

LOGO='DXconvert/dxconvert.gif'
HELP='DXconvert/dxconvert.help'
MIDILOGO='DXconvert/midi.gif'
for p in sys.path:
    _logo = os.path.join(p, 'DXconvert/dxconvert.gif')
    if os.path.exists(_logo):
        LOGO=_logo
        break
for p in sys.path:
    _help = os.path.join(p, 'DXconvert/dxconvert.help')
    if os.path.exists(_help):
        HELP=_help
        break
for p in sys.path:
    _midilogo = os.path.join(p, 'DXconvert/midi.gif')
    if os.path.exists(_midilogo):
        MIDILOGO=_midilogo
        break

############ GUI ##############

class dx7ConvertDialog(tkinter.Frame):
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
        self.infile = tkinter.Entry(body, width=60)
        self.infile.grid(row=ROW, column=COLUMN, columnspan=5, sticky=W, padx=5, pady=5)
        self.tooltip(self.infile, "Enter input filename(s)")

        infile_button = tkinter.Button(body, text="...", command=self.get_infile)
        infile_button.grid(row=ROW, column=7, padx=5, pady=5)
        self.tooltip(infile_button, "Open fileselector")

        ROW+=1
        tkinter.Label(body, text='Output file:').grid(row=ROW, sticky=W)
        self.outfile = tkinter.Entry(body, width=60)
        self.outfile.grid(row=ROW, column=COLUMN, columnspan=5, sticky=W, padx=5, pady=5)
        self.tooltip(self.outfile, "Enter output filename")

        outfile_button = tkinter.Button(body, text="...", command=self.get_outfile)
        outfile_button.grid(row=ROW, column=7, padx=5, pady=5)
        self.tooltip(outfile_button, "Open fileselector")
    
        ROW+=1
        tkinter.Label(body, text='Options:').grid(row=ROW, sticky=W)
        self.dx72 = tkinter.BooleanVar()
        self.dx72_button = tkinter.Checkbutton(body, text="--dx72", variable=self.dx72)
        self.dx72_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(self.dx72_button, "Save with AMEM/ACED (DX7II) data")

        ROW+=1
        self.TX7 = tkinter.BooleanVar()
        self.tx7_button = tkinter.Checkbutton(body, text="--tx7", variable=self.TX7)
        self.tx7_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(self.tx7_button, "Save with TX7 function data")

        ROW+=1
        self.split = tkinter.BooleanVar()
        split_button = tkinter.Checkbutton(body, text="--split", variable=self.split)
        split_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(split_button, "Save each single patch as a separate file")

        ROW+=1
        self.nosplit = tkinter.BooleanVar()
        nosplit_button = tkinter.Checkbutton(body, text="--nosplit", variable=self.nosplit)
        nosplit_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nosplit_button, "Save data in one single file")

        ROW+=1
        self.nosilence = tkinter.BooleanVar()
        nosilence_button = tkinter.Checkbutton(body, text="--nosilence", variable=self.nosilence)
        nosilence_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nosilence_button, "Remove patches that produce no sound")

        ROW=3
        COLUMN+=1
        self.sort = tkinter.BooleanVar()
        sort_button = tkinter.Checkbutton(body, text="--sort", variable=self.sort)
        sort_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(sort_button, "Sort patches by voicename (case-insensitive)")

        ROW+=1
        self.sort2 = tkinter.BooleanVar()
        sort2_button = tkinter.Checkbutton(body, text="--sort2", variable=self.sort2)
        sort2_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(sort2_button, "Sort patches by voicename (case-sensitive)")

        ROW+=1
        self.nodupes = tkinter.BooleanVar()
        nodupes_button = tkinter.Checkbutton(body, text="--nodupes", variable=self.nodupes)
        nodupes_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nodupes_button, "Remove duplicates")

        ROW+=1
        self.nodupes2 = tkinter.BooleanVar()
        nodupes2_button = tkinter.Checkbutton(body, text="--nodupes2", variable=self.nodupes2)
        nodupes2_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(nodupes2_button, "Remove duplicates, but ignore voicenames")
 
        ROW+=1
        self.random = tkinter.BooleanVar()
        random_button = tkinter.Checkbutton(body, text="--random", variable=self.random)
        random_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(random_button, "Renata's Randomizer")

        ROW=3
        COLUMN += 1
        self.bc2at = tkinter.BooleanVar()
        bc2at_button = tkinter.Checkbutton(body, text="--bc2at", variable=self.bc2at)
        bc2at_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(bc2at_button, "Copy BreathControl data to AfterTouch")

        ROW += 1
        self.fc1 = tkinter.BooleanVar()
        self.fc1.set(True)
        fc1_button = tkinter.Checkbutton(body, text="--fc1", variable=self.fc1)
        fc1_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(fc1_button, "Use FC1 foot controller data")

        ROW += 1
        self.fc2 = tkinter.BooleanVar()
        self.fc2.set(True)
        fc2_button = tkinter.Checkbutton(body, text="--fc2", variable=self.fc2)
        fc2_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(fc2_button, "Use FC2 foot controller data")

        ROW += 1
        self.bc = tkinter.BooleanVar()
        self.bc.set(True)
        bc_button = tkinter.Checkbutton(body, text="--bc", variable=self.bc)
        bc_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(bc_button, "Use BreathControl data")
        
        ROW += 1
        self.check = tkinter.BooleanVar()
        check_button = tkinter.Checkbutton(body, text="--check", variable=self.check)
        check_button.grid(row=ROW, column=COLUMN, pady=5, sticky=W)
        self.tooltip(check_button, "Check SysEx checksum before import")

        ROW=3
        COLUMN += 1
        select_label = tkinter.Label(body, text="--select <RANGE>:")
        select_label.grid(row=ROW, column=COLUMN, padx=10, pady=5, sticky=W)
        self.tooltip(select_label, 'Select range to save (e.g. "2,5,7-12,18-32")a')
        self.select = tkinter.Entry(body, width=8)
        self.select.grid(row=ROW, column=COLUMN+1, sticky=W)
        self.tooltip(self.select, 'Select range to save (e.g. "2,5,7-12,18-32")a')

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
        self.tooltip(brightness_label, "Adjust global brightness (+/-)")
        self.dxbrightness = tkinter.Entry(body, width=8)
        self.dxbrightness.grid(row=ROW, column=COLUMN+1, columnspan=2, sticky=W)
        self.tooltip(self.dxbrightness, "Adjust global brightness (+/-)")
       
        ROW += 1
        find_label = tkinter.Label(body, text='--find <string>:')
        find_label.grid(row=ROW, column=COLUMN, columnspan=2, padx=10, pady=5, sticky=W)
        self.tooltip(find_label, "search for STRING in filename")
        self.dxfind = tkinter.Entry(body, width=8)
        self.dxfind.grid(row=ROW, column=COLUMN+1, sticky=W, pady=5)
        self.tooltip(self.dxfind, "search for STRING in filename")
         
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
        self.tooltip(convert_button, "Start dxconvert!")

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
            parent=None, title='Select DX/TX file(s) to convert')
        if infile:
            self.infile.delete(0, END)
            self.infile.insert(0, infile)
        return

    def get_outfile(self):
        outfile = tkinter.filedialog.asksaveasfilename(
            parent=None, title='Select DX7 export name/filetype') 

        if outfile:
            outfile = os.path.normpath(outfile)
            outfile_ext = os.path.splitext(outfile)[1]
            outfile_dir = os.path.split(outfile)[0]
            self.outfile.delete(0, END)
            self.outfile.insert(0, outfile)

            if outfile[-4:].lower() == '.dx7':
                self.dx72_button.config(state=DISABLED)
                self.tx7_button.config(state=DISABLED)
            else:
                self.dx72_button.config(state=NORMAL)
                self.tx7_button.config(state=NORMAL)
        return

    def convert(self):
        self.status['text'] = '......'
        
        infile = self.infile.get()
        if not infile:
           message = 'No input file(s) selected'
           tkinter.messagebox.showerror("DXconvert-{}".format(PROGRAMVERSION), message)
           self.status['text'] = 'Select file(s) for conversion'
           return
       
        # Workaround for tkFileDialog.askopenfilesnames bug
        # Hopefully one day this will not be needed anymore
        if type(infile) == str:
            master = tkinter.Tk()
            master.withdraw()
            infile = master.tk.splitlist(infile)

        outfile = self.outfile.get()
        if not outfile:
            message = 'No output files selected'
            tkinter.messagebox.showerror("DXconvert-{}".format(PROGRAMVERSION), message)
            self.status['text'] = 'Select file(s) for conversion'
            return
        else:
            outfile_ext = os.path.splitext(outfile)[1]
            outfile_dir = os.path.split(outfile)[0]

        self.status['text'] = 'Reading ...'
        self.update()
        dx7data = []
        dx72data = []
        tx7data = []
        channel=0
        if self.offset.get():
            offset = self.offset.get()
        else:
            offset = '0'

        for inp in infile:
            inp = os.path.normpath(inp)
            if os.path.isfile(inp):

                dx7dat, dx72dat, tx7dat, channel=DXC.read(inp, offset, self.check.get(), self.mid_in, self.mid_out)
                dx7data += dx7dat
                dx72data += dx72dat
                tx7data += tx7dat
                self.status['text'] = 'Read {}'.format(inp)
                self.update()

        if self.channel.get():
            channel = min(15, max(0, int(self.channel.get())-1))

        if self.select.get():
            dx7dat, dx72dat, tx7dat = [], [], []
            for i in dxcommon.range2list(self.select.get()):
                dx7dat += dx7data[128*(i-1):128*i]
                dx72dat += dx72data[35*(i-1):35*i]
                tx7dat += dx7data[64*(i-1):64*i]
            dx7data, dx72data, tx7data = dx7dat, dx72dat, tx7dat

        if self.dxfind.get():
            self.status['text'] = 'Searching names ...'
            self.update()
            dx7data, dx72data, tx7data = DXC.dxfind(dx7data, dx72data, tx7data, self.dxfind.get())

        if self.dxbrightness.get():
            self.status['text'] = 'Adjusting brightness ...'
            self.update()
            dx7data = DXC.dxbrightness(dx7data, int(self.dxbrightness.get()))

        if self.random.get():
            self.status['text'] = "Randomizing voices ..."
            self.update()
            dx7data = dxcommon.dxrandom(dx7data)

        if self.nodupes2.get() == True:
            nodupes2 = True
        else:
            nodupes2 = False

        if (self.nodupes.get() == True) or (self.nodupes2.get() == True):
            self.status['text'] = "Removing duplicates ..."
            self.update()
            dx7data, dx72data, tx7data = DXC.dxnodupes(dx7data, dx72data, tx7data, self.dx72.get(), self.TX7.get(), nodupes2)

        if self.nosilence.get() == True:
            self.status['text'] = "Removing patches with no sound"
            self.updat()
            dx7data, dx72data, txcdata = DXC.nosilence(dx7data, dx72data, tx7data)

        if self.sort.get() == True:
            self.status['text'] = "Sorting voices by name ..."
            self.update()
            dx7data, dx72data, tx7data = DXC.dxsort(dx7data, dx72data, tx7data, self.dx72.get(), self.TX7.get())
        elif self.sort2.get() == True:
            self.status['text'] = "Sorting voices by name ..."
            self.update()
            dx7data, dx72data, tx7data = DXC.dxsort(dx7data, dx72data, tx7data, self.dx72.get(), self.TX7.get(), True)
        
        for i in range(len(dx7data)//128):
            if self.bc2at.get() == True:
                dx72data[20+35*i:24+35*i] = dx72data[16+35*i:20+35*i]
            if self.fc1.get() == False:
                dx72data[12+35*i:16+35*i] = [0, 0, 0, 0]
            if self.fc2.get() == False:
                dx72data[26+35*i:30+35*i] = [0, 0, 0, 0]
            if self.bc.get() == False:
                dx72data[16+35*i:20+35*i] = [0, 0, 0, 50]

        if self.split.get() and (len(dx7data)//128 > 1):
            count = 0
            for i in range(len(dx7data)//128):
                outfile_name = dxcommon.list2string(dx7data[128*i+118:128*i+128])
                outfile_name = dxcommon.validfname(outfile_name)
                Outfile = os.path.join(outfile_dir, outfile_name + outfile_ext)
            
                count = 0
                while os.path.exists(Outfile):
                    count += 1
                    if count>1:
                        Outfile = os.path.join(outfile_dir, outfile_name + "(" + str(count) + ")" + outfile_ext)

                DXC.write(outfile_name, dx7data[128*i:128*(i+1)], dx72data[35*i:35*(i+1)], tx7data[64*i:64*(i+1)], self.dx72.get(), self.TX7.get(), channel, self.nosplit.get(), self.mid_out)
            message = "Ready. {} Patches written.".format(len(dx7data)//128)
        else:
            message = DXC.write(outfile, dx7data, dx72data, tx7data, self.dx72.get(), self.TX7.get(), channel, self.nosplit.get(), self.mid_out)

        self.status['text'] = 'Converting ...'
        self.update()

        tkinter.messagebox.showinfo("DXconvert-{}".format(PROGRAMVERSION), message)
        self.status['text'] = 'Select file(s) for conversion'
        self.update()
        return
    
    def info(self):
        mw = tkinter.Tk()
        mw.title('HELP') 
        txt = ScrolledText(mw, width=90, height=35)
        txt.pack()
        with open(HELP) as f:
            txt.insert(END, '\n    DXconvert-{} ({})\n'.format(PROGRAMVERSION, PROGRAMDATE))
            for line in f:
                txt.insert(END, line)
        txt.config(state=DISABLED)
        return

def gui_main():
    root = tkinter.Tk()
    root.title("{}-{}".format(PROGRAMNAME, PROGRAMVERSION))
    root.resizable(True, False)
    root.minsize(300, 0)
    dx7ConvertDialog(root).pack(fill=X, expand=1)
    root.mainloop()
    return 0


################### MAIN #####################

if __name__ == '__main__':
    sys.exit(gui_main())
    

