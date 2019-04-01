import os
import numpy as np
from scipy.optimize import leastsq
import matplotlib
import matplotlib.pyplot as plt
import shotanalysis as sa

plt.style.use("classic")
matplotlib.rcParams['font.size'] = 17

def func(x, p):
    a, miu, sigma = p
    y = (x - miu) / sigma
    return  a * np.exp(-0.5 * np.power(y, 2))

def residuals(p, y, x):
    return y - func(x, p)

#####################################
# 751: 4.8 up: 4.9, bottom 4.5
# APV: 4.1 
num_board = 2
reflist = [7, 15]
s1list = [0, 1, 2, 3, 4]
s2list = [5, 6, 8, 9, 10, 11, 12, 13, 14]
s2up = [5, 6, 8, 9]
s2bottom = [10, 11, 12, 13, 14]
dir_data = "/home/gelijian/EAST/shot_data/"
DGZ_type = "APV"
if DGZ_type == "751":
    bias = 0.5
if DGZ_type == "APV":
    bias = 0
shotlist = np.arange(72000, 77000)
divergence = []
m = sa.TOFEDdata()
m.set_DGZ_type(DGZ_type)
for ch2 in s2list:
    if ch2 in s2up:
        gamma_peak = 4.1 + bias
    if ch2 in s2bottom:
        gamma_peak = 4.1 + bias
    for ch1 in s1list:
        data_integral = np.zeros((1, 3))
        for shot in shotlist:
            dir_shot = os.path.join(dir_data, "%d" % shot)
            if not os.path.exists(dir_shot):
                continue
            m.set_dir_shot(dir_shot)
            m.load_board_offset()
            data = m.load_pair(ch1, ch2)
            if data is not None:
                data_integral = np.vstack((data_integral, data))
        
        toflist = data_integral[1:, 0]
        binedge = np.arange(-50, 50, 0.4)
        binmiddle = 0.5 * (binedge[:-1] + binedge[1:])
        (ntof, bins) = np.histogram(toflist, bins = binedge)
        binpeak = binmiddle[(ntof == ntof.max())].mean()
        index = (binmiddle < (binpeak + 6)) * (binmiddle > (binpeak - 6))
        x = binmiddle[index]
        y = ntof[index]
        p0 = (ntof.max(), binpeak, 2.0)
        plsq= leastsq(residuals, p0, args = (y, x))
        a, miu, sigma = plsq[0] 
        y_fit = func(x, plsq[0])
        div = gamma_peak - miu
        fwhm = 2.355 * sigma
        divergence.append((ch1, ch2, div))
        print "s1:%d s2:%d binpeak:%g div: %g fwhm: %g" % (ch1, ch2, miu, div, fwhm)
        plt.figure()
        plt.plot(binmiddle, ntof, "k-o", label = "s1:%d s2:%d" % (ch1, ch2))
        plt.plot(x, y_fit, "r-", lw = 2, label = "fit")
        plt.title("s1:%d s2:%d binpeak:%g div: %g" % (ch1, ch2, miu, div))
        plt.xlabel("Time-of-flight [ns]")
        plt.ylabel("Counts")
        plt.xlim(-10, 30)
        plt.ylim(0, 1.4 * ntof.max())
        plt.legend()
        plt.show()

divergence = np.array(divergence)
np.savetxt("%s_divergence" % DGZ_type, divergence, fmt = "%g")
print divergence



