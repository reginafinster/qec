# -*- coding: utf-8 -*-
"""
Created on Wed May 18 20:41:26 2022

@author: regina
"""

import numpy as np
import os
from operator import itemgetter
import matplotlib.pyplot as plt


path = 'C:/Users/regin/Nextcloud/Postdoc/Code/numerical_results/Results_Simulator/Compare_RealModels_Bitflip/'

# load results from file
#qpu_results = np.loadtxt(path+'results/averaged_results2021-12-23.dat')

sc_results0 = np.loadtxt(path+'ibm_processor_bitflip_error0_initstate_1_0_200000shots.dat')
sc_results1 = np.loadtxt(path+'ibm_processor_bitflip_error1_initstate_1_0_200000shots.dat')
sc_results2 = np.loadtxt(path+'ibm_processor_bitflip_error2_initstate_1_0_200000shots.dat')

nv_results0 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_0_shots200000_init_1-0.dat')
nv_results1 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_1_shots200000_init_1-0.dat')
nv_results2 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_2_shots200000_init_1-0.dat')


averaged_results_sc0 = sum([sc_results0,sc_results1,sc_results2])/3
averaged_results_nv0 = sum([nv_results0,nv_results1,nv_results2])/3

# plot results 
x = np.arange(10)

plt.figure(figsize=(6.0,2.5))
plt.xlabel(r'different initial layouts')
plt.ylabel('logical error rates')
plt.bar(x+1,averaged_results_nv0[:10,1], label=r'NV-C', color='tab:red')
plt.bar(x+1,averaged_results_sc0[:10,1], label='SC', color='tab:green')
plt.xticks(np.arange(1))
plt.legend()
plt.savefig('tenbestresults_init0.pdf')
plt.show()

averaged_results_sc0[:10,1]

# =============================================================================
# sc_results0 = np.loadtxt(path+'ibm_processor_bitflip_error0_initstate_0_1_200000shots.dat')
# sc_results1 = np.loadtxt(path+'ibm_processor_bitflip_error1_initstate_0_1_200000shots.dat')
# sc_results2 = np.loadtxt(path+'ibm_processor_bitflip_error2_initstate_0_1_200000shots.dat')
# 
# nv_results0 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_0_shots200000_init_0-1.dat')
# nv_results1 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_1_shots200000_init_0-1.dat')
# nv_results2 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_2_shots200000_init_0-1.dat')
# 
# 
# averaged_results_sc1 = sum([sc_results0,sc_results1,sc_results2])/3
# averaged_results_nv1 = sum([nv_results0,nv_results1,nv_results2])/3
# 
# # plot results 
# x = np.arange(10)
# 
# plt.figure(figsize=(6.0,2.5))
# plt.xlabel(r'different initial layouts, inital state: $|\psi \rangle=1$')
# plt.ylabel('logical error rates')
# plt.bar(x+1,averaged_results_nv1[:10,1], label=r'NV-C', color='tab:red')
# plt.bar(x+1,averaged_results_sc1[:10,1], label='SC', color='tab:green')
# plt.xticks(np.arange(1))
# plt.legend()
# plt.savefig('tenbestresults_init1.pdf')
# plt.show()
# =============================================================================


# =============================================================================
# sc_results0 = np.loadtxt(path+'ibm_processor_bitflip_error0_initstate_superpos_200000shots.dat')
# sc_results1 = np.loadtxt(path+'ibm_processor_bitflip_error1_initstate_superpos_200000shots.dat')
# sc_results2 = np.loadtxt(path+'ibm_processor_bitflip_error2_initstate_superpos_200000shots.dat')
# averaged_results_sc2 = sum([sc_results0,sc_results1,sc_results2])/3
# 
# 
# nv_results0 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_0_shots200000_init_superpos.dat')
# nv_results1 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_1_shots200000_init_superpos.dat')
# nv_results2 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_2_shots200000_init_superpos.dat')
# 
# averaged_results_nv2 = sum([nv_results0,nv_results1,nv_results2])/3
# 
# # =============================================================================
# # nv_results0 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_0_shots200000_init_0_1_new.dat')
# # nv_results1 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_1_shots200000_init_0_1_new.dat')
# # nv_results2 = np.loadtxt(path+'NVcenter_bitflip_realnoise_errorpos_2_shots200000_init_0_1_new.dat')
# # 
# # averaged_results_nv3 = sum([nv_results0,nv_results1,nv_results2])/3
# # =============================================================================
# 
# 
# plt.figure(figsize=(10.0,3.5))
# plt.xlabel(r'different initial layouts')
# plt.ylabel('logical error rates')
# #plt.bar(x+1,averaged_results_nv1[:10,1], label='NV-C', color='tab:red')
# 
# plt.bar(x+1,averaged_results_nv1[:10,1], label=r'NV-C, $|\psi \rangle=|1\rangle$', color='tomato')
# plt.bar(x+1,averaged_results_nv2[:10,1], label=r'NV-C, $|\psi \rangle=1/\sqrt{2}( |0\rangle+ |1\rangle)$', color='red')
# plt.bar(x+1,averaged_results_nv[:10,1], label=r'NV-C, $|\psi \rangle=|0\rangle$', color='darkred')
# 
# #plt.bar(x+1,averaged_results_nv1[:10,1], label='NV-C', color='tab:orange')
# plt.bar(x+1,averaged_results_sc1[:10,1], label=r'SC, $|\psi \rangle=|1\rangle$', color='limegreen')
# plt.bar(x+1,averaged_results_sc2[:10,1], label=r'SC, $|\psi \rangle=1/\sqrt{2}( |0\rangle+ |1\rangle)$', color='tab:green')
# plt.bar(x+1,averaged_results_sc[:10,1], label=r'SC, $|\psi \rangle=|0\rangle$', color='darkgreen')
# plt.legend()
# plt.savefig('tenbestresults_init1.pdf')
# plt.show()
# 
# =============================================================================

