# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 07:44:25 2022

@author: regina
"""
import os
import sys
import numpy as np
import logging
import itertools
from datetime import date
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
from snippets import Input_Statevector

logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    
    path_to_binary = '\\noise_models\\noisemodel_ibmq_ehningen_2021_10_13.dat'
    
    parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    path_to_binary = parentdir + path_to_binary
    
    pos_error=2
    # fall 2 unabhängige Stabilizer (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]
    readout_string = '10' 
    #input_state = Input_Statevector(2,4).input_state_array_complex()
    input_state = [np.sqrt(0.3),np.sqrt(0.7)] 
    print(input_state)
    #qc = codes.BitFlip_IBM(pos_error=pos_error,initialize=input_state).qc
    #qc = codes.PhaseFlipUnitaryCorrection_IBM(pos_error=1,initialize=input_state,use_input_statevector=False).circuit()
    qc = codes.PhaseFlipUnitaryCorrection_without_transpilation_SC(pos_error=1).circuit()
    #qc = codes.BitFlip_NVCenter(pos_error=1,initialize=input_state).measure_at_end()
    #qc = codes.BitFlip_NVCenter(pos_error=1,initialize=input_state).bitflip_detection()
    display(qc.draw('mpl'))
    
    #initial_layout = [[0, 2, 5, 1, 3]] 
    coupling_map = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3], [3,5],[5,3],[1,6],[6,1]]
    #initial_layout = [[1,2,3,0,4]]
    n_qubits=6
    #coupling_map = [ [i+1,0] for i in range(n_qubits-1)] + [ [0,i+1] for i in range(n_qubits-1)]
    initial_layout = [[3,2,6,1,0]]
# =============================================================================
#     
#     initial_layout = [[1,2,3,0,4]]
#     coupling_map_ibm = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]
# 
# =============================================================================


    shots = 2000
        
    #NoiseModel = my_noise_models.NoiseModel_IBM(path_to_binary=path_to_binary)
    #noise_model = NoiseModel.build_model()
    basis_gates = ['cx', 'id', 'rz', 'sx', 'x']
    
    results = []
    
# =============================================================================
#     
#     tqc = transpile(qc, backend=simulator, \
#                             optimization_level=3, \
#                             coupling_map=coupling_map, \
#                             basis_gates=basis_gates,
#                             initial_layout=initial_layout)
#     display(tqc.draw('mpl'))
#     print('qc nb cnots: ', qc.count_ops()['cx'], 'tqc nb cnots: ', tqc.count_ops()['cx'])
# 
# =============================================================================
    for i in np.arange(0,100):
        
        simulator = AerSimulator(noise_model=None)
        tqc = transpile(qc, backend=simulator, \
                        optimization_level=3, \
                        coupling_map=coupling_map, \
                        basis_gates=basis_gates,
                        initial_layout=initial_layout)
        display(tqc.draw('mpl'))
        print('depth: ', tqc.depth())
        print('number cnots: ', tqc.count_ops()['cx'])
        print('size: ', tqc.size())
        
        results.append([tqc,tqc.count_ops()['cx']])
        
# =============================================================================
#         result = simulator.run(qc,shots=shots,memory=True).result()
#         ancilla_counts = result.get_counts()#[(readout_string+' 00')]
#         print(ancilla_counts)
#         projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
#         ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()
#         
# =============================================================================
# =============================================================================
#         print('\n')
#         print("results for IBM processor:")
#         print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
#         
#         error_rate = 1-( (result.get_counts()[(readout_string +' 00')]) /projection_counts['00'])
#         
#         print("error rate: ", 1-(ancilla_counts2[readout_string]/shots))
#         print("postselected error rate: ", error_rate)
#     
#         print('theoretical estimation of error rate after postselection: '\
#               ,1.0-((average_gate_fidelity(depolarizing_error(0.035,2)))**7)*(1-0.004)**5 )
#         
#         print(result.get_counts())
#         print(projection_counts)
#         print(ancilla_counts2)
#         #init_dmatrix = result.data()['init_dmatrix']
#         #print(init_dmatrix)
# =============================================================================
# =============================================================================
#             
#         results_ = [i,round(error_rate,5)]
#         results_.append(tqc.depth())
#         results_.append(tqc.count_ops()['cx'])
#         results_.append(tqc.size())
#         results_.append(layout)
#         results.append(results_)
# =============================================================================
        
# =============================================================================
#     # sort by value
#     aresults = [sublist[:-1] for sublist in results]
#     sresults = sorted(aresults, key=itemgetter(1))
#     sresults = np.array(sresults)
#     aresults = np.array(aresults)
#     
#     myresults = sorted(results, key=itemgetter(1))
#     
# 
#     with open(("ibmchip"+str(date.today())+".dat"), "w") as f:
#         f.write("#number\t logical error \t depth \t nb cnots \t size \t layout \n")
#         for result_ in myresults:
#             for el in result_: f.write(str(el)+"\t")
#             f.write("\n")
#         f.close()
#     
#     # plot results
#     x = np.arange(len(sresults[:20]))
#     plt.figure(figsize=(12.0,4.0))
#     plt.xlabel('number of iteration over layout')
#     plt.ylabel('logical error rates')
#     plt.bar(x,sresults[:20,1], label='logical error rate nv center')
#     plt.legend()
#     plt.show()
# =============================================================================





    
    
