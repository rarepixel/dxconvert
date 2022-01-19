DXCONVERT/TXCONVERT version 3.x
date: 20210508

===================================

WHAT'S THIS? 

DXCONVERT
is a cross-platform tool that reads files with DX7(II)/TX7 (compatible) 
patchdata, and writes them to files with DX7/DX7II/TX7 patchdata as pure 
clean SysEx data, standard format 0 MIDI file with SysEx data, or 
4096 bytes packed 32-voice DX7 format (VMEM). DXCONVERT can read many many 
different input file formats, including some strange and exotic ones. 
If in doubt, simply try. If the output is garbage, the fileformat is not 
or badly supported. For a list of currently supported file and data 
formats see FORMATS.txt. 
If you encounter an unsupported DX7 fileformat: please report!

DXconvert can also read files with voicedata from 4-op FM synth
(TX81Z, DX21, FB01, etc.), 2-op FM synths (PSS-480/580/680), and
.opm files from VOPM (a free 4-op FM VST plugin) and converts
these to DX7 voices. 

Optionally DXconvert can perform all kinds of manipulations on the data like:
sort by name, randomize, remove duplicates, find by name or select by number.

TXCONVERT
is a similar tool but it writes data to be used with the Yamaha 4-OP FM synths:
DX100, DX27(s), DX21, DX11 (V2), TX81Z, WT11, DS55, TQ5, YS100, YS200, B200, V50, FB01,
and Reface DX, and with a free VST plugin called VOPM.
It can read the same 4-op and 2-op FM synth voicedata that DXconverts reads,
but not the 6-OP DX7 data. This README file is written for DXconvert. A better
description of TXconvert is on my TODO list, but reading this document should
give you some idea about the use of TXconvert also.

====================================

REQUIREMENTS?

These tools were written using Python 3.8 
If you install the latest stable version of 3.x it should work.
It might also work with Python 2.7, but this is not guaranteed anymore.

Python is available for free for all major platforms ( Windows, Mac, Linux).

For MIDI support python-rtmidi is required. It's available from: 
    http://pypi.python.org/pypi/python-rtmidi/

For import of TX7/DX21/DX100/DX11 cassette-interface data in wav or cas
format you need the MSX castools from Vincent vam Dam. You can find it
here: http://home.kabelfoon.nl/~vincentd/
Also read README-wav2cas.txt

====================================

INSTALLATION? 

- Install Python-3.4.0 (or newer) for your OS
- Make sure python c.q. python.exe is in your system PATH

After installation of Python, you can copy the DXconvert directory to a 
suitable location. The subdirectory named "DXconvert" inside that 
directory should be in the directory from where you start dxconvert.py, 
or it should be a location where python on your system searches for 
packages and modules. (PYTHONPATH). For example on my Linux Fedora 
system, I have copied the DXconvert subdirectory to 
${HOME}/.local/lib/python-3.7/site-packages/. And I have copied/renamed 
dxconvert.py to ~/bin/dxconvert in my HOME directory. 
The ideal situation is when dxconvert.py is in your systems PATH 
and the DXconvert subdirectory in your PYTHONPATH.

If you have installed python-rtmidi MIDI I/O support is available.
Running midi_help.py script will show you the available MII ports.
You can select the ones you need and create an initial dxtxmidi.cfg
file. You can also use the main dx/txconvert programs to select the
MIDI ports. In simple situations this only needs to be done once.

NOTE: I do no not know much about Windows and Mac. Please add information 
to this README file and send it to me if you have used DXconvert 
succesfully on your platform.


=======================================

USAGE? 

GUI usage:
----------
Double-click on dxconvert-gui.py.
Select one or more input files, and one output filename. 

You can select DX7 or DX7II compatibility. If you deselect the DX7II checkbox, 
you might loose some parameters that only the DX7II/TX802/DX200 support.
DX7II data can also be exported as TX7 performance data, and vice versa.

The export fileformat is based on the extension of the output file name. 
4 file extensions are allowed:

1) DXconvert: .dx7 or .DX7:
4096 bytes raw DX7 voice data, without headers, without DX7II 
additional data. Do not use this fileformat if you want to keep DX7II 
additional parameters (AMEM/ACED) If the input file contains only a 
single patch, the patch is saved as a 128 bytes small single VMEM 
datapack. The program tries to convert DX7II/DX200 "AMS" and "PEGR"
parameters into old DX7 AMS and PEG data for improved compatibility. 

TXconvert: use *.dxx for raw 4OP voice data, *.fb1 for raw FB01 data.

