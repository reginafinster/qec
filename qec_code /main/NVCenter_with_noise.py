# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:33:56 2021

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
import copy

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
#sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
import my_noise_models
import codes

# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    
    tenbestlayouts6qubits = [(0, 4, 1, 2, 5, 3),(0, 2, 4, 1, 5, 3),(0, 4, 2, 1, 3, 5),(0, 2, 1, 4, 5, 3),(0, 1, 2, 4, 3, 5),\
                             (0, 4, 2, 1, 5, 3),(0, 2, 4, 1, 3, 5),(0, 5, 4, 1, 3, 2),(0, 1, 4, 2, 5, 3),(0, 2, 3, 1, 4, 5)]
    
    bestlayouts8qubits =  [(0, 6, 2, 1, 4, 3, 5, 7),(0, 2, 6, 1, 4, 3, 5, 7),\
                             (0,4,2,1,6,3,5,7),\
                             (0, 6, 4, 1, 2, 3, 5, 7),(0, 2, 4, 1, 6, 3, 5, 7),(0, 4, 6, 1, 2, 3, 5, 7),\
                             (0, 6, 1, 2, 4, 3, 5, 7),(0, 4, 6, 1, 2, 3, 5, 7),\
                             (0, 6, 2, 4, 1, 3, 5, 7),(0, 2, 1, 6, 4, 3, 5, 7),(0, 4, 2, 6, 1, 3, 5, 7),\
                             (0, 4, 2, 6, 1, 3, 5, 7),(0, 4, 2, 6, 1, 3, 5, 7),(0, 1, 6, 4, 2, 3, 5, 7)]
    n_qubits = 8
    pos_error=3 # 1,2,3 are codequbits!
    # fall 2 unabhängige Stabilizer (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]
    # fall 2 readout mit electron spin (00) for None, (11) for x[0], (01) for x[1], (10) for x[2]
    readout_string = '10'
    input_state = [np.sqrt(0.0),np.sqrt(1.0)]

    
    if (n_qubits==8):
        qc = codes.BitFlip_NVCenter(pos_error=pos_error,initialize=input_state).measure_at_end()
    elif (n_qubits==6):
        qc = codes.BitFlip_NVCenter(pos_error=pos_error,initialize=input_state).fivequbits()
    display(qc.draw('mpl'))
    
    #initial_layout = [[i for i in range(n_qubits)]]
    #initial_layout = [(0,) + el for el in list(itertools.permutations([i for i in range(1,n_qubits)]))] 
    #initial_layout = tenbestlayouts6qubits
    #best layouts for 8 qubits:
    initial_layout = [el + (3,5,7) for el in [(0,) + el for el in list(itertools.permutations([1,2,4,6]))]]
    shots = 200000
    print(initial_layout)
    
    noise_model = my_noise_models.NoiseModel_NVCenter(n_qubits=n_qubits).build_model()
        
    # loop over layout list and store result in list of dicts
    results = []

    for l, layout in enumerate(initial_layout):
        simulator = AerSimulator(noise_model=noise_model)
        tqc = transpile(qc, backend=simulator, \
                        basis_gates=my_noise_models.NoiseModel_NVCenter(n_qubits=n_qubits).basis_gates, \
                        optimization_level=0, \
                        coupling_map=my_noise_models.NoiseModel_NVCenter(n_qubits=n_qubits).coupling_map, \
                        initial_layout=layout)
        display(tqc.draw('mpl'))
        
        
        result = simulator.run(tqc,shots=shots,memory=True).result()
        ancilla_counts = result.get_counts()[(readout_string+' 00')]
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()
        
        print('\n')
        print("results for NV center:")
        print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
        
        error_rate = 1-( (result.get_counts()[(readout_string +' 00')]) /projection_counts['00'])
        
        print("error rate: ", 1-(ancilla_counts2[readout_string]/shots))
        print("postselected error rate: ", error_rate)
    
        print('theoretical estimation of error rate after postselection: '\
              ,1.0-((average_gate_fidelity(depolarizing_error(0.035,2)))**7)*(1-0.004)**5 )
        
        print(result.get_counts())
        print(projection_counts)
        print(ancilla_counts2)
            
        results_ = [l,round(error_rate,5)]
        results_.append(tqc.depth())
        results_.append(tqc.count_ops()['cx'])
        results_.append(tqc.size())
        results_.append(layout)
        results.append(results_)
        
    # sort by value
    aresults = [sublist[:-1] for sublist in results]
    sresults = sorted(aresults, key=itemgetter(1))
    sresults = np.array(sresults)
    aresults = np.array(aresults)
    
    myresults = sorted(results, key=itemgetter(1))
    # write to file
    #np.savetxt('s_op.dat',sresults)
# =============================================================================
#     with open(("nvcenter_list_withlayout_7qubits_noerror"+str(date.today())+".dat"), "w") as f:
#         f.write("#number\t logical error \t depth \t nb cnots \t size \t layout \n")
#         for result_ in myresults:
#             for el in result_: f.write(str(el)+"\t")
#             f.write("\n")
#         f.close()
# =============================================================================
    
    # plot results

    x = np.arange(len(sresults))
    plt.figure(figsize=(12.0,4.0))
    plt.xlabel('number of iteration over layout')
    plt.ylabel('logical error rates of the bitflip code')
    plt.bar(x,sresults[:,1], label='results for NV-center')
    #plt.bar(x,noerror_res[:,1], label='no gate')

    plt.legend()
    plt.show()
    
    np.savetxt('NVcenter_bitflip_realnoise_errorpos_2_shots200000_init_0_1_new.dat',sresults)
    print(myresults)





    
    
