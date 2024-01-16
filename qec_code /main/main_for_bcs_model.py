# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 15:30:59 2022

@author: regina
"""

from qiskit.providers.aer import AerSimulator
from qiskit import transpile, QuantumCircuit
import itertools


if __name__ == "__main__":
    
    n_spins = 6
    shots = 200000
    
    qc = QuantumCircuit(n_spins)
    qc.measure_all()
    
    coupling_map = [ [i+1,0] for i in range(n_spins-1)] + [ [0,i+1] for i in range(n_spins-1)]
    
    initial_layout = [i for i in range(n_spins)]
    
    basis_gates = ['x','y','rx','ry','id','cx']

    simulator = AerSimulator(noise_model=None)
    
    tqc = transpile(qc, backend=simulator, basis_gates=None, \
                    optimization_level=0, coupling_map=coupling_map, \
                        initial_layout=None)

    result = simulator.run(tqc,shots=shots,memory=True).result()
    print(result.get_counts())
