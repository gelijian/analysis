import os
import numpy as np
import matplotlib
from matplotlib import ticker
import matplotlib.pyplot as plt
import myplt

plt.style.use("classic")
font = {'family': 'serif',
        'weight': 'normal',
        'size': 17,
        }
matplotlib.rcParams['font.size'] = 17
instrument = "TOFED"
unit = "ns"
#~ instrument = "EJ301"
#~ unit = "keV"
shotnumber = 75051
dir_WF = os.path.join("%d" % (shotnumber), "WF")
dir_inst = os.path.join(dir_WF, instrument)
dir_NES_WF = os.path.join(dir_inst, "NES")
dir_instrument_WF = os.path.join(dir_inst, "instrument")
bin_instrument = np.loadtxt(os.path.join(dir_inst, "binmiddle"))
bin_width = bin_instrument[1] - bin_instrument[0]
Eblist = np.loadtxt(os.path.join(dir_inst, "Eblist"))
mulist = np.loadtxt(os.path.join(dir_inst, "mulist"))

##################  Load instrument Weight function ################
dim_Eb = len(Eblist)
dim_mu = len(mulist)
dim_bin_instrument = len(bin_instrument)
array_instrument_WF = np.zeros((dim_mu, dim_Eb, dim_bin_instrument))
for i in range(dim_mu):
    for j in range(dim_Eb):
        filename = os.path.join(dir_instrument_WF, "mu_%d_Eb_%d" % (i, j))
        WF_i_j = np.loadtxt(filename)
        array_instrument_WF[i, j, :] = WF_i_j

##############  plot the WF at specfic bin of instrument ###########
range_plot = [65.9, 76.3]
#~ range_plot = (890, 920)
for k in range(dim_bin_instrument):
    bin_plot = bin_instrument[k]
    if not ((bin_plot > range_plot[0]) & (bin_plot < range_plot[1])):
        continue
    bin_low, bin_high = bin_plot - bin_width / 2.0, bin_plot + bin_width / 2.0
    WF = array_instrument_WF[:, :, k]
    WF = WF / np.power(10, 8)
    message = "WF for %s at [%g, %g] %s" % (instrument, bin_low, bin_high, unit)
    print(message) 
    fig = plt.figure()
    levels = np.linspace(WF.max()/40, WF.max(), 15, endpoint = True)
    plt.contour(Eblist, mulist, WF, levels = levels, colors = "k", linewidths = 1)
    plt.contourf(Eblist, mulist, WF, 300, cmap = myplt.cmap)
    cb = plt.colorbar()
    cb.formatter.set_powerlimits((0, 0))
    cb.update_ticks()
    plt.xlabel("E [keV]", fontsize = 17)
    plt.ylabel("Pitch", fontsize = 17)
    plt.yticks(np.arange(-0.8, 1.0, 0.2))
    plt.tight_layout()
    #~ plt.savefig(os.path.join(dir_inst, '%s_%g_WF.eps' % (instrument, bin_plot)), dpi = 600)
    plt.show()
    plt.close()   
