# -*- coding: utf-8 -*-
"""
plotscript for qpu-results
"""
import numpy as np
import os
from operator import itemgetter
import matplotlib.pyplot as plt

path = 'C:/Users/regin/Nextcloud/Postdoc/Code/numerical_results/QPUResults/Ehningen22-06-22/'

# load results from file
qpu_results = np.loadtxt(path+'averaged_results_qpu2022-06-23.dat')
#qpu_results = np.loadtxt(path+'QPU/BitFlipDetectionIBMExpErrorQubit02022-05-27.dat')


#qpu_results = np.loadtxt(path+'results/BitFlipDetectionQPUErrorQubit0_32021-12-21.dat')
#sim_results = np.loadtxt(path+'compare/BitFlipDetectionIBMSimErrorQubit02021-12-21.dat')
mysim_results = np.loadtxt(path+'averaged_results_sim2022-06-23.dat')
#mysim_results = np.loadtxt(path+'simulator/BitFlipDetectionIBMSimErrorQubit02022-05-27.dat')



# sort ascending by logical error rate
#sorted_sim_results = np.array(sorted(sim_results, key=itemgetter(1)))
sorted_mysim_results = np.array(sorted(mysim_results, key=itemgetter(1)))
sorted_qpu_results = np.array(sorted(qpu_results, key=itemgetter(1)))

#  make single array to compare performance and plot result
all_results = mysim_results[:,0:2]
all_results = np.append(all_results, qpu_results[:,1:2], axis=1)
#all_results = np.append(all_results, sim_results[:,1:2], axis=1)
all_results = np.append(all_results, mysim_results[:,2:], axis=1)
all_results = np.array(sorted(all_results, key=itemgetter(1)))
all_results = all_results[0:20]

print(sorted_qpu_results[:,1])

# plot results 
x = np.arange(len(all_results))
y = np.arange(len(qpu_results))

plt.figure(figsize=(10.0,4.0))
plt.xlabel('number of iteration over layout')
plt.ylabel('logical error rates')
plt.bar(y+1,qpu_results[:,1], label='Quantum processor', color='tab:blue')
plt.bar(y+1,mysim_results[:,1], label='Simulator', color='tab:green', alpha=0.7)
plt.legend()
#plt.xticks(np.arange())
plt.savefig('comparison_sim_exp.pdf')
plt.show()
#plt.savefig('qpu_plot.pdf')

plt.figure(figsize=(8.0,4.0))
plt.xticks(np.arange(1, 21, 1))
plt.xlabel('different initial layouts')
plt.ylabel('logical error rates')
plt.bar(x+1,all_results[:,2], label='logical error rate, QPU', fc=(1, 0, 0, 0.7))
plt.bar(x+1,all_results[:,1], label='logical error rate, simulator', fc=(0, 0, 1, 0.7))
plt.legend()
plt.show()

plt.figure(figsize=(8.0,4.0))
plt.xticks(np.arange(1, 21, 1))
plt.bar(x+1,all_results[:,7], label='Readout Error')
plt.bar(x+1,all_results[:,4], label='average CNOT error')
plt.bar(x+1,all_results[:,6], label='X error')
plt.xlabel('number of iteration over layout')
plt.ylabel('gate errors')
plt.legend()
plt.show()

plt.figure(figsize=(8.0,4.0))
plt.xticks(np.arange(1, 21, 1))
plt.bar(x+1,all_results[:,5], label='average T2',fc=(0, 0, 1, 0.7))
plt.xlabel('number of iteration over layout')
plt.ylabel('average T2')
plt.legend()
plt.show()

# plt.figure(figsize=(8.0,4.0))
# plt.bar(x,all_results[:,6], label='X Error')
# plt.xlabel('number of iteration over layout')
# plt.ylabel('X Error')
# plt.legend()
# plt.show()

# plt.figure(figsize=(8.0,4.0))
# plt.bar(x,all_results[:,7], label='Readout Error')
# plt.xlabel('number of iteration over layout')
# plt.ylabel('average readout error')
# plt.legend()
# plt.show()
