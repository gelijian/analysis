import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sys
import os
plt.style.use("classic")
matplotlib.rcParams['font.size'] = 18

dir_data = os.path.join("/home/gelijian/EAST/shot_data")
campaign = "2017"
device = "TOFED"
device = "EJ301"
# device = "Stilbene"
shot = 75164
dir_MCNP = os.path.join(dir_data, "MCNP", device)
dir_shot = os.path.join(dir_data, campaign, "%d" % shot)
dir_device = os.path.join(dir_shot, "simulation", device)
dir_NES = os.path.join(dir_device, "NES")
print("Scatter component of %s at shot %d will be calculated" % (device, shot))
file_total_mcnp = os.path.join(dir_MCNP, "total")
file_direct_mcnp = os.path.join(dir_MCNP, "direct")
file_scatter_mcnp = os.path.join(dir_MCNP, "scatter")
total_mcnp = np.loadtxt(file_total_mcnp)[:, 1]
direct_mcnp = np.loadtxt(file_direct_mcnp)[:, 1]
scatter_mcnp = np.loadtxt(file_scatter_mcnp)[:, 1]
# scatter_mcnp = np.abs(total_mcnp - direct_mcnp)
Enlist = np.loadtxt(file_total_mcnp)[:, 0]
idx = Enlist > 1500

file_direct = os.path.join(dir_NES, "direct")
direct = np.loadtxt(file_direct)[:, 1]
ratio = direct.sum() / direct_mcnp.sum()
if device is "EJ301":
    reduced_ratio = 1.5
elif device is "TOFED":
    reduced_ratio = 0.8
else:
    print("input TOFED or EJ301")
    sys.exit(0)
scatter = scatter_mcnp * ratio * reduced_ratio
data_scatter = np.zeros((len(Enlist), 2))
data_scatter[:, 0] = Enlist
data_scatter[:, 1] = scatter

data_total = np.zeros((len(Enlist), 2))
data_total[:, 0] = Enlist
data_total[:, 1] = direct + scatter
np.savetxt(os.path.join(dir_NES, "total"), data_total, fmt="%g")
np.savetxt(os.path.join(dir_NES, "scatter"), data_scatter, fmt="%g")

## plot mcnp results
plt.figure()
plt.step(Enlist, scatter_mcnp, label = "scatter", lw = 2)
plt.step(Enlist, direct_mcnp, label = "direct", lw = 2)
plt.xlabel("En [keV]")
plt.ylabel("Counts")
plt.xlim(1500, )
plt.ylim(0, direct_mcnp.max() * 1.3)
plt.title("MCNP")
plt.legend()
plt.show()
plt.close()

## plot NES
filegenesislist = ["total", "scatter", "direct", "beam-beam", "beam-thermal", "thermal"]
labellist = ["total", "scatter", "direct", "bb", "bt", "tt"]
plt.figure()
ax = plt.gca()
for i in range(0, len(filegenesislist)):
    filename = os.path.join(dir_NES, filegenesislist[i])
    data = np.loadtxt(filename)
    plt.step(data[:, 0], data[:, 1], label = labellist[i], lw = 2) 
plt.xlabel("En [keV]")
plt.ylabel("Counts")
plt.xlim(1500, )
plt.legend()
plt.show()
plt.close()

