import sys
import os
import numpy as np
import matplotlib.pyplot as plt

campaign = "2018"
shot = 75051
instrument = "TOFED"
#instrument = "EJ301"
dir_root = "/home/gelijian/EAST/shot_data"
dir_shot = os.path.join("/home/gelijian/EAST/shot_data", campaign, "%d" % shot)
dir_device = os.path.join(dir_shot, "simulation", instrument)
dir_NES_WF = os.path.join(dir_device, "WF/NES")
dir_instrument_WF = os.path.join(dir_device, "WF/instrument")
dir_instrument_RF = os.path.join("home/gelijian/EAST/", instrument)
dir_instrument_RF_elements = os.path.join(dir_instrument_RF, "elements")
Enlist = np.loadtxt(os.path.join(dir_instrument_RF, "Enlist"))
binmiddle = np.loadtxt(os.path.join(dir_instrument_RF, "binmiddle"))
Eblist = np.loadtxt(os.path.join(dir_device, "Eblist"))
mulist = np.loadtxt(os.path.join(dir_device, "mulist"))
n_G4sim = 5000000.0 # G4 simulation for instrument RF functions(Response functions)

if (not os.path.exists(dir_instrument_WF)):
    os.mkdir(dir_instrument_WF)
    print "%s has been created!" % (dir_instrument_WF)

##########  Load instrument Response function ################
dim_En = len(Enlist)
dim_binmiddle = len(binmiddle)
matrix_instrument_RF = np.matrix(np.zeros((dim_binmiddle, dim_En)))
for i in xrange(dim_En):
    En = Enlist[i]
    filename = os.path.join(dir_instrument_RF_elements, "En_%dkeV" % (En))
    RF_i = np.loadtxt(filename).reshape(-1, 1) / n_G4sim
    matrix_instrument_RF[:, i] = RF_i

########## calculate the weight function for each (mu, Eb) component ################
for i in xrange(len(mulist)):
    for j in xrange(len(Eblist)):
        mu = mulist[i]
        Eb = Eblist[j]
        print "calculate the tof weight function for mu = %g, Eb = %g" % (mu, Eb)
        filename = os.path.join(dir_NES_WF, "mu_%d_Eb_%d" % (i, j))
        NES = np.loadtxt(filename)[:, 1].reshape(-1, 1)
        WF_instrument = matrix_instrument_RF * NES
        np.savetxt(os.path.join(dir_instrument_WF, "mu_%d_Eb_%d" % (i, j)), WF_instrument, fmt = "%g")
        print "finished"
np.savetxt(os.path.join(dir_device, "binmiddle"), binmiddle, fmt = "%g")
