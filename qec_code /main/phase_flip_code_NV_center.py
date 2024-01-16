# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 14:09:06 2022

@author: regina
"""

from qiskit.providers.aer import AerSimulator
from qiskit import transpile, QuantumCircuit,\
    QuantumRegister, ClassicalRegister, BasicAer
from qiskit.visualization import plot_histogram
import numpy as np
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.result import marginal_counts


class PhaseFlipUnitaryCorrection_NV:
    
    def __init__(self,pos_error):
        self.pos_error = pos_error
        self.c2rx_11 = self.c2rx_11()
        self.c3rx_111 = self.c3rx_111()
        self.c3rx_101 = self.c3rx_101()
        self.c3rx_110 = self.c3rx_110()

    
    def c3rx_111(self):
        arr = np.identity(16)
        arr[7,7] = -1.0
        arr[15,15] = -1.0
        return Operator(arr)
    
    def c3rx_101(self):
        arr = np.identity(16)
        arr[5,5] = -1.0
        arr[13,13] = -1.0
        return Operator(arr)
    
    def c3rx_110(self):
        arr = np.identity(16)
        arr[3,3] = -1.0
        arr[11,11] = -1.0
        return Operator(arr)
    
    def c2rx_11(self):
        arr = np.identity(8)
        arr[3,3] = -1.0
        arr[7,7] = -1.0
        return Operator(arr)
    
    def circuit(self):   
        q = QuantumRegister(6)
        c1 = ClassicalRegister(3)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        # encode
        qc.ry(-0.5*np.pi,[2,3])
        qc.unitary(self.c2rx_11,[1,2,0],label='c2rx')
        qc.unitary(self.c2rx_11,[1,3,0],label='c2rx')
        qc.ry(-0.5*np.pi,1)
        
        # noisy evolution in phase
        qc.barrier()
        if self.pos_error==None:
            pass
        else:
            qc.z(int(self.pos_error))
        qc.barrier()
        
        # stabilizer:
        # basis change
        qc.ry(0.5*np.pi,[1,2,3])
        
        # transfer to ancillae
        qc.ry(-0.5*np.pi,[4,5])
        qc.unitary(self.c2rx_11,[1,4,0],label='c2rx')
        qc.unitary(self.c2rx_11,[2,4,0],label='c2rx')
        
        qc.unitary(self.c2rx_11,[2,5,0],label='c2rx')
        qc.unitary(self.c2rx_11,[3,5,0],label='c2rx')
        qc.ry(0.5*np.pi,[4,5])
        
        # basis change
        qc.ry(-0.5*np.pi,[1,2,3])
        qc.measure([4,5],c2)
        
        # unitary correction
        qc.unitary(self.c3rx_111,[2,4,5,0],label='c3rx')
        qc.unitary(self.c3rx_110,[1,4,5,0],label='c3rx')
        qc.unitary(self.c3rx_101,[3,4,5,0],label='c3rx')
        
        # decode
        qc.ry(0.5*np.pi,[1,2,3])
        
        qc.measure([1,2,3],c1)
        
        return qc
        
    
if __name__ == "__main__":
  
    qc = PhaseFlipUnitaryCorrection_NV(1).circuit()
        
    display(qc.draw('mpl'))

    shots = 200
    simulator = AerSimulator()
    tqc = transpile(qc, backend=simulator, optimization_level=0,\
                    coupling_map=None, initial_layout=None)

    display(tqc.draw('mpl')) 
    result = simulator.run(tqc,shots=shots,memory=True).result()
    print(result.get_counts())
    
    