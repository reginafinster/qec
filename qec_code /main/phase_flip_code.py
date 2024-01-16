# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 12:08:33 2022

@author: regina
"""

from qiskit.providers.aer import AerSimulator
from qiskit import transpile, QuantumCircuit,\
    QuantumRegister, ClassicalRegister, BasicAer
from qiskit.visualization import plot_histogram
import numpy as np
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.result import marginal_counts



class PhaseFlipUnitaryCorrection_IBM:
    
    def __init__(self,pos_error):
        self.pos_error = pos_error
    
    def transpiled_ccz(self,cq1,cq2,tq):
        qc.cx(cq2,tq)
        qc.rz(-np.pi*0.25,tq)
        qc.cx(cq1,tq)
        qc.rz(np.pi*0.25,tq)
        qc.cx(cq2,tq)
        qc.rz(-np.pi*0.25,tq)
        qc.rz(np.pi*0.25,cq2)
        qc.cx(cq1,tq)
        qc.rz(np.pi*0.25,tq)
        qc.cx(cq1,cq2)
        qc.rz(np.pi*0.25,cq1)
        qc.rz(-np.pi*0.25,cq2)
        qc.cx(cq1,cq2)
        
    def transpiled_h(self,q):
        qc.rz(np.pi*0.5,q)
        qc.sx(q)
        qc.rz(np.pi*0.5,q)

    
    def circuit(self):   
        q = QuantumRegister(5)
        c1 = ClassicalRegister(3)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        #qc.x(0)
        
        # 0,1,2 code, 3,4 ancilla
        # create cat state
        # swap operations depend on the chosen initial layout [3,0,1,2,4]
        qc.cx(0,1)
        qc.cx(1,2)
        qc.h([0,1,2])
        
        qc.barrier()
        qc.swap(2,4)
        qc.swap(0,3)
        qc.barrier()
        
        # 3,1,4 code, 0,2 ancilla
        
        # noisy evolution
        if self.pos_error==None:
            pass
        elif self.pos_error==0:
            qc.z(3)
        elif self.pos_error==1:
            qc.z(1)
        elif self.pos_error==2:
            qc.z(4)
        
        qc.barrier()
        
        # measure stabilizer
        qc.h([3,1,4])
        
        qc.cx(3,0)
        qc.cx(1,0)
        
        qc.cx(1,2)
        qc.cx(4,2)
        
        qc.h([3,1,4])
        
        qc.barrier()

        # unitary correction
        
        # transpiled ccz(4,3,1), also (4->2,3->0,1->1)
        # dh. Bedingung für Korrektur auf q1 ist dass q3=1,q4=1
        qc.cx(0,1)
        qc.rz(-np.pi*0.25,1)
        qc.cx(2,1)
        qc.rz(np.pi*0.25,1)
        qc.cx(0,1)
        qc.rz(-np.pi*0.25,1)
        qc.rz(np.pi*0.25,0)
        qc.cx(2,1)
        qc.rz(np.pi*0.25,1)
        
        qc.barrier()
        qc.swap(1,2)
        # 3,2,4 code, 0,1 ancilla
        qc.barrier()
        
        # Fortsetzung transpiled ccz(4,3,1), also jetzt (4->1,3->0,1->2)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        qc.barrier()
        qc.swap(3,0)
        # 0,2,4 code, 3,1 ancilla
        qc.barrier()
        
        # transpiled ccz(4,3,0), also jetzt (4->1,3->3,0->0)
        # dh. Bedingung für Korrektur auf q0 ist dass q3=1,q4=0
        qc.x(1)
        
        qc.cx(3,0)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,0)
        qc.cx(3,0)
        qc.rz(-np.pi*0.25,0)
        qc.rz(np.pi*0.25,3)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,0)
        
        qc.barrier()
        qc.swap(0,3)
        # 3,2,4 code, 0,1 ancilla
        qc.barrier()
        
        
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        qc.x(1)
        
        qc.barrier()
        qc.swap(2,4)
        # 3,4,2 code, 0,1 ancilla

        qc.swap(1,2)
        # 3,4,1 code, 0,2 ancilla
        qc.barrier()
        
        # transpiled ccz(4,3,2), also jetzt (4->2,3->0,2->1)
        # dh. Bedingung für Korrektur auf q2 ist dass q3=0,q4=1
        qc.x(0)
        
        qc.cx(0,1)
        qc.rz(-np.pi*0.25,1)
        qc.cx(2,1)
        qc.rz(np.pi*0.25,1)
        qc.cx(0,1)
        qc.rz(-np.pi*0.25,1)
        qc.rz(np.pi*0.25,0)
        qc.cx(2,1)
        qc.rz(np.pi*0.25,1)
        
        qc.barrier()
        qc.swap(1,2)
        # 3,4,2 code, 0,1 ancilla
        qc.barrier()

        # weiter transpiled ccz(4,3,2), also jetzt (4->1,3->0,2->2)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        qc.x(0)
        
        qc.barrier()
        qc.swap(0,3)
        qc.swap(0,1)
        qc.swap(1,2)
        # 2,4,1 code, 3,0 ancilla
        qc.barrier()
       
        # decode
        qc.h([2,4,1])
        qc.cx(2,4)
        qc.cx(2,1)
        
        qc.measure([2,4,1],c1)
        qc.measure([3,0],c2)
        
        return qc
    
    def bitflip_code_only_detection_with_cat_state(self):
        q = QuantumRegister(5)
        c1 = ClassicalRegister(2)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        # initialize some state
        #qc.x(0)
        
        qc.cx(0,1)
        qc.cx(1,2)
        
        qc.barrier()
        qc.swap(2,4)
        qc.swap(0,3)
        qc.barrier()
        # 3,1,4 code, 0,2 ancilla
        
        # measure stabilizer
        
        qc.cx(3,0)
        qc.cx(1,0)
        
        qc.cx(1,2)
        qc.cx(4,2)
        qc.measure([0,2],c1)
    
        qc.barrier()
        # noisy evolution
        if self.pos_error==None:
            pass
        elif self.pos_error==0:
            qc.z(3)
        elif self.pos_error==1:
            qc.z(1)
        elif self.pos_error==2:
            qc.z(4)
        
        qc.barrier()
        
        # measure stabilizer
        
        qc.cx(3,0)
        qc.cx(1,0)
        
        qc.cx(1,2)
        qc.cx(4,2)
        
        qc.measure([0,2],c2)
        
        return qc


    
if __name__ == "__main__":
  
    qc = PhaseFlipUnitaryCorrection_IBM(None).circuit()
    #qc = PhaseFlipUnitaryCorrection_IBM(1).bitflip_code_only_detection_with_cat_state()
        
    display(qc.draw('mpl'))
    
    basis_gates = ['cx','id','rz','sx','x']
    coupling_map = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]
    initial_layout = [1,2,3,0,4]

    
    simulator = AerSimulator()
    tqc = transpile(qc, backend=simulator, basis_gates=basis_gates, \
                    optimization_level=0, coupling_map=coupling_map, \
                        initial_layout=initial_layout)

    display(tqc.draw('mpl'))
        
    result = simulator.run(tqc,shots=shots,memory=True).result()
    code_counts = marginal_counts(result, indices=[0,1,2]).get_counts()
    ancilla_counts = marginal_counts(result, indices=[3,4]).get_counts()
    
    print(result.get_counts(), code_counts, ancilla_counts)
    #display(plot_histogram(result.get_counts()))
    
    
    