2) .syx or .SYX:
DX7, TX7, or DX7II voice data SysEx file including SysEx header, 
checksum, and EOX (End Of Exclusive 0xf7).

3) .mid, .midi, .MID, or .MIDI: 
Same data as SysEx, but written as a Standard Midifile 
format 0 track that can be imported directly into your MIDI sequencer.

4) .txt or .TXT:
- If there is only one selected voice, this will save a list of all 
voiceparameters and their values. (decimal MIDI values, not always 
values as displayed on DX7)
- If there are more selected voices, this will save a list with 
voicenames.

5) other or no extension: SysEx format is used.

6) Special: if "MIDI" (without the quotes, case-sensitive) is selected as 
outfile name, data will be sent to a MIDI port, if available. To select 
the right MIDI port click on the MIDI icon.  

Many additional options are available like sorting, selecting, and
randomizing patches. Just click on the switches or fill in the appropiate
fields. See below for a description of the options (COMMANDLINE usage). 

If the input file contains more than 32 patches (e.g. 64 or 128) the 
output is split into multiple files. They will have names like 
INFILE(1).syx INFILE(2).syx etc. (Unless you select the --nosplit option)

NOTE: After completing your conversion you are free to change the file 
extension from .dx7 or .syx into something else. Some stupid DX7 managers 
refuse to read files if they do not have a specific extension. I have 
seen extensions like .bnk or .32 for simple SysEx or raw DX7 files. 
DXconvert can read all of them, at least all the ones that I have seen.


COMMANDLINE usage (Recommended!):
---------------------------------
The commandline version is named dxconvert.py/txconvert.py, 
The GUI version dxconvert-gui.py/txconvert-gui.py (or .pyw) has exactly the
same functionality.

Usage: 
	dxconvert.py INFILE(S) OUTFILE [options]

Commandline options:	
    dxconvert.py --help
    txconvert.py --help
will tell you many more tricks you can do with dxconvert/txconvert 

===========================================================================

LIMITATIONS and BUGS:

- Only DX7/DX7II Voice data and TX7 performance data are supported. 
Other data like DX7II Performances, Microtunings, and Fractional Scaling 
data are ignored and not saved in the exported files. 

- On some systems (Windows ?) splitting very large libraries is reported
to fail in combination with very long pathnames when using pythonw.exe to
start DXconvert. I have no idea why. Maybe a pythonw.exe bug ?
It does not seem to happen on my Linux system, and it does not happen 
when using python.exe instead of pythonw.exe to start DXconvert on 
Windows. That's why since 1.1.10 I use ".py" instead of ".pyw" as extension
for txconvert-gui.py and dxconvert-gui.py

Note: It seems that with Python-3.x version this problem has been fixed.

ALWAYS KEEP A BACKUP OF YOUR ORIGINAL FILES! 
I did a lot of testing, but still there could be bugs. 
Let me know if you find any. Also report unsupported Yamaha DX/TX
voice data fileformats to me. It might be supported in a next version.


========================================================================


EXTRAS:

In the Tools directory you will some useful utilities like mid2syx.py and 
syx2mid.py You can use these to convert ANY SysEx file into a MIDI format 0
file, or to extract SysEx data from a MIDI file. Use this for example if you 
want to convert a DX7II file including Performance and Microtuning data to 
standard MIDI file. But you can also use it with files from other synths.

=========================================================================

THANKS:

Many thanks go to Charles Copp (DX200 import ideas), Renata Dokmanovic (a 
lot), Sean Bolton (FB01 import and Hexter-DSSI, which I used a lot for 
testing sounds.), Paul Deco (heavy testing), Daniel Forró (exotic file examples),
Jon Morgan (FM-ALive DX Manager), Sam (VOPM), Steve Finney (Reface DX testing), 
ChunkyBloke (Korg DS-8 testing and conversion improvements)
and several members of Yahoo forums and Facebook groups who helped me with facts, 
figures, file examples, bugreports, feature requests, PayPal donations and good 
ideas to create and improve this program.

==========================================================================

LEGAL:

Yamaha is a registered trademark etcetera etcetera blablablabla ...
DXconvert is published under GPL v3 or higher. See LICENCE.txt 

=========================================================================

DONATIONS:

Do you want to support this project? 
Donations are welcome: 
https://paypal.me/mtarenskeen

==========================================================================

CONTACT:

m.tarenskeenATkpnmail.nl

or join the Facebook Yamaha DX7 owners, Yamaha Reface, Yamaha Soundmondo, Korg DS8 & 707, and/or Yamaha V50 group(s), 
or join the YamahaDX forum at groups.io 

Enjoy DXconvert and have more fun with your Yamaha synths!

M.T.

