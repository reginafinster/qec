# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:17:01 2022

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


if __name__ == "__main__":
    
    # define params
    pos_error_ibm = None
    pos_error_nv = None
   
    shots = 20000
    
    # set up circuit
    qc_nv = codes.PhaseFlipUnitaryCorrection_NV(pos_error=pos_error_nv).circuit()
    qc_ibm = codes.PhaseFlipUnitaryCorrection_IBM(pos_error=pos_error_ibm).circuit()
    #display(qc_nv.draw('mpl'))
    #display(qc_ibm.draw('mpl'))
    
    initial_layout_nv = [[0,1,2,3,4,5]] # for NV Center
    initial_layout_ibm = [[1,2,3,0,4]] # for IBM chip
    coupling_map_ibm = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

    # also das 0te qubit wird auf die 3 gelegt
    # loop over parameters and store result in list of dicts
    results = []
    good_parameter_list_t1t2 = np.arange(0.000001,0.001,0.000005)
    p_depol = 0.0
    bool_therror = True
    t = None
    #parameter_list = np.arange(0.001,0.01,0.0005)
    #parameter_list = [0.01]

    for l, param in enumerate(good_parameter_list_t1t2[:]):
        #p_depol = param
        t = param
        NoiseModelNV = my_noise_models.SimpleNoiseModel_NVCenter\
            (p_depol=p_depol,n_qubits=6,bool_therror=bool_therror,t=t)
        noise_model_nv = NoiseModelNV.build_model()
        NoiseModelIBM = my_noise_models.SimpleNoiseModel_IBM\
            (p_depol=p_depol,n_qubits=5,bool_therror=bool_therror,t=t)
        noise_model_ibm = NoiseModelIBM.build_model()
        
        # first nv center model
        simulator = AerSimulator(noise_model=noise_model_nv)
        tqc = transpile(qc_nv, backend=simulator, \
                        optimization_level=0)
        #display(tqc.draw('mpl'))
        
        result = simulator.run(tqc,shots=shots,memory=True).result()
        projection_counts = marginal_counts(result, indices=[0,1,2]).get_counts()
        
        print('\n')
        print("results for NV center:")
        print(projection_counts)
        #print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
        #error_rate_nv = 1-( (result.get_counts()[(readout_string_nv +' 00')]) /projection_counts['00'])
        #print("error rate nv center: ", 1-(ancilla_counts2[readout_string_nv]/shots))
        error_rate_nv = 1.0-projection_counts['000']/shots
        print("error rate: ", error_rate_nv)
        
        estimated_pdepol_nv = 1.0-( (average_gate_fidelity(depolarizing_error(p_depol,3)))**5 ) + \
              1.0- ((average_gate_fidelity(depolarizing_error(p_depol,4)))**3) + \
              1.0- ((average_gate_fidelity(depolarizing_error(p_depol,1)))**16)
        print('theoretical estimation of depol error rate: '\
              ,estimated_pdepol_nv)
        
        estimated_pthermal_nv = 1.0-(NoiseModelNV.get_cx_agf_relax())**8 +\
            1.0-(NoiseModelNV.get_single_agf_relax())**16
        print('theoretical estimation of relaxation error rate: ', \
              estimated_pthermal_nv)            
        print('\n')
        
        
        # next ibm model
        simulator = AerSimulator(noise_model=noise_model_ibm)
        tqc = transpile(qc_ibm, backend=simulator, basis_gates=NoiseModelIBM.basis_gates, \
                        optimization_level=0, coupling_map=coupling_map_ibm, \
                            initial_layout=initial_layout_ibm)
      
        #display(tqc.draw('mpl'))
        result = simulator.run(tqc,shots=shots,memory=True).result()
        #ancilla_counts = result.get_counts()[(readout_string_ibm +' 00')]
        projection_counts = marginal_counts(result, indices=[0,1,2]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[3,4]).get_counts()

        print("results for IBM chip:")
        #print("rate of counts out of code space: ", (1.0-(projection_counts['00']/shots)))
        
        print(projection_counts)
        error_rate_ibm = 1.0-(projection_counts['000']/shots)
        
        print("error rate: ", error_rate_ibm)
        
        estimated_pdepol_ibm = 1.0-(average_gate_fidelity(depolarizing_error(p_depol,2)))**59
        print('theoretical estimation of depol error rate: '\
              , estimated_pdepol_ibm)
        
        print('theoretical estimation of relaxation error rate: '\
              ,1.0-(NoiseModelIBM.get_agf_relax())**59 )

        
        results_ = [param]
        results_.append(round(error_rate_nv,8))
        results_.append(round(error_rate_ibm,8))
        results_.append(round(estimated_pdepol_nv,8))
        results_.append(round(estimated_pdepol_ibm,8))
        results_.append(round(estimated_pthermal_nv,8))
        results_.append(round(1.0-(NoiseModelIBM.get_agf_relax())**59,8))
        results.append(results_)

    # plot results
    aresults = np.array(results[1:20])
    x = aresults[:,0]
    plt.figure(figsize=(12.0,4.0))
    plt.title('same relaxation error on both systems')
    plt.xlabel('Decoherence times T1 and T2')
    plt.ylabel('logical error rates')
    plt.xlim(max(x), min(x))
    plt.plot(x,aresults[:,1], label='error nv center')
    plt.plot(x,aresults[:,2], label='error ibm chip')
    plt.plot(x,aresults[:,5], label='estimated rate nv center')
    plt.plot(x,aresults[:,6], label='estimated rate ibm chip')
    plt.legend()
    plt.show()
    
    
   #np.savetxt('simplemodel_t1t2.dat',aresults)
    print(aresults[:])
    
    import copy
    storeresults = copy.deepcopy(aresults)
    
    np.savetxt('simplemodel_vary_onlyt1.dat',aresults)

    
    

