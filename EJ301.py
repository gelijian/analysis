import json
import os
import numpy as np
import myplt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import shotanalysis as sa
plt.style.use("classic")
matplotlib.rcParams['font.size'] = 18

instrument = "EJ301"
campaign = "2018"
shot = 81512
# k = 6.9
k = 19.5
dir_shot = os.path.join("/home/gelijian/EAST/shot_data", campaign, "%d" % shot)
dir_figure = "/home/gelijian/EAST/shot_data/figure"
dir_parameters, dir_NES = sa.generate_dirs(dir_shot, instrument)
Enlist = np.arange(500, 3520, 20)
dir_RF = "/home/gelijian/EAST/shot_data/RF/EJ301"
sa.PHdata.set_dir_RF(dir_RF)
binedge, binmiddle, Enlist, matrix_RF = sa.PHdata.load_RF(Enlist)

# sim data
NES_sim_dict, phs_sim_dict = sa.load_NES_sim(dir_NES, matrix_RF)

# exp data
file_exp = os.path.join(dir_shot, "EJ301_data")
m = sa.PHdata()
m.loaddata(file_exp, k=k, b=0)
range_Eee = np.array([100, 1500])
range_psd = np.array([0.205, 0.35])
idx_n = m.PSD(range_Eee, range_psd)
phs_exp, bins = np.histogram(m.ph[idx_n], bins=binedge)

# n/gamma PSD
binedge_ph, binmiddle_ph = sa.generate_bins(0, 1000, 5)
binedge_psd, binmiddle_psd = sa.generate_bins(0, 0.4, 0.002)
fig = plt.figure()
plt.hist2d(m.ph, m.psd, bins=[binedge_ph, binedge_psd], norm=LogNorm())
plt.colorbar()
plt.ylim(0, 0.4)
plt.ylabel("PSD factor [a.u.]")
plt.xlabel("Light output [keV]")
plt.tight_layout()
plt.savefig(os.path.join(dir_figure, "png", "PSD_%s_%d.png" % (instrument, shot)), dpi=600)
plt.show()

# En spectrum
# r = 1.0 / NES_sim_dict["total"].max()
plt.figure()
for key, NES in NES_sim_dict.items():
    plt.step(Enlist, NES, sa.CPT_cfg[key]["style"], label=sa.CPT_cfg[key]["label"], lw=3)
plt.xlabel("En [keV]")
plt.ylabel("dN/dE [a.u.]")
plt.xlim(1500, 3500)
plt.ylim(0, 1.0)
plt.legend(loc="best", fontsize=16)
plt.savefig(os.path.join(dir_figure, "eps", "NES_%s_%d.eps" % (instrument, shot)), dpi=600)
plt.show()

# PHSexp vs sim
# log
idx = (binmiddle > 400) & (binmiddle < 850)
r, cash = sa.min_cash(phs_exp[idx], phs_sim_dict[sa.Component.total][idx])
print(r, cash)
plt.figure()
plt.errorbar(binmiddle, phs_exp, yerr=np.sqrt(phs_exp), fmt="ko", label="Measurement", markersize=7, capsize=4)
for key, y_sim in phs_sim_dict.items():
    plt.plot(binmiddle, y_sim * r, sa.CPT_cfg[key]["style"], label=sa.CPT_cfg[key]["label"], lw=4)
plt.legend(loc="best", fontsize=16)
plt.xlabel("Light output [keVee]")
plt.ylabel("Counts")
plt.xlim(200, 900)
plt.ylim(0, 2000)
plt.ylim(10, 10000)
plt.yscale("log")
plt.savefig(os.path.join(dir_figure, "eps", "PHS_%s_%d.eps" % (instrument, shot)), dpi=600)
plt.show()

# linear
plt.figure()
plt.errorbar(binmiddle, phs_exp, yerr=np.sqrt(phs_exp), fmt="ko", label="Measurement", markersize=7, capsize=4)
for key, y_sim in phs_sim_dict.items():
    plt.plot(binmiddle, y_sim * r, sa.CPT_cfg[key]["style"], label=sa.CPT_cfg[key]["label"], lw=4)
plt.legend(loc="best", fontsize=16)
plt.xlabel("Light output [keVee]")
plt.ylabel("Counts")
plt.xlim(200, 900)
plt.ylim(0, 2000)
plt.savefig(os.path.join(dir_figure, "eps", "PHS_linear_%s_%d.eps" % (instrument, shot)), dpi=600)
plt.show()



########## neutron flux #############
# file_zz = os.path.join(dir_parameters, "zz7_campbell.txt")
# binfluxwidth = 0.2  # unit: s
# binflux = np.arange(0, 20, binfluxwidth)
# binfluxmiddle = 0.5 * (binflux[1:] + binflux[:-1])
# timestamp = m.timestamp[idx_n] / math.pow(10, 9)
# histflux, bins = np.histogram(timestamp, bins=binflux)
# histflux = histflux / binfluxwidth
# error = np.sqrt(histflux / binfluxwidth)
# plt.figure()
# plt.errorbar(binfluxmiddle, histflux, yerr=error, fmt="ko", label="EJ301 ", markersize=5)
# if os.path.exists(file_zz):
#     data_zz = np.loadtxt(file_zz)
#     ratio = histflux.max() / data_zz[:, 1].max()
#     plt.plot(data_zz[:, 0], data_zz[:, 1] * ratio, "r--", lw=4, label="Fission chambe (rescaled)")
# plt.xlabel("Time [s]")
# plt.ylabel("Count rate [cps] ")
# plt.xlim(1, 10)
# plt.ylim(0, histflux.max() * 1.3)
# plt.legend()
# plt.tight_layout()
# #~ plt.savefig(os.path.join(dir_sim, "n_flux_%d.%s" % (shotnum, fmt_fig)), fmt = fmt_fig, dpi = 600)
# plt.show()
# plt.close()