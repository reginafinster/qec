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
import layout_tools

logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    
    path_to_binary = '\\noise_models\\noisemodel_ibmq_ehningen2022-05-27.dat'
    
    parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    path_to_binary = parentdir + path_to_binary
    
    pos_error=0
    # fall 2 unabhängige Stabilizer (00) for None, (01) for x[0], (11) for x[1], (10) for x[2]
    readout_string = '01' 
    #input_state = Input_Statevector(2,2).input_state_list_complex()[2] #wenn ich das verwenden will, noch den input_state übergeben
    input_state = [1.0,0.0]
    qc = codes.BitFlip_IBM(pos_error=pos_error,initialize=input_state).qc
    #qc = codes.IBM_untranspiled_bitflip(pos_error=pos_error).circuit()
    display(qc.draw('mpl'))
    
    shots = 200000
        
    NoiseModel = my_noise_models.NoiseModel_IBM(path_to_binary=path_to_binary)
    noise_model = NoiseModel.build_model()
    initial_layout = layout_tools.ConnectedSubgraphs(NoiseModel.coupling_map).find_connected_subgraphs()
    print(len(initial_layout))
    
    results = []

    for l, layout in enumerate(initial_layout):
        
        print(layout)
        simulator = AerSimulator(noise_model=noise_model)
        tqc = transpile(qc, backend=simulator, \
                        optimization_level=0, \
                        coupling_map=NoiseModel.coupling_map,\
                        basis_gates=NoiseModel.basis_gates,\
                        initial_layout=layout[0])
        #display(tqc.draw('mpl', idle_wires=False))
        print("number of cnots: ", tqc.count_ops()['cx'])
        
        
        result = simulator.run(qc,shots=shots,memory=True).result()
        ancilla_counts = result.get_counts()[(readout_string+' 00')]        
        projection_counts = marginal_counts(result, indices=[0,1]).get_counts()
        ancilla_counts2 = marginal_counts(result, indices=[2,3]).get_counts()
        
        print('\n')
        print("results for IBM chip:")
        print("rate of counts out of code space: ",  (1.0-(projection_counts['00']/shots)))
        
        error_rate = 1-( (result.get_counts()[(readout_string +' 00')]) /projection_counts['00'])
        
        print("error rate: ", 1-(ancilla_counts2[readout_string]/shots))
        print("postselected error rate: ", error_rate)
    
        print('theoretical estimation of error rate after postselection: '\
              ,1.0-((average_gate_fidelity(depolarizing_error(0.035,2)))**7)*(1-0.004)**5 )
        
        print(result.get_counts())
        print(projection_counts)
        print(ancilla_counts2)
        #init_dmatrix = result.data()['init_dmatrix']
        #print(init_dmatrix)
            
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
    
    # plot results
    x = np.arange(len(sresults[:20]))
    plt.figure(figsize=(12.0,4.0))
    plt.xlabel('number of iteration over layout')
    plt.ylabel('logical error rates')
    plt.bar(x,sresults[:20,1], label='logical error rate sc processor')
    plt.legend()
    plt.show()
    
    np.savetxt('ibm_processor_bitflip_error0_initstate_superpos_200000shots.dat', sresults)





    
    
