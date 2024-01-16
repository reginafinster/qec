# -*- coding: utf-8 -*-
"""
Created on Fri May  6 08:41:13 2022

@author: regin
"""

import numpy as np
import matplotlib.pyplot as plt

path = 'C:/Users/regin/Nextcloud/Postdoc/Code/numerical_results/Results_Simulator/PhaseFlipCode/'

aresults = np.loadtxt(path+'phaseflip_damping_compare_t2=2t1.dat')
aresults1 = np.loadtxt(path+'phaseflip_damping_compare_t2=t1.dat')
aresults2 = np.loadtxt(path+'phaseflip_damping_compare_10t2=t1.dat')


x = aresults[:,0]*1000000
x1 = aresults1[:,0]*1000000
x2 = aresults2[:,0]*1000000
plt.figure(figsize=(10.0,4))
#plt.title('simulation of the Phaseflip-ECC with different device properties')
#plt.xlabel('depolarizing error')
plt.xlabel(r"Decoherence time $T_2 \quad [\mu s]$")
plt.ylabel('logical error rates')
plt.xlim(min(x), max(x))

#plt.xticks([0, 1, 2], ["a", "b", "c"])

plt.plot(x,aresults[:,2], color='#006400',marker='.',  linestyle='dashed', label='SC, $T_1=0.5T_2$')
plt.plot(x1,aresults1[:,2], color='tab:green', marker='.', label='SC, $T_1=T_2$')
plt.plot(x2,aresults2[:,2], color='#7CFC00',marker='.', linestyle='dotted', label='SC, $T_1=10T_2$')
plt.plot(x,aresults[:,1], color='#800000', linestyle='dashed', marker='.', label='NV-C, $T_1=0.5T_2$')
plt.plot(x1,aresults1[:,1], color='tab:red',marker='.',  label='NV-C, $T_1=T_2$')
plt.plot(x2,aresults2[:,1], color='#FFA07A',marker='.',  linestyle='dotted', label='NV-C,$T_1=10T_2$')
#plt.errorbar(x,aresults[:,2],yerr=0.0001)
#plt.plot(x,aresults[:,5], color='tab:cyan', linestyle='--', label='gate infidelities NV-center')
#plt.plot(x,aresults[:,6], color='tab:blue', linestyle='--', label='gate infidelities sup.proc.')
#plt.plot(x,theoretical_bound(p=x), label='analytical bound $p_e =\sum_{s=t+1}^{n} n!/(k!(n-k)!) p (1-p)^{n-s} $')
plt.legend(prop={'size': 8})
plt.savefig('phaseflip_dampingerror.pdf')
plt.show()