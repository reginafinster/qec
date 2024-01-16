# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 17:35:04 2022

@author: regina
"""
import os
import sys
import numpy as np
import logging
import pickle
from qiskit.providers.aer import AerSimulator, StatevectorSimulator
from qiskit import transpile, QuantumCircuit
from qiskit.result import marginal_counts
from operator import itemgetter
import matplotlib.pyplot as plt
from qiskit.visualization import plot_state_city, plot_state_hinton
from qiskit.quantum_info import *

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
#sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
import my_noise_models
import codes

# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    input_state = [np.sqrt(0.7),np.sqrt(0.3)] 

    #qc = codes.BitFlip_IBM(detection_only=True,cat_state=False,input_state=input_state,pos_error=1).qc
    #qc = codes.PhaseFlipUnitaryCorrection_NV(pos_error=1,input_statevector=input_state).circuit()
    qc = codes.PhaseFlipUnitaryCorrection_without_transpilation_SC(pos_error=2).circuit()


    
    display(qc.draw('mpl'))
    
    
    simulator = AerSimulator(noise_model=None)
    linear_coupling_map = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]
    hex_coupling_map_1 = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2],[1,4],[4,1]]
    hex_coupling_map_2 = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2],[2,4],[4,2]]
    basis_gates = ['cx', 'id', 'rz', 'sx', 'x','reset']
    
    test_coupling_map = [[4, 3], [3, 4], [3, 1], [1, 3], [1, 0], [0, 1], [0, 2], [2, 0]]

    
    tqcs_test =[]

    for i in range(200):
        tqc = transpile(qc,backend=simulator,basis_gates=basis_gates, \
                        coupling_map=hex_coupling_map_1)
        display(tqc.draw('mpl'))
        #result = simulator.run(tqc,shots=1,memory=True).result()
        print('depth: ', tqc.depth())
        print('number cnots: ', tqc.count_ops()['cx'])
        print('size: ', tqc.size())
        tqcs_test.append([tqc,tqc.count_ops()['cx']])
        

    sorted_tqcs = np.array(sorted(tqcs_test, key=itemgetter(-1))) 
    display(sorted_tqcs[0][0].draw('mpl'))
    sorted_tqcs[0]

    
# =============================================================================
#     with open("good_tqc_rohdaten.dat", "bw") as f:
#         pickle.dump(goodtqc,f)
# =============================================================================
    
    #pickle.dump(goodtqc,)
    #init_dmatrix = result.data()['init_dmatrix']
    #final_dmatrix = result.data()['result_dmatrix']
    
    #fid = state_fidelity(init_dmatrix, final_dmatrix)
    #print(result.get_counts())
    #print(fid)
    
# =============================================================================
#     simulator = AerSimulator(noise_model=None)
#     #backend = StatevectorSimulator()
#     job = simulator.run(qc)
#     result = job.result()
#     outputstate = result.data()['init_statevector']
#     #outputstate1 = result.get_statevector(qc, decimals=3)
#     print(outputstate)
#     #print(outputstate1)
# =============================================================================
    
    #my_statevector = np.zeros(32)
    #my_statevector[0] = np.sqrt(input_state[0])
    #my_statevector[1] = np.sqrt(input_state[1])
    #print(my_statevector)
    #my_statevector[1] = np.sqrt(self.input_state[1])




    
    #display(plot_state_hinton(outputstate))
