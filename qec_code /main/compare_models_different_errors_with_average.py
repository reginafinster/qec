# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:33:56 2021

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
from qiskit.quantum_info import average_gate_fidelity
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
    
    # nv center: (00) for None, (11) for x[0], (01) for x[1], (10) for x[2]
    # ehningen: (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]
    nv_readout_dict = {None:'00',0:'11',1:'01',2:'10'}
    ibm_readout_dict = {None:'00',0:'01',1:'11',2:'10'}

    readout_string_nv = nv_readout_dict.get(pos_error)
    readout_string_ibm = ibm_readout_dict.get(pos_error) 

    shots = shots
    
    # set up circuit
    qc_nv = codes.BitFlip_NVCenter(pos_error=pos_error_nv,initialize=input_state,set_input_statevector=False).measure_at_end()
    qc_ibm = codes.BitFlip_IBM(pos_error=pos_error_ibm,initialize=input_state).qc
    #display(qc_nv.draw('mpl'))
    #display(qc_ibm.draw('mpl'))
    
    initial_layout_nv = [[0,1,2,3,4,5,6,7]] # for NV Center
    coupling_map_ibm = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]
    initial_layout_ibm = [1,2,3,0,4]

    # loop over parameters and store result in list of dicts
    results = []
    #good_parameter_list_t1t2 = np.arange(0.000001,0.0001,0.000005)
    p_depol_check = False
    p_depol = 0.0
    t=None
    bool_therror = True
    #parameter_list = np.arange(0.001,0.1,0.005) # for depol
    parameter_list = np.arange(0.00001,0.0001,0.000005) # for damping
    #parameter_list = [0.001, 0.0001]

    for l, param in enumerate(parameter_list[:]):
        if p_depol_check: 
            p_depol=param
        if bool_therror:
            t = param
        NoiseModelNV = my_noise_models.SimpleNoiseModel_NVCenter\
            (p_depol=p_depol,n_qubits=8,bool_therror=bool_therror,t=t,single_gates_noisy=False)
        noise_model_nv = NoiseModelNV.build_model()
        
        NoiseModelIBM = my_noise_models.SimpleNoiseModel_IBM\
            (p_depol=p_depol,n_qubits=5,bool_therror=bool_therror,t=t,single_gates_noisy=False)
        noise_model_ibm = NoiseModelIBM.build_model()
        
        # first nv center model
        simulator = AerSimulator(noise_model=noise_model_nv)
        tqc = transpile(qc_nv, backend=simulator, \
                        basis_gates=NoiseModelNV.basis_gates, \
                        optimization_level=0, \
                        coupling_map=NoiseModelNV.coupling_map, \
                        initial_layout=initial_layout_nv)
        
        #display(tqc.draw('mpl'))
        result = simulator.run(tqc,shots=shots,memory=True).result()
        try:
            ancilla_counts = result.get_counts()[(readout_string_nv +' 00')]
        except KeyError:
            ancilla_counts = 0
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        error_rate_nv = 1-( ancilla_counts /projection_counts['00'])
       
        # next ibm model
        simulator = AerSimulator(noise_model=noise_model_ibm)
        tqc = transpile(qc_ibm, backend=simulator, basis_gates=NoiseModelIBM.basis_gates, \
                        optimization_level=0, coupling_map=coupling_map_ibm, \
                            initial_layout=initial_layout_ibm)
      
        #display(tqc.draw('mpl'))
        result = simulator.run(tqc,shots=shots,memory=True).result()
        try:
            ancilla_counts = result.get_counts()[(readout_string_ibm +' 00')]
        except KeyError:
            ancilla_counts = 0
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        error_rate_ibm = 1-( ancilla_counts /projection_counts['00'])
     
            
        results_ = [param]
        results_.append(round(error_rate_nv,5))
        results_.append(round(error_rate_ibm,5))
        results_.append(round(1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**7,8))
        results_.append(round(1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**4,8))
        results_.append(round(1.0-(NoiseModelNV.get_cx_agf_relax())**7,8))
        results_.append(round(1.0-(NoiseModelIBM.get_agf_relax())**4,8))
        results.append(results_)
        
    return results


meta_res = []
pos_error_list = [0,1,2]
input_state_array = snippets.Input_Statevector(3,3).input_state_array_complex()
print(input_state)

shots = 20000
for coeffs in input_state:
    print(coeffs)
    for error in pos_error_list:
        print("\n calculating input state with error position: ", coeffs, error)
        res = compare_models(pos_error=error, input_state=coeffs, shots=shots)
        meta_res.append(res)
        aresults = np.array(res)
        x = aresults[:,0]
        plt.figure(figsize=(12.0,4.0))
        plt.title('input_state:'+ str(coeffs) + 'error_pos:'+str(error))
        plt.xlabel('damping error')
        plt.xlabel('T1 and T2')
        #plt.ylabel('logical error rates')
        plt.xlim(max(x), min(x))
        plt.plot(x,aresults[:,1], label='error nv center')
        plt.plot(x,aresults[:,2], label='error ibm chip')
        #plt.plot(x,aresults[:,5], linestyle='--', label='estimated rate nv center')
        #plt.plot(x,aresults[:,6], linestyle='--', label='estimated rate ibm')
        plt.legend()
        plt.show()

# plot results
aresults = np.array(meta_res)
aresults = sum(aresults)/(len(input_state)*len(pos_error_list))



#aresults = np.loadtxt('simplemodel_t1=t2_dampingerror_average.dat')
#aresults = np.loadtxt('simplemodel_t1=t2_depoalizingerror_average.dat')

x = aresults[:,0]
plt.figure(figsize=(12.0,4.0))
#plt.title('simulation of the Bitflip-ECC with different device properties')
#plt.xlabel('depolarizing error')
plt.xlabel('Decoherence times T1 and T2')
plt.ylabel('logical error rates')
#plt.xlim(0.01,0.095)
plt.xlim(min(x), max(x))
plt.plot(x,aresults[:,1], color='tab:red', label='NV-center')
plt.plot(x,aresults[:,2], color='tab:green', label='superconducting processor')
#plt.plot(x,aresults[:,3], color='tab:cyan', linestyle='--', label='gate infidelities NV-center')
#plt.plot(x,aresults[:,4], color='tab:blue', linestyle='--', label='gate infidelities sup.proc.')
#plt.plot(x,theoretical_bound(p=x), label='analytical bound $p_e =\sum_{s=t+1}^{n} n!/(k!(n-k)!) p (1-p)^{n-s} $')
plt.legend()
plt.show()



def theoretical_bound(p):
    return np.power(p,2)*3.0 + np.power(p,3)*2.0

#np.savetxt('bitflip_damping18-5-22.dat', aresults)  
#np.savetxt('simplemodel_t1=t2_depoalizingerror_average.dat',aresults)
# =============================================================================
#     print(aresults[:])
#     
#     import copy
#     storeresults = copy.deepcopy(aresults)
#     
#     np.savetxt('simplemodel_vary_onlyt1.dat',aresults)
# =============================================================================

