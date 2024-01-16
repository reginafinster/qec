# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 11:36:48 2022

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
from qiskit.providers.aer.noise import *
from qiskit.quantum_info import *

# =============================================================================
# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
# #sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
# import my_noise_models
# import codes
# =============================================================================

# set up logger
logger_ = logging.getLogger()
logger_.setLevel(logging.WARNING)


if __name__ == "__main__":
    
    
    qc = QuantumCircuit(2,2)
    qc.h(0)
    #qc.x(0)
    qc.cx(0,1)
    qc.measure_all()
    
    my_noise_model = NoiseModel()
    single_thermal_error = thermal_relaxation_error(t1=0.0001, t2=0.0001, time=0.000005)
    no_error = pauli_error([('I', 1.0)])
    #double_depol_error = no_error.tensor(single_depol_error)
    double_thermal_error = single_thermal_error.tensor(no_error)
    my_noise_model.add_quantum_error(double_thermal_error,'cx',[0,1])
    print(double_thermal_error)
    #single_depol_error = depolarizing_error(0.1,1)
    #double_depol_error = single_depol_error.tensor(single_depol_error)
    #my_noise_model.add_quantum_error(double_depol_error,'cz',[0,1])
    #my_noise_model.add_quantum_error(single_thermal_error,['x'],[0])
    print(my_noise_model)
    
    simulator = AerSimulator(noise_model=my_noise_model)
    tqc = transpile(qc, backend=simulator)
    display(tqc.draw('mpl'))
    
    result = simulator.run(tqc,shots=20000,memory=True).result()
    print(result.get_counts())
    
    
    
    
    
    
    