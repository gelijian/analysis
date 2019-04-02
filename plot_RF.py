import sys
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import myplt
plt.style.use("classic")
matplotlib.rcParams['font.size'] = 18

instrument = "Stilbene"
dir_figure = "/home/gelijian/EAST/shot_data/figure"
dir_RF = os.path.join("/home/gelijian/EAST/shot_data/RF", instrument)
dir_RF_elements = os.path.join(dir_RF, "elements")
Enlist = np.loadtxt(os.path.join(dir_RF, "Enlist"))
binmiddle = np.loadtxt(os.path.join(dir_RF, "binmiddle"))

##########  Load instrument Response function ################
dim_En, dim_binmiddle = len(Enlist), len(binmiddle)
matrix_RF = np.matrix(np.zeros((dim_binmiddle, dim_En)))
for i, En in enumerate(Enlist):
    filename = os.path.join(dir_RF_elements, "En_%dkeV" % (En))
    matrix_RF[:, i] = np.loadtxt(filename).reshape(-1, 1)
M = matrix_RF.T
fig = plt.figure()
index = np.ceil(np.log10(M.max()))
levels = np.logspace(0, index, 50)
plt.contourf(binmiddle, Enlist / 1000.0, M, levels = levels, norm = matplotlib.colors.LogNorm(), cmap = myplt.cmap)
cbar = plt.colorbar()
cbar.set_ticks(np.power(10, np.arange(1, index + 1)))
# plt.ylim(0.5, )
# plt.xlim(30, 140)
# plt.xlabel("time of flight [ns]")
plt.xlabel("Light output [keVee]")
plt.ylabel("En [MeV]")
plt.savefig(os.path.join(dir_figure, "eps", '%s_RF.eps' % instrument), dpi = 600)
plt.show()
