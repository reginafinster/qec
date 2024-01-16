# -*- coding: utf-8 -*-
"""
Created on Fri May  6 08:41:13 2022

@author: regin
"""

import numpy as np
import matplotlib.pyplot as plt

path = 'C:/Users/regin/Nextcloud/Postdoc/Code/numerical_results/Results_Simulator/PhaseFlipCode/'
aresults = np.loadtxt(path+'phaseflip_depol_compare.dat')


x = aresults[:,0]
plt.figure(figsize=(10.0,4))
#plt.title('simulation of the Phaseflip-ECC with different device properties')
#plt.xlabel('depolarizing error')
plt.xlabel(r"$p_{depol}$")
plt.ylabel('logical error rates')
plt.xlim(min(x), max(x))


plt.plot(x,aresults[:,1], marker='x',  color='tab:red', label='NV-C')
plt.plot(x,aresults[:,2], marker='x',  color='tab:green', label='SC')
plt.legend(prop={'size': 8})
plt.savefig('phaseflip_depolerror1.pdf')
plt.show()