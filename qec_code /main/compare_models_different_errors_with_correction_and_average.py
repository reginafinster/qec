# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 13:39:50 2022

@author: regina
"""

import os
import sys
import numpy as np
import logging
from qiskit.providers.aer import AerSimulator, StatevectorSimulator
from qiskit import transpile, QuantumCircuit
from qiskit.result import marginal_counts
from qiskit.providers.aer.noise import depolarizing_error
from qiskit.quantum_info import average_gate_fidelity, state_fidelity
from operator import itemgetter
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
#sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
import my_noise_models
import codes
import snippets

# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


def compare_models(pos_error, input_state, shots):
    
    # define params
    pos_error_nv = pos_error+1
    pos_error_ibm = pos_error
   
    shots = shots
    
    # set up circuit
    qc_nv = codes.PhaseFlipUnitaryCorrection_NV(pos_error=pos_error_nv,initialize=input_state,use_input_statevector=False).circuit()
    qc_ibm = codes.TranspiledPhaseFlip_SCProcessor(pos_error=pos_error_ibm,initialize=input_state,use_input_statevector=False).circuit()
    #display(qc_nv.draw('mpl'))
    #display(qc_ibm.draw('mpl'))
    
    initial_layout_nv = [[0,1,2,3,4,5]] # for NV Center
    #old:#initial_layout_ibm = [[1,2,3,0,4]] # for IBM chip
    initial_layout_ibm = [[3,2,4,1,0]]
    coupling_map_ibm = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2],[1,4],[4,1]]
    #old #coupling_map_ibm = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

    # loop over parameters and store result in list of dicts
    results = []
    #good_parameter_list_t1t2 = np.arange(0.000001,0.001,0.000005)
    p_depol_check = False
    p_depol = 0.0
    bool_therror = True
    t = 0.0
    # list for depol error
    #parameter_list = np.arange(0.0001,0.01,0.0005)
    # list for damping error
    parameter_list = np.arange(0.00001,0.0001,0.000005)

    for l, param in enumerate(parameter_list[:]):
        if p_depol_check: 
            p_depol=param
        if bool_therror:
            t = param
        NoiseModelNV = my_noise_models.SimpleNoiseModel_NVCenter\
            (p_depol=p_depol,n_qubits=6,bool_therror=bool_therror,t=t,single_gates_noisy=True)
        noise_model_nv = NoiseModelNV.build_model()
        NoiseModelIBM = my_noise_models.SimpleNoiseModel_IBM\
            (p_depol=p_depol,n_qubits=5,bool_therror=bool_therror,t=t,single_gates_noisy=True)
        noise_model_ibm = NoiseModelIBM.build_model()
        
        # first nv center model
        simulator = AerSimulator(noise_model=noise_model_nv)
        tqc = transpile(qc_nv, backend=simulator,optimization_level=0)
        #display(tqc.draw('mpl'))
        
        result = simulator.run(tqc,shots=shots).result()
        
        init_dmatrix_nv = result.data()['init_dmatrix']
        result_dmatrix_nv = result.data()['result_dmatrix']
        fid_nv = state_fidelity(init_dmatrix_nv, result_dmatrix_nv)
        print("Overlap NV-center: ", fid_nv)
        error_rate_nv = 1.0-state_fidelity(init_dmatrix_nv, result_dmatrix_nv)
        print("Infidelity NV-center: ",error_rate_nv)
        
# =============================================================================
#         projection_counts = marginal_counts(result, indices=[0,1,2]).get_counts()
#         
#        
#         #print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
#         #error_rate_nv = 1-( (result.get_counts()[(readout_string_nv +' 00')]) /projection_counts['00'])
#         #print("error rate nv center: ", 1-(ancilla_counts2[readout_string_nv]/shots))
#         
#         rate_0 = 0.0
#         if input_state[0]>0.0:
#             rate_0 = np.absolute((projection_counts['000']/shots) - input_state[0])/input_state[0]
#         rate_1 = 0.0
#         if input_state[1]>0.0:
#             rate_1 = np.absolute((projection_counts['111']/shots) - input_state[1])/input_state[1]
#         error_rate_nv = (rate_0+rate_1)/2.0
#         
# =============================================================================
        #print("error rate: ", error_rate_nv)
        estimated_pdepol_nv = 1.0-( (average_gate_fidelity(depolarizing_error(p_depol,3)))**5 ) + \
              1.0- ((average_gate_fidelity(depolarizing_error(p_depol,4)))**3) + \
              1.0- ((average_gate_fidelity(depolarizing_error(p_depol,1)))**16)
        #print('theoretical estimation of depol error rate: '\
        #      ,estimated_pdepol_nv)
# =============================================================================
#         estimated_pthermal_nv = 1.0-(NoiseModelNV.get_cx_agf_relax())**8 +\
#             1.0-(NoiseModelNV.get_single_agf_relax())**16
#         #print('theoretical estimation of relaxation error rate: ', \
# =============================================================================
        #      estimated_pthermal_nv)            
        #print('\n')
        
        
        # next ibm model
        simulator = AerSimulator(noise_model=noise_model_ibm)
        tqc = transpile(qc_ibm, backend=simulator, \
                        optimization_level=0, coupling_map=coupling_map_ibm, \
                            initial_layout=initial_layout_ibm)
        #tqc.draw('mpl',style="bw",filename="transpiledcircuit.png")
        result = simulator.run(tqc,shots=shots).result()
        
        init_dmatrix_ibm = result.data()['init_dmatrix']
        result_dmatrix_ibm = result.data()['result_dmatrix']
        fid_ibm = state_fidelity(init_dmatrix_ibm, result_dmatrix_ibm)
        print("Fidelity SC: ", fid_ibm)
        error_rate_ibm = 1.0-state_fidelity(init_dmatrix_ibm, result_dmatrix_ibm)
        print("Infidelity SC: ",error_rate_ibm)
        #ancilla_counts = result.get_counts()[(readout_string_ibm +' 00')]
# =============================================================================
#         projection_counts = marginal_counts(result, indices=[0,1,2]).get_counts()
#         
#         rate_0 = 0.0
#         if input_state[0]>0.0:
#             rate_0 = np.absolute((projection_counts['000']/shots) - input_state[0])/input_state[0]
#         rate_1 = 0.0
#         if input_state[1]>0.0:
#             rate_1 = np.absolute((projection_counts['111']/shots) - input_state[1])/input_state[1]
#         error_rate_ibm = (rate_0+rate_1)/2.0
#         #ancilla_counts2 = marginal_counts(result, indices=[3,4]).get_counts()
# 
#         #print("results for IBM chip:")
#         #print("rate of counts out of code space: ", (1.0-(projection_counts['00']/shots)))
#         
#         #print(projection_counts)
#        
#         
#         #print("error rate: ", error_rate_ibm)
# =============================================================================
        
        estimated_pdepol_ibm = 1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**59
        #print('theoretical estimation of depol error rate: '\
        #      , estimated_pdepol_ibm)
        
        #print('theoretical estimation of relaxation error rate: '\
        #      ,1.0-(NoiseModelIBM.get_agf_relax())**59 )

        
        results_ = [param]
        results_.append(round(error_rate_nv,8))
        results_.append(round(error_rate_ibm,8))
        results_.append(round(estimated_pdepol_nv,8))
        results_.append(round(estimated_pdepol_ibm,8))
# =============================================================================
#         results_.append(round(estimated_pthermal_nv,8))
#         results_.append(round(1.0-(NoiseModelIBM.get_agf_relax())**59,8))
# =============================================================================
        results.append(results_)

    return results

meta_res = []
pos_error_list = [0,1,2]

# =============================================================================
# stepsize = 0.01
# polarization_values = np.arange(0.0,(1.0+stepsize),stepsize)
# input_state = list(zip(polarization_values,list(reversed(polarization_values))))
# 
# =============================================================================
input_state = snippets.Input_Statevector(20,1).input_state_array_complex()

#input_state = [np.sqrt(0.7),np.sqrt(0.3)] 

# ich sehe, dass bei 20000 shots eine ausreichende Konvergenz vorhanden ist.
shots = 20000
for coeffs in input_state:
    for error in pos_error_list:
        print("\n calculating input state with error position: ", coeffs, error)
        res = compare_models(pos_error=error, input_state=coeffs, shots=shots)
        meta_res.append(res)
        aresults = np.array(res)
        x = aresults[:,0]
        plt.figure(figsize=(12.0,4.0))
        plt.title('error'+str(coeffs)+str(error))
        plt.xlabel('damping error')
        plt.xlabel('T1 and T2')
        #plt.ylabel('logical error rates')
        plt.xlim(max(x), min(x))
        plt.plot(x,aresults[:,1], label='error nv center')
        plt.plot(x,aresults[:,2], label='error ibm chip')
        plt.plot(x,aresults[:,3], linestyle='--', label='estimated rate nv center')
        plt.plot(x,aresults[:,4], linestyle='--', label='estimated rate ibm')
        plt.legend()
        plt.show()

# plot results
aresults = np.array(meta_res)
aresults = sum(aresults)/(len(input_state)*len(pos_error_list))
aresults = aresults[1:]


#aresults1 = np.loadtxt('phaseflip_depol_compare_t2=t1_secondtry.dat')
#aresults2 = np.loadtxt('phaseflip_depol_compare_t2=t1_firsttry.dat')


x = aresults[:,0]
plt.figure(figsize=(12.0,4.0))
#plt.title('simulation of the Phaseflip-ECC with different device properties')
#plt.xlabel('depolarizing error')
plt.xlabel('Decoherence time T2')
plt.ylabel('logical error rates')
plt.xlim(min(x), max(x))
#plt.plot(x,aresults1[:,1], color='#800000', linestyle='dashed', label='NV-C, T2=2T1')
#plt.plot(x,aresults1[:,2], color='#006400', linestyle='dashed', label='SC, T2=2T1')
plt.plot(x,aresults[:,1], color='#800000', label='NV-C, T2=2T1')
plt.plot(x,aresults[:,2], color='#006400', label='SC, T2=2T1')
#plt.plot(x,aresults2[:,1], color='#800000', linestyle='dotted', label='NV-C, T2=2T1')
#plt.plot(x,aresults2[:,2], color='#006400', linestyle='dotted', label='SC, T2=2T1')
#plt.plot(x,aresults[:,5], color='tab:cyan', linestyle='--', label='gate infidelities NV-center')
#plt.plot(x,aresults[:,6], color='tab:blue', linestyle='--', label='gate infidelities sup.proc.')
#plt.plot(x,theoretical_bound(p=x), label='analytical bound $p_e =\sum_{s=t+1}^{n} n!/(k!(n-k)!) p (1-p)^{n-s} $')
plt.legend()
plt.show()


np.savetxt('phaseflip_damping_compare_t2=0-1t1.dat',aresults)


# =============================================================================
#     import copy
#     storeresults = copy.deepcopy(aresults)
#     np.savetxt('phaseflip_damping_compare.dat',aresults)
# =============================================================================
    


    
    

