#!/usr/bin/python

# Copyright (C) 2006, 2007 Luigi Ballabio

# This file is part of ControlRoom.

# ControlRoom is free software: you can redistribute it and/or modify it
# under the terms of its license.
# You should have received a copy of the license along with this program;
# if not, please email lballabio@users.sourceforge.net

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the license for more details.

###################################################################################################################
def export(spectrum, name, energy_min, energy_max, dE):  #Export a spectrum to a txt file

  f = file(name, 'w')
  energy_list = []
  current_energy = energy_min
  while (current_energy <= energy_max):
     energy_list.append(current_energy)
     current_energy += dE

  for E in energy_list:
     try:
        s_temp = str(E / MeV) + '     ' + str((float((spectrum[E]) / ( second**(-1))))) + '\n'
        f.write(s_temp)
     except:
        print 'An error occured while writing'

####################################################################################################################
import time
import numpy as np
from ControlRoom import *
import WFtest
import sys, logging, os

fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
logging.root.addHandler(hnd)
logging.root.setLevel(logging.INFO)
log = logging.getLogger()

################ set the output directory path #####################
shotnumber = 75051
instrument = "TOFED"
coords_file = os.path.join("%d" % (shotnumber), "irregular_grid.file")
losfile = os.path.join("LOS_file", "los_%s.File" % instrument)
log.info("Calculate weight function of %d shot for %s" % (shotnumber, instrument))
log.info("coords file is %s" % (coords_file))
log.info("line of sight file is %s" % (losfile))
dir_WF = os.path.join("%d" % (shotnumber), "WF")
dir_inst = os.path.join(dir_WF, instrument)
dir_NES_WF = os.path.join(dir_inst, "NES")
if (not os.path.exists(dir_WF)):
    os.mkdir(dir_WF)
    log.info("%s has been created" % dir_WF)
if (not os.path.exists(dir_inst)):
    os.mkdir(dir_inst)
    log.info("%s has been created" % dir_inst)
if (not os.path.exists(dir_NES_WF)):
    os.mkdir(dir_NES_WF)
    log.info("%s has been created" % dir_NES_WF)

################ set the parameters of thermal plasma and beam ions ##### 
n_thermal = 3.6e+19/meters**3
T_thermal = 1.4 * keV
n_beam = 1.0e+17/meters**3
Emin, Emax, bins = 500*keV, 3520*keV, 151
dE = (Emax - Emin)/bins
Enlist = np.arange(500, 3520, 20)
Eblist = np.arange(10, 110, 5)
mulist = np.arange(-0.98, 1.0, 0.07)
np.savetxt(os.path.join(dir_inst, "Enlist"), Enlist, fmt = "%g")
np.savetxt(os.path.join(dir_inst, "Eblist"), Eblist, fmt = "%g")
np.savetxt(os.path.join(dir_inst, "mulist"), mulist, fmt = "%g")
log.info("number of Eb: %g, number of mu: %g" % (len(Eblist), len(mulist)))
#################### Now we set up and launch the simulation ################
####### claculate the neutron energy spectrum for each(Eb, mu) element ######
Randomizer.seed(42)
Kinematics.setMode(RELATIVISTIC)
reaction = DDN3HeReaction()
whichProduct = 1
samples = 1000000
coordinates = WFtest.coordinates(coords_file)
d_profile = WFtest.thermal_profile(T_thermal, T_thermal, n_thermal, coordinates)

for i in xrange(len(mulist)):
    for j in xrange(len(Eblist)):
        start = time.time()
        Eb = Eblist[j] * keV
        mu = mulist[i]
        log.info("mu: %g, beam energy: %g keV"%(mu, Eb / keV))
        log.info('Calculating beam-thermal spectrum...')
        b_profile = WFtest.monobeam_profile(Eb, mu, n_beam, coordinates)
        cells = lineOfSight(losfile, d_profile, b_profile)
        beamthermal = CalculateVolumeSpectrum(reaction, whichProduct, cells,
                                   Emin, Emax, bins, samples,
                                   E1range = (0.0*MeV, 1.0*MeV),
                                   E2range = (0.0*MeV, 1.2*MeV),
                                   Bdirection = Clockwise)
        
        log.info('done')
        beamthermal = beamthermal / 2.0
        filename = "mu_%d_Eb_%d" % (i, j)
        export(beamthermal, os.path.join(dir_NES_WF, filename), Emin, Emax, dE)
        beamthermal_intensity = beamthermal.sum()
        print 'beam-thermal intensity (s**(-1)): %.2e' % float(beamthermal_intensity/(second**(-1)))
        stop = time.time()
        print stop -start

################ generate the info file #############################
finfo = open(os.path.join(dir_inst, "WF_info"), "w")
finfo.write("shot number = %d\n" % (shotnumber))
finfo.write("Number of samples = %g\n"%(samples))
finfo.write("T_thermal = %g keV\n" % (T_thermal / keV))
finfo.write("n_thermal = %E / m-3\n" % (n_thermal / meters**-3))
finfo.write("n_beam = %E / m-3\n"%(n_beam / meters**-3))
finfo.write("Grid info are in the files: Eblist, mulist\n")
finfo.write("Ebmin = %g keV, Ebmax = %g keV\n"%(Eblist.min(), Eblist.max()))
finfo.write("mumin = %g, mumax = %g"%(mulist.min(), mulist.max()))
finfo.close()
