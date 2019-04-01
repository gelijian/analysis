import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.stats import chisquare
import shotanalysis as sa
plt.style.use("classic")
matplotlib.rcParams['font.size'] = 18


def LOP_s1(tof, theta):
    """ Function doc """
    b0, b1, b2, b3 = -2.97, 69.13, -38.58, 56.2
    constant = 5228.157
    TOFradius = 0.75
    En = constant * ((2 * TOFradius) ** 2) / tof ** 2
    theta = np.radians(theta)
    Ep = En * np.sin(theta) ** 2
    loutput = b0 + b1 * Ep + b2 * Ep ** 2 + b3 * Ep ** 3
    return loutput


device = "TOFED"
campaign = "2018"
shot = 81512
dir_data = os.path.join("/home/gelijian/EAST/shot_data/", campaign)
dir_figure = os.path.join("/home/gelijian/EAST/shot_data/figure")
dir_shot = os.path.join(dir_data, "%d" % shot)
dir_RF = "/home/gelijian/EAST/RF/TOFED"
dir_parameters, dir_NES = sa.generate_dirs(dir_shot, device)
Enlist = np.arange(500, 3520, 20)
sa.TOFEDdata.set_dir_RF(dir_RF)
# binedge = np.arange(-200, 200, 0.5)
# fwhm_DAQ = np.sqrt(0.8**2 + 0.8**2 + 0.8**2)
# sa.TOFEDdata.cal_RF(binedge, fwhm_DAQ)
binedge, binmiddle, Enlist, matrix_RF = sa.TOFEDdata.load_RF(Enlist)

# sim data
NES_sim_dict, tof_sim_dict = sa.load_NES_sim(dir_NES, matrix_RF)


# exp data
tof_cfg = {
    sa.Digitizer.V1751: {
        sa.RingType.up: {"th_s1": 50, "p1": (10, 20), "p2": (55, 30)},
        sa.RingType.bottom: {"th_s1": 50, "p1": (15, 25), "p2": (60, 40)}
    },
    sa.Digitizer.APV8508: {
        sa.RingType.up: {"th_s1": 180, "p1": (15, 20), "p2": (50, 30)},
        sa.RingType.bottom: {"th_s1": 180, "p1": (12, 25), "p2": (55, 40)},
    }
}

# shotlist = np.loadtxt("goodshot")[:, 0]
# shotlist = [81512]
shotlist = np.arange(81510, 81515)

data_exp = np.empty((0, 5))
for shot in shotlist:
    dir_shot = os.path.join(dir_data, "%d" % shot)
    if not os.path.exists(dir_shot):
        continue
    filename = os.path.join(dir_shot, "TOFED_data")
    data = np.loadtxt(filename)
    data_exp = np.vstack((data_exp, data))

tof_exp_list = []
tof_kin_list = []
binedge_tof, binmiddle_tof = sa.generate_bins(-200, 200, 3)
binedge_ql, binmiddle_ql = sa.generate_bins(0, 5000, 30)
t = np.arange(10, 200, 0.1)

for digitizer in sa.Digitizer:
    for ring in sa.RingType:
        idx_digitizer = data_exp[:, 4] == digitizer.value
        idx_ring = data_exp[:, 3] == ring.value
        data = data_exp[idx_digitizer & idx_ring, :]
        tof = data[:, 0]
        qls1 = data[:, 1]

        p1 = tof_cfg[digitizer][ring]["p1"]
        p2 = tof_cfg[digitizer][ring]["p2"]
        idx1 = qls1 > p1[0] * LOP_s1(tof, p1[1])
        idx2 = qls1 < p2[0] * LOP_s1(tof, p2[1])
        # i3 = tof < 50
        # i4 = tof > 90
        # idx = (i1 & i2) | i3 | i4
        # tof_kin = np.append(tof_kin, tof[idx] + offset[i])
        tof_exp_list = np.append(tof_exp_list, tof)
        tof_kin_list = np.append(tof_kin_list, tof[idx1 & idx2])
        plt.figure()
        plt.plot(t, p1[0] * LOP_s1(t, p1[1]), "r-", lw=2)
        plt.plot(t, p2[0] * LOP_s1(t, p2[1]), "r-", lw=2)
        plt.hist2d(tof, qls1, bins=(binedge_tof, binedge_ql), norm=LogNorm())
        plt.colorbar()
        plt.title("%s of %s" % (ring.name, digitizer.name))
        plt.xlabel("time-of-flight [ns]")
        plt.ylabel("Qlong of s1")
        # plt.xlim(-50, 150)
        plt.show()
        plt.close()


# En spectrum
r = 1.0 / NES_sim_dict[sa.Component.total].max()
plt.figure()
for key, NES in NES_sim_dict.items():
    plt.step(Enlist, NES * r, sa.CPT_cfg[key]["style"], label=sa.CPT_cfg[key]["label"], lw=3)
plt.xlabel("En [keV]")
plt.ylabel("dN/dE [a.u.]")
plt.xlim(1500, 3500)
plt.ylim(0, 1.2)
plt.legend(loc="best", fontsize=16)
plt.savefig(os.path.join(dir_shot, "NES_%s_%d.eps" % (device, shot)), dpi=600)
plt.show()


# TOF exp
tof_exp, bins = np.histogram(tof_exp_list, bins=binedge)
tof_kin, bins = np.histogram(tof_kin_list, bins=binedge)
plt.figure()
plt.errorbar(binmiddle, tof_exp, yerr=np.sqrt(tof_exp), fmt="ko", lw=1.5, label="Measurement", markersize=7, capsize=4)
plt.plot(binmiddle, tof_kin, "r-", lw = 2, label="DKS")
plt.xlabel("time-of-flight [ns]")
plt.ylabel("Counts / bin")
plt.xlim(-100, 120)
plt.ylim(0, )
plt.legend(fontsize=17)
plt.savefig(os.path.join(dir_figure, "TOFED_exp_sim.eps"), dpi=600)
plt.show()


# TOF exp vs sim
idx = sa.inrange(binmiddle, (30, 50))
bg = np.floor(tof_exp[idx].mean()) + 0.5
idx = sa.inrange(binmiddle, (65, 85))
tof_exp = np.abs(tof_exp - bg)
r, cash = sa.min_cash(tof_exp[idx], tof_sim_dict[sa.Component.total][idx])
print(r, cash)
plt.figure()
plt.errorbar(binmiddle, tof_exp, yerr=np.sqrt(tof_exp), fmt="ko", lw=1.5, label="Measurement", markersize=7, capsize=4)
for key, tof_sim in tof_sim_dict.items():
    plt.plot(binmiddle, tof_sim * r, sa.CPT_cfg[key]["style"], label=sa.CPT_cfg[key]["label"], lw=3)
plt.xlabel("time-of-flight [ns]")
plt.ylabel("Counts / bin")
plt.xlim(60, 90)
plt.ylim(0, tof_exp[idx].max() * 1.1)
plt.legend(fontsize=17)
# plt.savefig("TOFED_exp_sim_neutron.eps", dpi=600)
plt.show()


