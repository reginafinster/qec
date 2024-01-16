# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:52:58 2022

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
from qiskit.quantum_info import average_gate_fidelity, Kraus
from operator import itemgetter
import matplotlib.pyplot as plt
from functools import reduce


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'/modules')
#sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
#sys.path.append('/Users/reginafinsterholzl/Nextcloud/Postdoc/Code/modules')


import my_noise_models
import codes


# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    #path_to_binary='/Users/reginafinsterholzl/Nextcloud/Postdoc/Code/noise_models/noisemodel_ibmq_ehningen_2021_10_13.dat'
    
    path_to_binary = '\\noise_models\\noisemodel_ibmq_ehningen_2021_10_13.dat'
    parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    path_to_binary = parentdir + path_to_binary
    
    # define params
    pos_error_ibm = 1
    pos_error_nv = 2
    
    readout_string_nv = '01' # nv center: (00) for None, (11) for x[0], (01) for x[1], (10) for x[2]
    readout_string_ibm = '11' # ehningen: (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]

    shots = 200000
    
    # set up circuit
    qc_nv = codes.BitFlip_NVCenter(pos_error=pos_error_nv).measure_at_end()
    qc_ibm = codes.BitFlip_IBM(detection_only=True,cat_state=False,pos_error=pos_error_ibm).qc
    #display(qc_nv.draw('mpl'))
    #display(qc_ibm.draw('mpl',idle_wires=False))
    
    
    initial_layout_ibm = [2, 4, 10, 1, 7]
    gate_list_ibm = [[2, 1], [4, 1], [4, 7], [10, 7]] 
    initial_layout_nv = [[0,1,2,3,4,5,6,7]] # for NV Center
    #initial_layout_ibm = [[0, 2, 4, 1, 3]] # for IBM chip
    gate_list_nv = [[1,0],[2,0],[0,6],[2,0],[3,0],[0,7],[7,0]]

    # loop over parameters and store result in list of dicts
    results = []
    #good_parameter_list_t1t2 = np.arange(0.000001,0.0001,0.000005)
    parameter_list = np.arange(0.0,0.002,0.00005)

    for l, param in enumerate(parameter_list[:]):
        t = param
        
        NoiseModelNV = my_noise_models.NoiseModel_NVCenter(
            n_qubits=8,change_coherence_times=True,t=t,fill_up_gate_error=False)
        noise_model_nv = NoiseModelNV.build_model()
        
        NoiseModelIBM = my_noise_models.NoiseModel_IBM(
            path_to_binary=path_to_binary,change_coherence_times=True,t=t,\
            fill_up_gate_error=False)
        noise_model_ibm = NoiseModelIBM.build_model()
        
        # first nv center model
        simulator = AerSimulator(noise_model=noise_model_nv)
        tqc = transpile(qc_nv, backend=simulator,basis_gates=NoiseModelNV.basis_gates, \
                        optimization_level=0, coupling_map=NoiseModelNV.coupling_map, \
                        initial_layout=initial_layout_nv)
        
        result = simulator.run(tqc,shots=shots,memory=True).result()
        ancilla_counts = result.get_counts()[(readout_string_nv +' 00')]
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()
        
# =============================================================================
#         print(result.get_counts())
#         print(projection_counts)
#         print(ancilla_counts2)
# =============================================================================
        
        print('\n')
        print("results for NV center:")
        #print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
        
        error_rate_nv = 1-( (result.get_counts()[(readout_string_nv +' 00')]) /projection_counts['00'])
        predicted_error_nv = 1.0- reduce((lambda x, y: x * y),[NoiseModelNV.gate_fidelities[str(gate)].get('cx')\
                                           for gate in gate_list_nv])
        print([NoiseModelNV.gate_fidelities[str(gate)].get('cx') for gate in gate_list_nv])
        
        #print("error rate nv center: ", 1-(ancilla_counts2[readout_string_nv]/shots))
        print("postselected error rate: ", error_rate_nv)
        
        print('theoretical estimation of error rate after postselection: ', predicted_error_nv)
        
        print('\n')
        # next ibm model
        simulator = AerSimulator(noise_model=noise_model_ibm)
        tqc = transpile(qc_ibm, backend=simulator, basis_gates=NoiseModelIBM.basis_gates, \
                        optimization_level=0, coupling_map=NoiseModelIBM.coupling_map, \
                            initial_layout=initial_layout_ibm)
        #display(tqc.draw('mpl',idle_wires=False))
      
        result = simulator.run(tqc,shots=shots,memory=True).result()
        ancilla_counts = result.get_counts()[(readout_string_ibm +' 00')]
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()

        print("results for IBM chip:")
        #print("rate of counts out of code space: ", (1.0-(projection_counts['00']/shots)))
        
        error_rate_ibm = 1-( (result.get_counts()[(readout_string_ibm +' 00')]) /projection_counts['00'])
        predicted_error_ibm = 1.0- reduce((lambda x, y: x * y),[NoiseModelIBM.gate_fidelities[str(gate)].get('cx')\
                                           for gate in gate_list_ibm])
        print([NoiseModelIBM.gate_fidelities[str(gate)].get('cx') for gate in gate_list_ibm])
        
        #print("error rate ibm: ", 1-(ancilla_counts2[readout_string_ibm]/shots))
        print("postselected error rate: ", error_rate_ibm)
        
        print('theoretical estimation of error rate after postselection: ', predicted_error_ibm)

# =============================================================================
#         print(result.get_counts())
#         print(projection_counts)
#         print(ancilla_counts2)
# =============================================================================
        
        results_ = [param]
        results_.append(round(error_rate_nv,6))
        results_.append(round(error_rate_ibm,6))
        results_.append(round(predicted_error_nv,6))
        results_.append(round(predicted_error_ibm,6))
        results.append(results_)

    # plot results
    aresults = np.array(results[:])
    x = aresults[:,0]
    plt.figure(figsize=(12.0,4.0))
    plt.title('error rates for 3 Qubit BitFlip Code')
    plt.xlabel('t1')
    plt.ylabel('logical error rates')
    plt.plot(x,aresults[:,1], label='error nv')
    plt.plot(x,aresults[:,2], label='error ibm')
    plt.plot(x,aresults[:,3], label='estimated rate nv')
    plt.plot(x,aresults[:,4], label='estimated rate ibm')
    plt.legend()
    plt.show()
    
   np.savetxt('comparerealisticmodels_t1.dat',aresults)
# =============================================================================
#     print(aresults[:])
#     
#     import copy
#     storeresults = copy.deepcopy(aresults)
#     
#     np.savetxt('simplemodel_vary_onlyt1.dat',aresults)
# =============================================================================

    
    
