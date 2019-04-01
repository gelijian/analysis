import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import shotanalysis as sa

plt.style.use("classic")
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 18

dir_data = "/home/gelijian/EAST/shot_data/201706/"
shot = 75055
dir_shot = os.path.join(dir_data, "%d" % shot)
dir_shot_parameter = os.path.join(dir_shot, "simulation", "shot_parameters")
os.chdir(dir_shot_parameter)
########################    reading     #########################
ipm = np.loadtxt("ipm.txt")
DFSDEV = np.loadtxt('DFSDEV.txt')
nbi1lhi = np.loadtxt('nbi1lhi.txt')
nbi1lhv = np.loadtxt('nbi1lhv 1000.txt')
nbi1lpower = nbi1lhi
nbi1lpower[:, 1] = nbi1lhi[:, 1] * nbi1lhv[:, 1] / 1000                       # MW
nbi1rhi = np.loadtxt('nbi1rhi.txt')
nbi1rhv = np.loadtxt('nbi1rhv 1000.txt')
nbi1rpower = nbi1rhi
nbi1rpower[:, 1] = nbi1rhi[:, 1] * nbi1rhv[:, 1] / 1000                       # MW
zz7_campbell = np.loadtxt("zz7_campbell.txt")

data_list = [ipm, DFSDEV]
label = ["ip", "ne"]
style = ["k-", "r-"]
ylim = [(0,600), (0, 8)]
################################    plot    #####################################
for i in xrange(len(data_list)):
    data = data_list[i]
    plt.figure(figsize = (8, 2))
    plt.step(data[:, 0], data[:, 1], style[i], lw = 2, label = label[i])
    plt.xlim(0, 12)
    plt.ylim(ylim[i])
    plt.legend()
    #~ plt.savefig("%s.eps" % label[i], dpi = 600)
    plt.show()
    plt.close()

data_list = [nbi1lpower, nbi1rpower]
label = ["pnbi1l", "pnbi1r"]
style = ["b-", "g-"]
plt.figure(figsize = (8, 2))
for i in xrange(len(data_list)):
    data = data_list[i]
    plt.step(data[:, 0], data[:, 1], style[i], lw = 2, label = label[i])
plt.xlim(0, 12)
plt.ylim(0, 2.5)
plt.legend()
#~ plt.savefig("pnbi.eps", dpi = 600)
plt.show()
plt.close()

###################### LS ###################################
second = np.power(10, 9)
binwidth = 0.1 # unit: s
binedge = np.arange(0, 20 * second, binwidth * second)
binmiddle = 0.5 * (binedge[1:] + binedge[:-1])
m = sa.PHdata()
filename = os.path.join(dir_data, "%d/751_ch/ch_22.txt" % (shot))
m.loaddata(filename, k = 6.95, b = 0)
range_Eee = [[100, 1000], [100, 1000]]
range_psd = [[0.195, 0.35], [0.0, 0.195]]
label = ["neutron", "gamma"]
plt.figure(figsize = (8, 2))
print m.psd
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
for i in xrange(2):
    index = m.PSD(range_Eee[i], range_psd[i])
    print index.shape
    timestamp = m.timestamp[index]
    counts, bins = np.histogram(timestamp, bins = binedge)
    flux = counts / binwidth
    flux[binmiddle < 1.6 * second] = 0
    plt.step(binmiddle / second, flux, lw = 2, label = label[i])
plt.legend()
plt.xlim(0, 12)
plt.ylim(0, 20000)
#~ plt.savefig("LS_n_g.eps", dpi = 600)
plt.show()
plt.close()




