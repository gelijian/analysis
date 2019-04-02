import sys, logging, os
import numpy as np
import scipy.interpolate 
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.mlab import griddata
from matplotlib.colors import LogNorm
from ControlRoom import *
import WFtest
import myplt
plt.style.use("classic")
matplotlib.rcParams['font.size'] = 20

def _valid(line):
    return line.strip() and not line.startswith(r' //')

def _first_valid(file):
    line = file.readline()
    while not _valid(line):
        line = file.readline()
    return line

def _columns(file,transpose=False):
    data = []
    line = _first_valid(file)
    while _valid(line):
        data.append(tuple([float(x) for x in line.strip().split()]))
        line = file.readline()
    if transpose:
        return zip(*data)
    else:
        return data

def _floats(file):
    for line in file:
        for s in line.split():
            yield float(s)


#################### read data from the files #################
shot = 81512
dir_figure = "/home/gelijian/EAST/shot_data/figure"
dir_data = "/home/gelijian/EAST/shot_data/2018"
dir_shot = os.path.join(dir_data, "%d" % shot)
dir_nubeam = os.path.join(dir_shot, "simulation", "nubeam")
fbm_filename = os.path.join(dir_nubeam, "fbm.file")
fbm_file = open(fbm_filename)
E, dE = zip(*_columns(fbm_file))
mu, dmu = zip(*_columns(fbm_file))
rho, theta, volume = zip(*_columns(fbm_file))

Energy = np.array(E) / 1000.0   # eV to keV
dE = np.array(dE[0]) / 1000.0   # eV to keV
Mu = np.array(mu) 
dMu = np.array(dmu[0])
rho = np.array(volume)
volume = np.array(volume)  # cm^3
fbm_data = []
inputs = _floats(fbm_file)
for i in range(len(volume)):
    fs = []
    for y in mu:
        for x in E:
            fs.append(inputs.next())
    fs = np.array(fs)    # n/(cm^3 * eV * per_mu_bin)
    fs.shape = (50, 75)
    fbm_data.append(fs)

############## plot the fbm volume mean distribution ##############
fbm_total = 0
for i in xrange(len(fbm_data)):
    fbm_total = fbm_total + fbm_data[i] * volume[i]
fbm_volume_mean = (fbm_total / volume.sum())   # n/(cm^3 * eV * per_mu_bin)
fbm_volume_mean = fbm_volume_mean * pow(10, 3)  # n/(cm^3 * keV * per_mu_bin)
fig = plt.figure()
#levels = np.linspace(fbm_volume_mean.max() * pow(10, -2), fbm_volume_mean.max(), 12)
plt.contour(Energy, Mu, fbm_volume_mean, 10, colors = "k")
plt.contourf(Energy, Mu, fbm_volume_mean, 40, cmap = myplt.cmap)
plt.colorbar()
plt.ylim(-1, 1)
plt.xlim(0, )
plt.xlabel("E [keV]")
plt.ylabel("Pitch")
plt.yticks(np.arange(-1, 1.1, 0.2), fontsize = 16)
plt.xticks(fontsize = 16)
plt.tight_layout()
plt.savefig(os.path.join(dir_figure, "eps", 'FID_%d.eps' % shot), dpi = 600)
plt.show()
plt.close()

################ plot neutron emission profile #################
# coords_filename = os.path.join(dir_nubeam, "irregular_grid.file")
# fnprofile_filename = os.path.join(dir_nubeam, "neutron_profile")
# coords = np.loadtxt(coords_filename ,skiprows = 1)
# fnprofile = np.loadtxt(fnprofile_filename)
# rho0 = np.linspace(0, 1, num = len(fnprofile), endpoint = True)
# f1 = scipy.interpolate.interp1d(rho0, fnprofile)
# rho = coords[:, 0]
# R = coords[:, 2]
# Z = coords[:, 3]
# fn = f1(rho)
# R_list = np.linspace(0, 3, 200)
# Z_list = np.linspace(-1, 1, 200)
# fn_list = griddata(R, Z, fn, R_list, Z_list, interp='linear')

# first_wall_file = os.path.join("/home/gelijian/EAST/shot_data/EAST_wall/first_wall")
# first_wall = np.loadtxt(first_wall_file)
# fw = matplotlib.patches.Polygon(first_wall, closed = True, fill = False, lw = 3)

# plt.figure()
# ax = plt.gca()
# ax.add_patch(fw)
# levels = np.power(10, np.arange(11, 14.01, 0.05))
# plt.contourf(R_list, Z_list, fn_list, levels, norm = LogNorm())
# cbar = plt.colorbar()
# idx = np.arange(11, 15)
# cbar.set_ticks(np.power(10, idx))
# plt.xlabel("R [m]")
# plt.ylabel("Z [m]")
# plt.xlim(0.5, 3.0)
# plt.ylim(-1.2, 1.2)
# plt.savefig("n_profile.eps", dpi = 600)
# plt.show()











