import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

plt.style.use("classic")
matplotlib.rcParams['font.size'] = 17

def Get_En (tof):
    """ En in unit MeV """
    TOFradius = 0.75
    constant = 5228.157
    En = constant * ((2 * TOFradius) **2) / tof ** 2
    return En
 

        Ep = En * (np.sin(flight_angle / 180.0 * np.pi) ** 2)
        return self.protonrespfun(Ep)

def LOP_s1 (tof, theta, b0 = 0, b1 = 69.13, b2 = -38.58, b3 = 56.2):
    """ Function doc """
    TOFradius = 0.75
    constant = 5228.157
    En = constant * ((2 * TOFradius) **2) / tof ** 2
    Ep = En * (np.sin(theta / 180.0 * np.pi) ** 2)

    return b0 + b1*Ep + b2*Ep**2 + b3*Ep**3
    
print LOP_s1(0.3)
print LOP_s1(1.0)
x = np.arange(0, 2000, 1) / 1000.0
y = LOP_s1(x)
plt.plot(x, y)
plt.xlim(0, 2.4)
plt.show()
