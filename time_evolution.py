import os
import sys
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import shotanalysis as sa

plt.style.use("classic")
matplotlib.rcParams['font.size'] = 14

dir_data = "/home/gelijian/EAST/shot_data/201706"
second = np.power(10, 9)
###########  Exp data process #####################
s1list = [0, 1, 2, 3, 4]
s2list = [5, 6, 8, 9, 10, 11, 12, 13, 14]
slist = s1list + s2list
DGZ_type = ["751","APV"]
styles = ["r-o", "b-o"]
th_s1 = [(0, 1000000), (150, 100000)]
th_s2 = [(0, 5000000), (0, 1000000)]
offset = [0, 1.2 * second]
shotlist = np.arange(75055, 75056)
m = sa.TOFEDdata()
for shot in shotlist:
    dir_shot = os.path.join(dir_data, "%d" % shot)
    if not os.path.exists(dir_shot):
        continue
    width = 0.1
    binedge = np.arange(0, 15 * second, width * second)
    binmiddle = 0.5 * (binedge[:-1] + binedge[1:])
    tlist_s1 = [[], []]
    tlist_s2 = [[], []]
    #~ for i in xrange(len(DGZ_type)):
        #~ dir_ch = os.path.join(dir_shot, "%s_ch" % DGZ_type[i])
        #~ for ch in slist:
            #~ filename = os.path.join(dir_ch, "ch_%d.txt" % ch)
            #~ data = np.loadtxt(filename)
            #~ timestamp = data[:, 0]
            #~ ql = data[:, 2]
            #~ if ch in s1list:
                #~ index = sa.index_range(ql, th_s1[i])
                #~ tlist_s1[i] = np.append(tlist_s1[i], timestamp[index])
            #~ if ch in s2list:
                #~ index = sa.index_range(ql, th_s2[i])
                #~ tlist_s2[i] = np.append(tlist_s2[i], timestamp[index])
        #~ tlist_s1[i] += offset[i]
        #~ c1, bins = np.histogram(tlist_s1[i], bins = binedge)
        #~ c2, bins = np.histogram(tlist_s2[i], bins = binedge)
        #~ f1 = c1 / width
        #~ f2 = c2 / width
        #~ index = (binmiddle < 12 * second) & (binmiddle > 10 * second)
        #~ f1[binmiddle < 2 * second] = f1[index].mean()
        #~ plt.figure(figsize = (8, 2))
        #~ plt.step(binmiddle / second, f1 * 2, lw = 2, label = "S1")
        #~ plt.step(binmiddle / second, f2 * 2, lw = 2, label = "S2")
        #~ plt.title("shot: %d, DGZ: %s" % (shot, DGZ_type[i]))
        #~ plt.legend()
        #~ plt.show()
        #~ plt.close()
    m.set_dir_shot(dir_shot)
    th_tof = [0, 200]
    cnlist = []
    width = 0.5
    binedge = np.arange(0, 15 * second, width * second)
    binmiddle = 0.5 * (binedge[:-1] + binedge[1:])
    plt.figure()
    for i in xrange(len(DGZ_type)):
        filename = os.path.join(dir_data, "%s_divergence_old" % DGZ_type[i])
        filename = os.path.join(dir_data, filename)
        m.set_DGZ_type(DGZ_type[i])
        m.load_divergence(filename)
        m.load_board_offset()
        data = m.load_pairs(s1list, s2list, include_divergence = True)
        i1 = sa.index_range(data[:, 0], th_tof)
        i2 = sa.index_range(data[:, 1], th_s1[i])
        i3 = sa.index_range(data[:, 2], th_s2[i])
        index = i1 & i2 & i3
        tlist = data[index, 3] + offset[i]
        cnlist = np.append(cnlist, tlist)
        cn, bins = np.histogram(tlist, bins = binedge)
        fn = cn / width
        #~ plt.figure(figsize = (8, 2))
        plt.step(binmiddle / second, fn, lw = 2, label = DGZ_type[i])
    plt.title("shot: %d, DGZ: %s" % (shot, DGZ_type[i]))
    plt.legend()
    plt.show()
    
    plt.figure(figsize = (8, 2))
    cn, bins = np.histogram(tlist, bins = binedge)
    fn = cn / width
    plt.step(binmiddle / second, fn, lw = 2, label = "cn")
    plt.xlim(0, 12)
    plt.ylim(0, 120)
    plt.legend()
    plt.savefig("cn.eps", dpi = 600)
    plt.show()
    


        
