import os
import sys
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import interpolate
from matplotlib.colors import LogNorm
import shotanalysis as sa

plt.style.use("classic")
matplotlib.rcParams['font.size'] = 20
matplotlib.rcParams["savefig.bbox"] = "tight"

dir_data = "/home/gelijian/EAST/shot_data/201706"
dir_RF = "/home/gelijian/EAST/shot_analysis/TOFED_RF"
sa.TOFEDdata.set_dir_RF(dir_RF)
#~ binedge = np.arange(-200, 200, 0.4)
#~ fwhm_DAQ = np.sqrt(0.6**2 + 0.6**2 + 0.6**2)
#~ sa.TOFEDdata.cal_RF(binedge, fwhm_DAQ)
Enlist = np.arange(500, 3520, 20)
binedge = np.arange(-200, 200, 0.4)
binmiddle = 0.5 * (binedge[1:] + binedge[:-1])

###########  Exp data process #####################
s1list = [0, 1, 2, 3, 4]
s2list = [5, 6, 8, 9, 10, 11, 12, 13, 14]
DGZ_type = ["751", "APV"]
styles = ["r-o", "b-o"]
th_s1 = [(0, 10000), (180, 10000)]
th_s2 = [(0, 5000), (0, 5000)]
#~ offset = [-0.4, 0.4]
offset = [0.04, 0.04]
#~ shotlist = [75056]
#~ shotlist = [72603]
shotlist = np.arange(75030, 75076)
good_shot = []
m = sa.TOFEDdata()
tof_shot_list = []
for shot in shotlist:
    dir_shot = os.path.join(dir_data, "%d" % shot)
    if not os.path.exists(dir_shot):
        continue
    m.set_dir_shot(dir_shot)
    tof_shot = []
    tof_list = []
    for i in xrange(2):
        filename = os.path.join(dir_data, "%s_divergence_old" % DGZ_type[i])
        m.set_DGZ_type(DGZ_type[i])
        m.load_divergence(filename)
        m.load_board_offset()
        data = m.load_pairs(s1list, s2list, include_divergence = True)
        qls1 = data[:, 1]
        qls2 = data[:, 2]
        i1 = sa.index_range(qls1, th_s1[i])
        i2 = sa.index_range(qls2, th_s2[i])
        index = i1 & i2
        tof = data[index, 0] + offset[i]
        tof_list.append(tof)
        tof_shot = np.append(tof_shot, tof)
    #~ index= (tof_shot < 10) & (tof_shot > 1)
    index = (tof_shot < 85) & (tof_shot > 65)
    count = index.sum()
    if count > 20:
        good_shot.append((shot, count))
        tof_shot_list.append(tof_shot)
        print (shot, count)
    else:
        continue
    #~ plt.figure()    
    #~ for i in xrange(2):
        #~ histtof, bins = np.histogram(tof_list[i], bins = binedge)       
        #~ plt.plot(binmiddle, histtof, styles[i], lw = 3, label = DGZ_type[i])
    #~ histtof_shot, bins = np.histogram(tof_shot, bins = binedge)
    #~ plt.step(binmiddle, histtof_shot, "k-", lw = 3, label = "total")
    #~ plt.title("shot %d" % shot)
    #~ plt.xlabel("time-of-flight [ns]")
    #~ plt.ylabel("Counts / bin")
    #~ plt.xlim(-50, 150)
    #~ plt.ylim(0, histtof_shot.max() * 1.1)
    #~ plt.savefig("72603_TOF.eps", dpi = 600)
    #~ plt.show()
    #~ plt.close()
np.savetxt("goodshot", good_shot, fmt = "%g")  
#~ index = (binmiddle > 90) & (binmiddle < 105) & (histtof_exp > 19)
#~ histtof_exp[index] = histtof_exp[index] - 4

histtof_exp = 0
for i in xrange(len(tof_shot_list)):
    histtof, bins = np.histogram(tof_shot_list[i], bins = binedge)
    histtof_exp += histtof 
index = sa.index_range(binmiddle, (-200, -20))
bg = np.floor(histtof_exp[index].mean())
print bg
i1 = (binmiddle > -200) & (binmiddle < -20) 
i2 = (binmiddle > 10) & (binmiddle < 63)
i3 = binmiddle > 90
i4 = np.abs(histtof_exp - bg) > 5
index = (i1 | i2) & i4
histtof_exp[index] = 0.7 * histtof_exp[index] + 0.3 *  bg
index = i3 & i4
histtof_exp[index] = 0.6 * histtof_exp[index] + 0.4 *  bg
plt.figure()
plt.step(binmiddle, histtof_exp, "k-", lw = 1)
plt.xlabel("time-of-flight [ns]")
plt.ylabel("Counts / bin")
plt.xlim(-200, 200)
plt.ylim(0, histtof_exp.max() * 1.1)
plt.savefig("TOF.eps", dpi = 600)
plt.show()
plt.close()













