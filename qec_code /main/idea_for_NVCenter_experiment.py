# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 15:30:59 2022

@author: regina
"""

from qiskit.providers.aer import AerSimulator
from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
import itertools


if __name__ == "__main__":
    
    pos_error = 3
    n_qubits = 4
    q = QuantumRegister(4)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q,c)
    
    # create cat state using electron spin as mediator
    qc.cx(1,0)
    qc.cx(0,2)
    qc.cx(0,3)
    qc.cx(1,0)
    qc.barrier()
    
    # noisy evolution
    if pos_error==None:
        pass
    else:
        qc.x(int(pos_error))
    
    qc.barrier()
    # decode
    qc.cx(1,0)
    qc.cx(0,3)
    qc.cx(0,2)
    qc.cx(1,0)
    qc.measure([2,3],c)
    qc.draw('mpl')
    
    coupling_map = [ [i+1,0] for i in range(n_qubits-1)] + [ [0,i+1] for i in range(n_qubits-1)]
    
    initial_layout = [i for i in range(n_qubits)]
    
    basis_gates = ['x','y','rx','ry','id','cx']

    simulator = AerSimulator(noise_model=None)
    
    tqc = transpile(qc, backend=simulator, basis_gates=None, \
                    optimization_level=0, coupling_map=coupling_map, \
                        initial_layout=None)

    result = simulator.run(tqc,shots=shots,memory=True).result()
    print(result.get_counts())
