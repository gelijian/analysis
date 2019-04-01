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
        s_temp = str(E / keV) + ' ' + str((float((spectrum[E]) / ( second**(-1))))) + '\n'
        f.write(s_temp)
     except:
        print('An error occured while writing')

####################################################################################################################
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

reaction = DDN3HeReaction()
whichProduct = 1
Emin, Emax, bins = 500*keV, 3520*keV, 151
delta_E = (Emax - Emin)/bins
samples = 1000000

#########################################################
torus = Torus(R = 1.88*meters, k = 1.8)

# the NUBEAM profiles are read as follows:

## create output directory
device = "TOFED"
# device = "EJ301"
campaign = "2018"
dir_data = os.path.join("/home/gelijian/EAST/shot_data")
dir_LOS = os.path.join(dir_data, "LOS")
shot = 81513
losfile = os.path.join(dir_LOS, "los_%s.File" % (device))
dir_shot = os.path.join(dir_data, campaign, "%d" % shot)
dir_sim = os.path.join(dir_shot, "simulation")
dir_nubeam = os.path.join(dir_sim, "nubeam")
dir_device = os.path.join(dir_sim, device)
dir_NES = os.path.join(dir_device, "NES")
coords_file = os.path.join(dir_nubeam, "irregular_grid.file")
fbm_file = os.path.join(dir_nubeam, "fbm.file")
if (not os.path.exists(dir_device)):
    os.mkdir(dir_device)
if (not os.path.exists(dir_NES)):
    os.mkdir(dir_NES)
f_intensity = file(os.path.join(dir_NES, 'relative_intensity'), 'w')
log.info('device: %s The neutron energy spectra for %s shot will be calculated...' % (device, shot))

#set thermal profile
n_thermal = 4.5e+19/meters**3
Ti = 1.5 * keV
Te = 1.5 * keV
coordinates = WFtest.coordinates(coords_file)
d_profile = WFtest.thermal_profile(Ti, Te, n_thermal, coordinates)
b_profile = WFtest.fbm_profile(fbm_file, coordinates)

# Now we set up and launch the simulation
Randomizer.seed(42)
Kinematics.setMode(RELATIVISTIC)


# thermal-thermal

log.info('Calculating thermal-thermal spectrum...')
cells = lineOfSight(losfile, d_profile, d_profile)
thermal = CalculateVolumeSpectrum(reaction, whichProduct, cells,
                                   Emin, Emax, bins, samples,
                                   E1range = (0.0*MeV, 1.0*MeV),
                                   E2range = (0.0*MeV, 1.2*MeV),
                                   Bdirection = Clockwise)
thermal = thermal/2.0
log.info('done')
export(thermal, os.path.join(dir_NES, 'thermal'), Emin, Emax, delta_E)
thermal_intensity = thermal.sum()
f_intensity.write('thermal intensity:   \n')
string = 'thermal intensity (s**(-1)):   ' + str(float(thermal_intensity/(second**(-1)))) + '\n'
f_intensity.write(string)
print('thermal intensity (s**(-1)): %.2e' % float(thermal_intensity/(second**(-1))))

# beam-thermal
log = logging.getLogger()
log.info('Calculating beam-thermal spectrum...')
cells = lineOfSight(losfile, d_profile, b_profile)
beamthermal = CalculateVolumeSpectrum(reaction, whichProduct, cells,
                                   Emin, Emax, bins, samples,
                                   E1range = (0.0*MeV, 1.0*MeV),
                                   E2range = (0.0*MeV, 1.2*MeV),
                                   Bdirection = Clockwise)
log.info('done')
beamthermal = beamthermal/2.0
export(beamthermal, os.path.join(dir_NES, 'beam-thermal'), Emin, Emax, delta_E)
beamthermal_intensity = beamthermal.sum()
f_intensity.write('beam-thermal intensity:   \n')
string = 'beam-thermal intensity (s**(-1)):   ' + str(float(beamthermal_intensity/(second**(-1)))) + '\n'
f_intensity.write(string)


# beam-beam
log = logging.getLogger()
log.info('Calculating beam-beam spectrum...')
cells = lineOfSight(losfile, b_profile, b_profile)
beambeam = CalculateVolumeSpectrum(reaction, whichProduct, cells,
                                   Emin, Emax, bins, samples,
                                   E1range = (0.0*MeV, 1.0*MeV),
                                   E2range = (0.0*MeV, 1.2*MeV),
                                   Bdirection = Clockwise)
beambeam = beambeam/2.0/4.0
log.info('done')
export(beambeam, os.path.join(dir_NES, 'beam-beam'), Emin, Emax, delta_E)
beambeam_intensity = beambeam.sum()
f_intensity.write('beam-beam intensity:   \n')
string = 'beam-beam intensity (s**(-1)):   ' + str(float(beambeam_intensity/(second**(-1)))) + '\n'
f_intensity.write(string)


# direct_total
direct = thermal + beamthermal + beambeam
export(direct, os.path.join(dir_NES, 'direct'), Emin, Emax, delta_E)
total_intensity = direct.sum()
f_intensity.write('direct intensity:   \n')
string = 'direct intensity (s**(-1)):   ' + str(float(total_intensity/(second**(-1)))) + '\n'
f_intensity.write(string)

####################################################################
thermal_relative_intensity = thermal.sum()/direct.sum()
f_intensity.write('thermal relative intensity:   \n')
string = 'thermal relative intensity:   ' + str(float(thermal_relative_intensity)) + '\n'
f_intensity.write(string)

beamthermal_relative_intensity = beamthermal.sum()/direct.sum()
f_intensity.write('beam-thermal relative intensity:   \n')
string = 'beam-thermal relative intensity:   ' + str(float(beamthermal_relative_intensity)) + '\n'
f_intensity.write(string)

beambeam_relative_intensity = beambeam.sum()/direct.sum()
f_intensity.write('beam-beam relative intensity:   \n')
string = 'beam-beam relative intensity:   ' + str(float(beambeam_relative_intensity)) + '\n'
f_intensity.write(string)



