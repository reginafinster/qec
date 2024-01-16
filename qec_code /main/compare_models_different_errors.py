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

# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


# ich möchte über verschiedene Input-Zustände und über verschiedene Fehler mitteln.


if __name__ == "__main__":
    
    # define params
    pos_error_ibm = None
    pos_error_nv = None
    
    readout_string_nv = '00' # nv center: (00) for None, (11) for x[0], (01) for x[1], (10) for x[2]
    readout_string_ibm = '00' # ehningen: (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]

    shots = 20000
    
    # set up circuit
    qc_nv = codes.BitFlip_NVCenter(pos_error=pos_error_nv).measure_at_end()
    qc_ibm = codes.BitFlip_IBM(detection_only=True,cat_state=False,pos_error=pos_error_ibm).qc
    #display(qc_nv.draw('mpl'))
    #display(qc_ibm.draw('mpl'))
    
    initial_layout_nv = [[0,1,2,3,4,5,6,7]] # for NV Center
    initial_layout_ibm = [[0, 2, 4, 1, 3]] # for IBM chip

    # loop over parameters and store result in list of dicts
    results = []
    #good_parameter_list_t1t2 = np.arange(0.000001,0.0001,0.000005)
    p_depol = 0.0
    bool_therror = False
    parameter_list = np.arange(0.001,0.1,0.005)
    #parameter_list = np.arange(0.000001,0.001,0.000005)
    #parameter_list = [0.0]

    for l, param in enumerate(parameter_list[:]):
        p_depol = param
        #t = param
        NoiseModelNV = my_noise_models.SimpleNoiseModel_NVCenter\
            (p_depol=p_depol,n_qubits=8,bool_therror=bool_therror,t=t)
        noise_model_nv = NoiseModelNV.build_model()
        NoiseModelIBM = my_noise_models.SimpleNoiseModel_IBM\
            (p_depol=p_depol,n_qubits=5,bool_therror=bool_therror,t=t)
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
        
        #print("error rate nv center: ", 1-(ancilla_counts2[readout_string_nv]/shots))
        print("postselected error rate: ", error_rate_nv)
        
        
        print('theoretical estimation of depol error rate after postselection: '\
              ,1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**7 )
        
        print('theoretical estimation of relaxation error rate after postselection: '\
              ,1.0-(NoiseModelNV.get_cx_agf_relax())**7 )
            
        
        print('\n')
        # next ibm model
        simulator = AerSimulator(noise_model=noise_model_ibm)
        tqc = transpile(qc_ibm, backend=simulator, basis_gates=NoiseModelIBM.basis_gates, \
                        optimization_level=0, coupling_map=NoiseModelIBM.coupling_map, \
                            initial_layout=initial_layout_ibm)
      
        #display(tqc.draw('mpl'))
        result = simulator.run(tqc,shots=shots,memory=True).result()
        ancilla_counts = result.get_counts()[(readout_string_ibm +' 00')]
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()

        print("results for IBM chip:")
        #print("rate of counts out of code space: ", (1.0-(projection_counts['00']/shots)))
        
        error_rate_ibm = 1-( (result.get_counts()[(readout_string_ibm +' 00')]) /projection_counts['00'])
        
        #print("error rate ibm: ", 1-(ancilla_counts2[readout_string_ibm]/shots))
        print("postselected error rate: ", error_rate_ibm)
        
        print('theoretical estimation of depol error rate after postselection: '\
              ,1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**4 )
        
        print('theoretical estimation of relaxation error rate after postselection: '\
              ,1.0-(NoiseModelIBM.get_agf_relax())**4 )
        
# =============================================================================
#         print(result.get_counts())
#         print(projection_counts)
#         print(ancilla_counts2)
# =============================================================================
        
        results_ = [param]
        results_.append(round(error_rate_nv,5))
        results_.append(round(error_rate_ibm,5))
        results_.append(round(1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**7,8))
        results_.append(round(1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**4,8))
        results_.append(round(1.0-(NoiseModelNV.get_cx_agf_relax())**7,8))
        results_.append(round(1.0-(NoiseModelIBM.get_agf_relax())**4,8))
        results.append(results_)

    # plot results
    aresults = np.array(results[1:])
    x = aresults[:,0]
    plt.figure(figsize=(12.0,4.0))
    plt.title('same depolarizing error on both systems')
    plt.xlabel('depolarizing error')
    #plt.xlabel('Decoherence times T1 and T2')
    plt.ylabel('logical error rates')
    #plt.xlim(max(x), min(x))
    plt.plot(x,aresults[:,1], label='error nv center')
    plt.plot(x,aresults[:,2], label='error ibm chip')
    plt.plot(x,aresults[:,3], label='estimated rate nv center')
    plt.plot(x,aresults[:,4], label='estimated rate ibm')
    plt.legend()
    plt.show()
    
   #np.savetxt('simplemodel_t1t2.dat',aresults)
# =============================================================================
#     print(aresults[:])
#     
#     import copy
#     storeresults = copy.deepcopy(aresults)
#     
#     np.savetxt('simplemodel_vary_onlyt1.dat',aresults)
# =============================================================================

    
    
