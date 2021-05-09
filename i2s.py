from pyo import *
import time
import sys
import math
from PIL import Image
import numpy as np

def img_to_params(im_path):
    im = Image.open(im_path)
    im = im.convert('RGB')
    width, height = im.size


    values = []
    pixel = 10
    overlap = 2
    for w in range(0, width, pixel-overlap):
        for h in range(0, height, pixel-overlap):
            reds = []
            greens = []
            blues = []
            for pw in range(w,min(w+pixel,width)):
                for hw in range(h,min(h+pixel,height)):
                    r, g, b = im.getpixel((pw, hw))
                    reds.append(r)
                    greens.append(g)
                    blues.append(b)

            mr = np.mean(r)
            mg = np.mean(g)
            mb = np.mean(b)
            values.append( (mr, mg, mb) )

    return values

s = Server().boot()
s.amp = 0.1

# Defines tables for the amplitude, the ratio and the modulation index.
amp_table = CosTable([(0, 0), (100, 1), (1024, 0.5), (4048, 0.5), (8192, 0)])
rat_table = ExpTable(
    [(0, 0.5), (1500, 0.5), (2000, 0.8), (3500, 0.8), (4000, 1), (5500, 1), (6000, 0.5), (8192, 0.4),]
)
ind_table = LinTable([(0, 20), (512, 10), (8192, 0)])

# call their graph() method. Use the "yrange" argument to set the minimum
# and maximum bundaries of the graph (defaults to 0 and 1).
amp_table.graph(title="Amplitude envelope")
rat_table.graph(title="Ratio envelope")
ind_table.graph(yrange=(0, 20), title="Modulation index envelope")

# Initialize the table readers (TableRead.play() must be called explicitly).
amp = TableRead(table=amp_table, freq=1, loop=False, mul=0.3)
rat = TableRead(table=rat_table, freq=1, loop=False)
ind = TableRead(table=ind_table, freq=1, loop=False)

# Use the signals from the table readers to control an FM synthesis.
fm = FM(carrier=[100, 100], ratio=rat, index=ind, mul=amp).out()

# Call the "note" function to generate an event.
def note(arg):
    freq, dur, cap = arg
    fm.carrier = [freq, freq * cap]
    amp.freq = 1.0 / dur
    rat.freq = 1.0 / dur
    ind.freq = 1.0 / dur
    amp.play()
    rat.play()
    ind.play()

calls = []
moment = 0
bpm = 220
root_freq = 80
param_arr = img_to_params(sys.argv[1])

for params in param_arr:
    r, g, b = params
    play_for = 60/bpm
    cap = 1 + 500/(r+10)

    freq = root_freq * math.pow(2,int(b/25)/12)

    calls.append(CallAfter(note,moment,(freq, play_for, cap)))
    for k in range(1,int(g/30)):
        calls.append(CallAfter(note,moment,(freq*k, play_for/k, cap)))
    moment += play_for

s.gui(locals())
exit()
