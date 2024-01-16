# -*- coding: utf-8 -*-
"""
Created on Thu May 12 07:09:15 2022

@author: regina
"""

import numpy as np
import matplotlib.pyplot as plt

#res1 = np.loadtxt('simplemodel_t1=t2_dampingerror_average.dat')
#res2 = np.loadtxt('simplemodel_t1=t2_depoalizingerror_average.dat')

res1 = np.loadtxt('bitflip_dampingerror_average_18-5-22.dat')
res2 = np.loadtxt('bitflip_depolerror_average_18-5-22.dat')



fig = plt.figure(figsize=(10.0,4))
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

x1 = res1[:,0]*1000000
x2 = res2[:,0]

ax1.set_xlim(min(x1), max(x1))
ax2.set_xlim(min(x2), max(x2))

# =============================================================================
# ax1.set_xticks(np.arange()) 
# ax1.set_xticklabels([1,4,5], fontsize=12)
# =============================================================================

ax1.plot(x1,res1[:,1], color='tab:red', marker='.',  label='NV-C, damping error')
ax1.plot(x1,res1[:,2], color='tab:green', marker='.', label='SC, damping error')
ax1.set_xlabel(r"Decoherence time $T_2 \quad [\mu s]$")
plt.arrow(0.07,0.42,0.0,0.05, length_includes_head=True, head_length=0.02, color='gray',width=0.0005)


ax2.plot(x2,res2[:,1], color='tab:red', marker='x', linestyle='dashed', label='NV-C, depolarizing error')
ax2.plot(x2,res2[:,2], color='tab:green', marker='x', linestyle='dashed', label='SC, depolarizing error')
ax2.set_xlabel(r"$p_{depol}$")
#ax2.spines['top'].set_color('#dddddd')
#ax2.spines['bottom'].set_color('#dddddd')
#ax2.xaxis.label.set_color('red') # change only the label


handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
plt.legend(handles1+handles2, labels1+labels2,loc='upper left')

ax1.set_ylabel('logical error rates')
#plt.legend()
plt.savefig('bitflip_compareplot.pdf')
plt.show()


# =============================================================================
# new_tick_locations = np.array([.2, .5, .9])
# 
# def tick_function(X):
#     V = 1/(1+X)
#     return ["%.3f" % z for z in V]
# 
# ax2.set_xlim(ax1.get_xlim())
# ax2.set_xticks(new_tick_locations)
# ax2.set_xticklabels(tick_function(new_tick_locations))
# ax2.set_xlabel(r"Modified x-axis: $1/(1+X)$")
# plt.show()
# =============================================================================
