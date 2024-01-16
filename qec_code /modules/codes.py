# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 10:59:53 2021

@author: regina
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info.operators import Operator, Pauli

class PhaseFlipUnitaryCorrection_NV:
    
    def __init__(self,pos_error,initialize=False,input_statevector=False,use_input_statevector=False):
        self.pos_error = pos_error
        self.initialize = initialize
        self.input_statevector = input_statevector
        self.use_input_statevector=use_input_statevector
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
        
        if self.use_input_statevector:
            # initialize some state, encoded qubit is number 1!
            my_statevector = np.zeros(64,dtype=complex)
            my_statevector[0] = self.input_statevector[0]
            my_statevector[2] = self.input_statevector[1]
            qc.set_statevector(my_statevector)
        elif self.use_input_statevector==False:
            my_initial_state = [self.initialize[0],
                                self.initialize[1]]
            qc.initialize(my_initial_state, 1)
        
# =============================================================================
#         # initialize some state, encoded qubit is number 1!
#         if input_state:
#             my_initial_state = [np.sqrt(input_state[0]), np.sqrt(input_state[1])]
#             qc.initialize(my_initial_state, 1)
# =============================================================================
        
        # encode
        qc.ry(-0.5*np.pi,[2,3])
        qc.unitary(self.c2rx_11,[1,2,0],label='c2rx')
        qc.unitary(self.c2rx_11,[1,3,0],label='c2rx')
        qc.ry(-0.5*np.pi,1)
        
        qc.save_density_matrix([q[1],q[2],q[3]],label='init_dmatrix')

        # noisy evolution in phase
        #qc.barrier()
        if self.pos_error==None:
            pass
        else:
            qc.z(int(self.pos_error))
        #qc.barrier()
        
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
        
        # unitary correction
        qc.unitary(self.c3rx_111,[2,4,5,0],label='c3rx')
        qc.unitary(self.c3rx_110,[1,4,5,0],label='c3rx')
        qc.unitary(self.c3rx_101,[3,4,5,0],label='c3rx')
        
        qc.save_density_matrix([q[1],q[2],q[3]],label='result_dmatrix')

        # decode
        qc.ry(0.5*np.pi,[1,2,3])
        
        qc.measure([1,2,3],c1)
        qc.measure([4,5],c2)

        return qc
    
    
class PhaseFlipUnitaryCorrection_IBM_veraltet:
    
    def __init__(self,pos_error,initialize=False,input_statevector=False,use_input_statevector=False):
        self.pos_error = pos_error
        self.initialize = initialize
        self.input_statevector = input_statevector
        self.use_input_statevector = use_input_statevector
    
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
        
        if self.use_input_statevector:
            my_statevector = np.zeros(32,dtype=complex)
            my_statevector[0] = self.input_statevector[0]
            my_statevector[1] = self.input_statevector[1]
            qc.set_statevector(my_statevector)
        else:
            my_initial_state = [self.initialize[0],
                                self.initialize[1]]
            qc.initialize(my_initial_state, 0)
            
        #qc.save_density_matrix([q[0]],label='init_dmatrix')
        
        
        # 0,1,2 code, 3,4 ancilla
        # create cat state
        # swap operations depend on the chosen initial layout [3,0,1,2,4]
        qc.cx(0,1)
        qc.cx(1,2)
        qc.h([0,1,2])
        
        #qc.save_density_matrix([q[0],q[1],q[2]],label='init_dmatrix')
        
        #qc.barrier()
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
        
        #qc.barrier()

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
        
        #qc.barrier()
        qc.swap(1,2)
        # 3,2,4 code, 0,1 ancilla
        #qc.barrier()
        
        # Fortsetzung transpiled ccz(4,3,1), also jetzt (4->1,3->0,1->2)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        #qc.barrier()
        qc.swap(3,0)
        # 0,2,4 code, 3,1 ancilla
        #qc.barrier()
        
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
        
        #qc.barrier()
        qc.swap(0,3)
        # 3,2,4 code, 0,1 ancilla
        #qc.barrier()
        
        
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        qc.x(1)
        
        #qc.barrier()
        qc.swap(2,4)
        # 3,4,2 code, 0,1 ancilla

        qc.swap(1,2)
        # 3,4,1 code, 0,2 ancilla
        #qc.barrier()
        
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
        
        #qc.barrier()
        qc.swap(1,2)
        # 3,4,2 code, 0,1 ancilla
        #qc.barrier()

        # weiter transpiled ccz(4,3,2), also jetzt (4->1,3->0,2->2)
        qc.cx(1,0)
        qc.rz(np.pi*0.25,1)
        qc.rz(-np.pi*0.25,0)
        qc.cx(1,0)
        
        qc.x(0)
        
        #qc.save_density_matrix([q[3],q[4],q[2]],label='result_dmatrix')

        #qc.barrier()
        qc.swap(0,3)
        qc.swap(0,1)
        qc.swap(1,2)
        # 2,4,1 code, 3,0 ancilla
        #qc.barrier()
        
       
        # decode
        qc.h([2,4,1])
        qc.cx(2,4)
        qc.cx(2,1)
        
        qc.measure([2,4,1],c1)
        qc.measure([3,0],c2)
        
        return qc
    
class PhaseFlipUnitaryCorrection_without_transpilation_SC:
    
    def __init__(self,pos_error):
        self.pos_error = pos_error
        self.ccz = self.ccz()
        
    def ccz(self):
        arr = np.identity(8)
        arr[7,7] = -1.0
        return Operator(arr)
    
    def circuit(self):   
        q = QuantumRegister(5)
        c1 = ClassicalRegister(3)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        # some initial state
        #qc.x(0)
        
        # create cat state
        qc.cx(0,1)
        qc.cx(1,2)
        qc.h([0,1,2])
        
        qc.barrier()
        #qc.save_statevector(label='init_statevector')
        #qc.save_density_matrix([0,1,2],label='init_dmatrix')
        
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.z(int(self.pos_error))
        
        qc.barrier()
        
        # measure stabilizer
        qc.h([0,1,2])
        
        qc.cx(0,3)
        qc.cx(1,3)
        
        qc.cx(1,4)
        qc.cx(2,4)
        
        qc.h([0,1,2])
        
        # transpiled ccz(4,3,1)
        # dh. Bedingung für Korrektur auf q1 ist dass q3=1,q4=1
        qc.unitary(self.ccz,[4,3,1],label='ccz')

        # transpiled ccz(4,3,0)
        # dh. Bedingung für Korrektur auf q0 ist dass q3=1,q4=0
        qc.x(4)
        qc.unitary(self.ccz,[4,3,0],label='ccz')
        qc.x(4)
        
        # transpiled ccz(4,3,2)
        # dh. Bedingung für Korrektur auf q2 ist dass q3=0,q4=1
        qc.x(3)
        qc.unitary(self.ccz,[4,3,2],label='ccz')
        qc.x(3)
        
# =============================================================================
#         qc.barrier()
#         qc.x(0)
#         qc.barrier()
#         qc.x(1)
#         qc.barrier()
#         qc.x(2)
#         qc.barrier()
# =============================================================================
        
        #qc.save_density_matrix([0,1,2],label='result_dmatrix')
        #qc.save_statevector(label='result_statevector')
        
        return qc
    
class TranspiledPhaseFlip_SCProcessor:
    
    def __init__(self,pos_error,use_input_statevector=False,input_statevector=None,initialize=None): 
        self.pos_error = pos_error
        self.use_input_statevector = use_input_statevector
        self.input_statevector = input_statevector
        self.initialize = initialize
    
    def circuit(self):
        #define initial layout
        # initial layout (3,2,4,1,0) also heißen die qubits (4,3,1,0,2)
        q0=4
        q1=3
        q2=1
        q3=0
        q4=2
        
        q = QuantumRegister(5,name="q")
        qc = QuantumCircuit(q)
        
        if self.use_input_statevector:
            print("using input statevector")
            my_statevector = np.zeros(32,dtype=complex)
            my_statevector[0] = self.input_statevector[0]
            my_statevector[1] = self.input_statevector[1]
            qc.set_statevector(my_statevector)
            #qc.save_statevector(label='init_statevector')
        else:
            print("using initialize")
            my_initial_state = [self.initialize[0],
                                self.initialize[1]]
            qc.initialize(my_initial_state, q3)
        
        #qc.save_statevector(label='init_statevector')
        qc.cx(q3,q2)

        qc.cx(q1,q2)
        qc.cx(q2,q1)
        qc.cx(q1,q2)
        
        qc.rz(np.pi/2,q3)
        qc.sx(q3)
        qc.rz(np.pi/2,q3)
        
        qc.cx(q1,q4)
        
        qc.rz(np.pi/2,q1)
        qc.sx(q1)
        qc.rz(np.pi/2,q1)
        
        qc.rz(np.pi/2,q4)
        qc.sx(q4)
        qc.rz(np.pi/2,q4)
        
        #qc.save_statevector(label='init_statevector')
        
        qc.save_density_matrix([q3,q1,q4],label='init_dmatrix')
        
        qc.barrier()
        
        # noisy evolution
        if self.pos_error==None:
            pass
        elif self.pos_error==0:
            qc.z(q3)
        elif self.pos_error==1:
            qc.z(q1)
        elif self.pos_error==2:
            qc.z(q4)
        
        qc.barrier()
        
        qc.rz(np.pi/2,q1)
        qc.sx(q1)
        qc.rz(np.pi/2,q1)
        
        qc.rz(np.pi/2,q3)
        qc.sx(q3)
        qc.rz(np.pi/2,q3)
        
        qc.rz(np.pi/2,q4)
        qc.sx(q4)
        qc.rz(np.pi/2,q4)
        
        qc.cx(q3,q2)
        
        qc.rz(np.pi/2,q3)
        qc.sx(q3)
        qc.rz(np.pi/2,q3)
        
        qc.cx(q1,q2)
        qc.cx(q0,q1)
        qc.cx(q1,q0)
        qc.cx(q4,q1)
        
        qc.rz(np.pi/2,q0)
        qc.sx(q0)
        qc.rz(np.pi/2,q0)
        
        qc.rz(np.pi/4,q1)
        qc.cx(q2,q1)
        qc.rz(-np.pi/4,q1)
        
        qc.cx(q0,q1)
        
        qc.rz(np.pi/2,q4)
        qc.sx(q4)
        qc.rz(np.pi/2,q4)
        
        qc.rz(np.pi/4,q1)
        qc.cx(q2,q1)
        qc.rz(-np.pi/4,q1)
        qc.cx(q0,q1)
        qc.cx(q1,q2)
        qc.cx(q2,q1)
        qc.cx(q1,q2)
        
        qc.rz(np.pi/4,q1)
        
        qc.x(q2)
        qc.rz(np.pi/4,q2)
        qc.cx(q0,q1)
        qc.rz(-np.pi/4,q1)
        qc.cx(q0,q1)
        qc.rz(np.pi/4,q0)
        qc.cx(q1,q2)
        
        qc.rz(-np.pi/4,q2)
        qc.cx(q3,q2)
        qc.rz(np.pi/4,q2)
        qc.cx(q1,q2)
        qc.rz(-np.pi/4,q2)
        qc.cx(q3,q2)
        qc.cx(q1,q2)
        qc.cx(q2,q1)
        qc.cx(q1,q2)
        qc.x(q1)
        
        qc.rz(np.pi/4,q2)
        qc.rz(np.pi/4,q1)
        qc.cx(q3,q2)
        qc.rz(-np.pi/4,q2)
        qc.cx(q3,q2)
        
        qc.x(q2)
        qc.rz(np.pi/4,q3)
        qc.cx(q2,q1)
        qc.rz(-np.pi/4,q1)
        qc.cx(q4,q1)
        qc.rz(np.pi/4,q1)
        qc.cx(q2,q1)
        
        qc.rz(-np.pi/4,q1)
        qc.rz(np.pi/4,q2)
        
        qc.cx(q1,q4)
        qc.cx(q4,q1)
        
        qc.cx(q1,q2)
        qc.rz(-np.pi/4,q2)
        qc.cx(q1,q2)
        qc.rz(np.pi/4,q1)
        qc.x(q2)
        
        #qc.measure([q2,q4],c)
        qc.save_density_matrix([q3,q0,q1],label='result_dmatrix')
        #qc.save_statevector(label='result_statevector')

        return qc

class PhaseFlipUnitaryCorrection_without_layout_swaps_IBM:
    
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
        
        # some initial state
        #qc.x(0)
        
        # create cat state
        qc.cx(0,1)
        qc.cx(1,2)
        qc.h([0,1,2])
        
        qc.barrier()
        
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.z(int(self.pos_error))
        
        qc.barrier()
        
        # measure stabilizer
        qc.h([0,1,2])
        
        qc.cx(0,3)
        qc.cx(1,3)
        
        qc.cx(1,4)
        qc.cx(2,4)
        
        qc.h([0,1,2])
        
        #qc.barrier()
        
        # unitary correction
        
        # transpiled ccz(4,3,1)
        # dh. Bedingung für Korrektur auf q1 ist dass q3=1,q4=1
        qc.cx(3,1)
        qc.rz(-np.pi*0.25,1)
        qc.cx(4,1)
        qc.rz(np.pi*0.25,1)
        qc.cx(3,1)
        qc.rz(-np.pi*0.25,1)
        qc.rz(np.pi*0.25,3)
        qc.cx(4,1)
        qc.rz(np.pi*0.25,1)
        qc.cx(4,3)
        qc.rz(np.pi*0.25,4)
        qc.rz(-np.pi*0.25,3)
        qc.cx(4,3)
        
        
        # transpiled ccz(4,3,0)
        # dh. Bedingung für Korrektur auf q0 ist dass q3=1,q4=0
        qc.x(4)
        
        qc.cx(3,0)
        qc.rz(-np.pi*0.25,0)
        qc.cx(4,0)
        qc.rz(np.pi*0.25,0)
        qc.cx(3,0)
        qc.rz(-np.pi*0.25,0)
        qc.rz(np.pi*0.25,3)
        qc.cx(4,0)
        qc.rz(np.pi*0.25,0)
        qc.cx(4,3)
        qc.rz(np.pi*0.25,4)
        qc.rz(-np.pi*0.25,3)
        qc.cx(4,3)
        
        qc.x(4)
        
        # transpiled ccz(4,3,2)
        # dh. Bedingung für Korrektur auf q2 ist dass q3=0,q4=1
        
        qc.x(3)
        
        qc.cx(3,2)
        qc.rz(-np.pi*0.25,2)
        qc.cx(4,2)
        qc.rz(np.pi*0.25,2)
        qc.cx(3,2)
        qc.rz(-np.pi*0.25,2)
        qc.rz(np.pi*0.25,3)
        qc.cx(4,2)
        qc.rz(np.pi*0.25,2)
        qc.cx(4,3)
        qc.rz(np.pi*0.25,4)
        qc.rz(-np.pi*0.25,3)
        qc.cx(4,3)
        
        qc.x(3)
        
        #qc.barrier()

        # decode
        qc.cx(0,1)
        qc.cx(0,2)
        qc.h([0,1,2])
        
        qc.measure([0,1,2],c1)
        qc.measure([3,4],c2)
        
        return qc


class BitFlip_NVCenter:
    
    def __init__(self, pos_error, input_statevector=False,
                 initialize=False,input_mixedstate=False,set_input_statevector=False):
        self.pos_error = pos_error
        self.input_statevector = input_statevector
        self.initialize = initialize
        self.input_mixedstate = input_mixedstate
        self.set_input_statevector=set_input_statevector
        
        
    def test_methods(self):
        '''
        Die Methode, unterwegs die Dichtematrix zu speichern und dann zu vergleichen,
        macht vor allem dann Sinn, wenn ich bereits den verrauschten Code betrachte.
        Wenn ich einen Code ohne Fehler testen will, dann bietet sich an, den 
        Statevector zu simulieren.

        Returns
        -------
        None.

        '''
      
        # #################################
        # test with density matrix from experiment
        ###################################
      
        # set up pure initial state (optional)
        #y_initial_state = [1/np.sqrt(2), 1/np.sqrt(2)]
        #qc.initialize(y_initial_state, p[0])
        
        # set up mixed initial state
        #mixedstate = np.zeros((512,512))
        #mixedstate[0][0] = 0.5
        #mixedstate[1][1] = 0.5
        #rho = [[0.95+0.j, 0.0+0.0j],[0.0+0.0j,0.05+0.j]]
        #qc.set_density_matrix(mixedstate)
        
        # save inital state
        #qc.save_density_matrix(label='init_dmatrix')
        #qc.save_density_matrix([p[0]], label='init_dmatrix')
        qc.save_density_matrix([p[0]], label = 'single_init_dmatrix')
        
        # #################################
        # some code
        ###################################
        
        qc.save_density_matrix(p, label='init_dmatrix')
        
        
        # print out results
        init_dmatrix = result.data()['init_dmatrix']
        corr_dmatrix = result.data()['corr_dmatrix']
        init2_dmatrix = result.data()['single_init_dmatrix']
        corr2_dmatrix = result.data()['decoded_dmatrix']
        
        fid = state_fidelity(init_dmatrix, corr_dmatrix)
        fid0 = state_fidelity(init2_dmatrix, corr2_dmatrix)
        
        # #################################
        # test with state vector simulator
        ###################################
        
        backend = StatevectorSimulator()
        job = backend.run(circ)
        result = job.result()
        outputstate = result.get_statevector(circ, decimals=3)
        print(outputstate)
        from qiskit.visualization import plot_state_city
        plot_state_city(outputstate)
    
    
    def test_bitflip_detection_NV_center(self):
        '''
        test encoding, Korrektur und decoding
        Achtung, hier ist der zentrale Spin noch die Nummer 5!!

        Returns
        -------
        None.

        '''
        q = QuantumRegister(6)
        c1 = ClassicalRegister(2)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1)
        
# =============================================================================
#         # set up pure initial state (optional)
#         my_initial_state = [np.sqrt(0.9), np.sqrt(0.1)]
#         #my_initial_state = [1/np.sqrt(2), 1/np.sqrt(2)]
#         qc.initialize(my_initial_state, 0)
# 
# =============================================================================
        mixedstate = np.zeros((64,64))
        mixedstate[0][0] = 0.9
        mixedstate[1][1] = 0.1
        qc.set_density_matrix(mixedstate)
        
        #qc.save_density_matrix([0],label='init_dmatrix')
        # create cat state using electron spin as mediator
        #qc.x(0)
        qc.cx(0,5)
        qc.cx(5,1)
        qc.cx(5,2)
        qc.cx(0,5)
        
        qc.save_density_matrix([0,1,2],label='init_dmatrix')

        #qc.save_density_matrix([0,1,2],label='init_dmatrix')
        qc.barrier()
        
# =============================================================================
#         # noisy evolution
#         if self.pos_error==None:
#             pass
#         else:
#             qc.x(int(self.pos_error))
# =============================================================================
        
        # project into code space and measure
        # measure first stabilizer on electron spin
        #qc.cx(0,5)
        qc.cx(0,5)
        qc.cx(1,5)
        
        # state transfer to first ancilla
        qc.cx(5,3)
        
        # measure second stabilizer on electron spin
        qc.cx(1,5)
        qc.cx(2,5)
        
        # state transfer to second ancilla
        qc.cx(5,4)
        
        # correct state of electron spin
        qc.cx(4,5)
        
        # measure using electron spin destructively
        qc.barrier()
        
        qc.measure([3,4],c1)
        qc.reset(5)
        
# =============================================================================
#         # correction of noisy evolution
#         if self.pos_error==None:
#             pass
#         else:
#             qc.x(int(self.pos_error))
# =============================================================================
        
        qc.barrier()
        
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
        
        qc.barrier()
        
        # measure first stabilizer on electron spin
        qc.cx(0,5)
        qc.cx(1,5)
        
        # state transfer to first ancilla
        qc.cx(5,3)

        # measure second stabilizer on electron spin
        qc.cx(1,5)
        qc.cx(2,5)
        
        # state transfer to second ancilla
        qc.cx(5,4)
        
        # correct state of electron spin
        qc.cx(4,5)
        
        # measure using electron spin destructively
        qc.barrier()
        
        qc.measure([3,4],c1)
        
        # correction of noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
            
        qc.save_density_matrix([0,1,2],label='final_dmatrix')

        
        # decode
        qc.cx(0,5)
        qc.cx(5,1)
        qc.cx(5,2)
        qc.cx(0,5)
        
        
        return qc

    
    def fivequbits(self):
        q = QuantumRegister(6)
        c1 = ClassicalRegister(2)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        # create cat state using electron spin as mediator
        qc.cx(1,0)
        qc.cx(0,2)
        qc.cx(0,3)
        
        qc.barrier()
        
        # project into code space and measure
        # measure first stabilizer on electron spin
        qc.cx(2,0)
        
        # state transfer to first ancilla
        qc.cx(0,4)
        
        # measure second stabilizer on electron spin
        qc.cx(2,0)
        qc.cx(3,0)
        
        # state transfer to second ancilla
        qc.cx(0,5)
        
        # correct state of electron spin
        qc.cx(5,0)
        
        # measure using electron spin destructively
        qc.barrier()
        
        qc.measure([4,5],c1)
        qc.reset(0)
        
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
        
        qc.barrier()
        
        # measure first stabilizer on electron spin
        qc.cx(1,0)
        qc.cx(2,0)
        
        # state transfer to first ancilla
        qc.cx(0,4)
        
        # measure second stabilizer on electron spin
        qc.cx(2,0)
        qc.cx(3,0)
        
        # state transfer to second ancilla
        qc.cx(0,5)
        
        # correct state of electron spin
        qc.cx(5,0)
        
        # measure using electron spin destructively
        qc.barrier()
        
        qc.measure([4,5],c2)
        
        return qc
    
    def measure_at_end(self):
        '''
        code qubits are 1,2,3. 0 is electron spin. 4,5 are ancillae

        '''
        q = QuantumRegister(8,'q')
        c1 = ClassicalRegister(2,'c1')
        c2 = ClassicalRegister(2,'c2')
        qc = QuantumCircuit(q,c1,c2)
        
        # initialize in some pure state, state is initially on qubit 1!!!
        # (because electron spin is on qubit 0)
        if self.set_input_statevector==True:
            print("error")
            # noch fertigmachen
# =============================================================================
#             my_statevector = np.zeros(32)
#             my_statevector[0] = self.input_statevector[0]
#             my_statevector[1] = self.input_statevector[1]
#             qc.set_statevector(my_statevector)
# =============================================================================
        else:
            my_initial_state = [self.initialize[0],
                                self.initialize[1]]
            qc.initialize(my_initial_state, 1)
# =============================================================================
#         elif self.input_mixedstate:
#             print("error")
#             #noch fertigmachen
# =============================================================================
# =============================================================================
#             mixedstate = np.zeros((32,32))
#             mixedstate[0][0] = self.input_mixedstate[0]*np.conjugate(self.input_mixedstate[0])
#             mixedstate[0][1] = self.input_mixedstate[0]*np.conjugate(self.input_mixedstate[1])
#             mixedstate[1][1] = self.input_mixedstate[1]*np.conjugate(self.input_mixedstate[1])
#             mixedstate[1][0] = self.input_mixedstate[1]*np.conjugate(self.input_mixedstate[0])
#             #rho = [[0.95+0.j, 0.0+0.0j],[0.0+0.0j,0.05+0.j]]
#             qc.set_density_matrix(mixedstate)
#         
# =============================================================================
        # create cat state using electron spin as mediator
        qc.cx(1,0)
        qc.cx(0,2)
        qc.cx(0,3)
        
        #qc.barrier()
        
        # project into code space and measure
        # measure first stabilizer on electron spin
        qc.cx(2,0)
        
        # state transfer to first ancilla
        qc.cx(0,4)
        
        # measure second stabilizer on electron spin
        qc.cx(2,0)
        qc.cx(3,0)
        
        # state transfer to second ancilla
        qc.cx(0,5)
        
        # correct state of electron spin
        qc.cx(5,0)
        
        # measure using electron spin destructively
        #qc.barrier()
        
        #qc.reset(0)
        
# =============================================================================
#         #optional: s-gate
#         qc.sdg([1,2,3])
#         
# =============================================================================
# =============================================================================
#         #optinal: transversal H-gate
#         qc.h([1,2,3])
# =============================================================================
        
# =============================================================================
#         # optional: logical X gate
#         qc.x([1,2,3])
# =============================================================================
        
# =============================================================================
#         # optional: logical H Gate
#         array=[[ 0.70710678+0.j,  0.        +0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.        +0.j,  0.70710678+0.j],
#                   [ 0.        +0.j, -0.70710678+0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.70710678+0.j,  0.        +0.j],
#                   [ 0.        +0.j,  0.        +0.j, -0.70710678+0.j,
#                     0.        +0.j,  0.        +0.j,  0.70710678+0.j,
#                     0.        +0.j,  0.        +0.j],
#                   [ 0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.70710678+0.j,  0.70710678+0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j],
#                   [ 0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.70710678+0.j, -0.70710678+0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j],
#                   [ 0.        +0.j,  0.        +0.j,  0.70710678+0.j,
#                     0.        +0.j,  0.        +0.j,  0.70710678+0.j,
#                     0.        +0.j,  0.        +0.j],
#                   [ 0.        +0.j,  0.70710678+0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.70710678+0.j,  0.        +0.j],
#                   [ 0.70710678+0.j,  0.        +0.j,  0.        +0.j,
#                     0.        +0.j,  0.        +0.j,  0.        +0.j,
#                     0.        +0.j, -0.70710678+0.j]]
#         logical_H = Operator(array)
#         qc.unitary(logical_H,[1,2,3],label='logicalH')
# =============================================================================
        
# =============================================================================
#         # optional: logical S-Gate
#         array = np.zeros((8,8), dtype=complex)
#         array[0,0] = 1.0
#         array[1,1] = -1.0j
# 
# =============================================================================
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
        
        #qc.barrier()
        
# =============================================================================
#         #### comment in line below when executing the transversal H gate
# 
#         #qc.h([1,2,3])
# =============================================================================
        
        
        # measure first stabilizer on electron spin
        qc.cx(1,0)
        qc.cx(2,0)
        
        # state transfer to third ancilla
        qc.cx(0,6)
        
        # measure second stabilizer on electron spin
        qc.cx(2,0)
        qc.cx(3,0)
        
        # state transfer to forth ancilla
        qc.cx(0,7)
        
# =============================================================================
#         #### comment in line below when executing the transversal H gate
#         #qc.h([1,2,3])
# =============================================================================
        
        # correct state of electron spin
        qc.cx(7,0)
        
        # measure using electron spin destructively
        
        qc.measure([4,5],c1)
        qc.measure([6,7],c2)
        
        return qc

    
    def bitflip_detection(self):
        q = QuantumRegister(5)
        c = ClassicalRegister(2)
        qc = QuantumCircuit(q,c)
        
        # not necessary for init state = ground state
        # create cat state
        qc.cx(q[0],q[1])
        qc.cx(q[0],q[2])
        #qc.barrier()
        
        # measure stabilizer
        qc.cx(0,3)
        qc.cx(1,3)
        
        qc.cx(1,4)
        qc.cx(2,4)
        
        qc.measure([3,4],[0,1])
    
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
    
        # measure stabilizer
        qc.cx(0,3)
        qc.cx(1,3)
        
        qc.cx(1,4)
        qc.cx(2,4)
        
        qc.measure([3,4],[0,1])
        
        return qc
    
    
class BitFlip_IBM:
            
    def __init__(self,pos_error,
                 input_statevector=False,
                 initialize=False,
                 input_mixedstate=False,
                 set_input_statevector=False
                 ):
        self.pos_error = pos_error
        self.input_statevector = input_statevector
        self.initialize = initialize
        self.input_mixedstate = input_mixedstate
        self.set_input_statevector = set_input_statevector
        self.qc = self.code() 
        

    
    def code(self):
        q = QuantumRegister(5,'q')
        c1 = ClassicalRegister(2,'c1')
        c2 = ClassicalRegister(2,'c2')
        qc = QuantumCircuit(q,c1,c2)
        
        # initialize some state
        if self.set_input_statevector:
            my_statevector = np.zeros(32,dtype=complex)
            my_statevector[0] = self.input_statevector[0]
            my_statevector[1] = self.input_statevector[1]
            qc.set_statevector(my_statevector)
        else:
            my_initial_state = [self.initialize[0],
                                self.initialize[1]]
            qc.initialize(my_initial_state, 0)
# =============================================================================
#         elif self.input_mixedstate:
#             mixedstate = np.zeros((32,32))
#             mixedstate[0][0] = self.input_mixedstate[0]*np.conjugate(self.input_mixedstate[0])
#             mixedstate[0][1] = self.input_mixedstate[0]*np.conjugate(self.input_mixedstate[1])
#             mixedstate[1][1] = self.input_mixedstate[1]*np.conjugate(self.input_mixedstate[1])
#             mixedstate[1][0] = self.input_mixedstate[1]*np.conjugate(self.input_mixedstate[0])
#             #rho = [[0.95+0.j, 0.0+0.0j],[0.0+0.0j,0.05+0.j]]
#             qc.set_density_matrix(mixedstate)
# =============================================================================
        
        # create cat state
        # swap operations depend on the chosen layout! (0,3,1,4,2)

        #qc.save_statevector(label='init_dmatrix')        
        qc.cx(0,1)
        qc.cx(1,2)
        
# =============================================================================
#         qc.barrier()
#         qc.swap(2,4)
#         qc.swap(0,3)
#         qc.barrier()
# =============================================================================
        
# Alternative version optimized for swap gates
        #qc.barrier()
        qc.cx(2,4)
        qc.cx(4,2)
        qc.cx(2,4)
        qc.cx(3,0)
        qc.cx(0,3)
        #qc.barrier()
        
        # 3,1,4 code, 0,2 ancilla
        
        # measure stabilizer
        
        #qc.cx(3,0)
        qc.cx(1,0)
        
        qc.cx(1,2)
        qc.cx(4,2)
        qc.measure([0,2],c1)
    
        #qc.barrier()
        # noisy evolution
        if self.pos_error==None:
            pass
        elif self.pos_error==0:
            qc.x(3)
        elif self.pos_error==1:
            qc.x(1)
        elif self.pos_error==2:
            qc.x(4)
        
        #qc.barrier()
        
        # measure stabilizer
        
        qc.cx(3,0)
        qc.cx(1,0)
        
        qc.cx(1,2)
        qc.cx(4,2)
        
        qc.measure([0,2],c2)
        
        return qc
# =============================================================================
#         qc.swap(q[0],q[3])
#         qc.cx(q[3],q[1])
#         qc.swap(q[2],q[4])
#         qc.cx(q[1],q[4])
# 
#         qc.swap(2,4)
#         qc.swap(0,3)
#         qc.barrier()
#         
#         # measure stabilizer
#         qc.cx(0,3)
#         qc.cx(1,3)
#         
#         qc.cx(1,4)
#         qc.cx(2,4)
#         
#         qc.measure([3,4],c1)
#     
#         # noisy evolution
#         if self.pos_error==None:
#             pass
#         else:
#             qc.x(int(self.pos_error))
#     
#         # measure stabilizer
#         qc.cx(0,3)
#         qc.cx(1,3)
#         
#         qc.cx(1,4)
#         qc.cx(2,4)
#         
#         qc.measure([3,4],c2)
# =============================================================================


class BitFlipToffoli:
    
    def __init__(self, pos_error):
        self.pos_error = pos_error
        self.qc = self.bitflip_code_unitary_correction_new_toffoli()
        
    
    # Bitflip Code mit unitärer Korrektur
    def bitflip_code_unitary_correction_new_toffoli_for_IBM(self):
        q = QuantumRegister(3)
        a = QuantumRegister(3)
        c1 = ClassicalRegister(3)
        c2 = ClassicalRegister(3)
        #c3 = ClassicalRegister(3)
        #c4 = ClassicalRegister(3)
        qc = QuantumCircuit(q,a,c1,c2)
    
        # create cat state
        qc.cx(q[0],q[1])
        qc.cx(q[0],q[2])
    
        # noisy evolution
        if self.pos_error==None:
            pass
        else:
            qc.x(int(self.pos_error))
    
        # measure stabilizer
        qc.cx(q[0],a[0])
        qc.cx(q[1],a[0])
        
        qc.cx(q[1],a[1])
        qc.cx(q[2],a[1])
        
        # parity check
        qc.cx(a[0],a[2])
        qc.cx(a[1],a[2])
        
        qc.measure(a,c1)
    
        # apply unitary correction using phase-ignorant toffoli-gate decomposition
        # first toffoli gate: control on a[0],a[2], target q[0]
        qc.ry(np.pi/4,q[0])
        qc.cx(a[0],q[0])
        qc.ry(np.pi/4,q[0])
        qc.cx(a[2],q[0])
        qc.ry(-np.pi/4,q[0])
        qc.cx(a[0],q[0])
        qc.ry(-np.pi/4,q[0])
        
        # second toffoli gate: control on a[1],a[2], target q[2]
        qc.ry(np.pi/4,q[2])
        qc.cx(a[1],q[2])
        qc.ry(np.pi/4,q[2])
        qc.cx(a[2],q[2])
        qc.ry(-np.pi/4,q[2])
        qc.cx(a[1],q[2])
        qc.ry(-np.pi/4,q[2])
        
        # third toffoli gate: control on a[0],a[2], target q[1]
        qc.ry(np.pi/4,q[1])
        qc.cx(a[0],q[1])
        qc.ry(np.pi/4,q[1])
        qc.cx(a[2],q[1])
        qc.ry(-np.pi/4,q[1])
        qc.cx(a[0],q[1])
        qc.ry(-np.pi/4,q[1])
    
        #qc.measure(q,c3)
        qc.measure(q,c2)
        
        return qc
    
        
class IBM_untranspiled_bitflip:
    
    def __init__(self,pos_error):
        self.pos_error = pos_error
        
        
    def circuit(self):
        q = QuantumRegister(5)
        c1 = ClassicalRegister(2)
        c2 = ClassicalRegister(2)
        qc = QuantumCircuit(q,c1,c2)
        
        qc.cx(0,1)
        qc.cx(1,2)
    
        qc.cx(2,4)
        qc.cx(4,2)
        qc.cx(2,4)
        qc.cx(3,0)
        qc.cx(0,3)
        #qc.cx(3,0)
        #qc.barrier()
    
        # 3,1,4 code, 0,2 ancilla
    
        # measure stabilizer
    
        #qc.cx(3,0)
        qc.cx(1,0)
    
        qc.cx(1,2)
        qc.cx(4,2)
        qc.measure([0,2],c1)
    
        #qc.barrier()
        # noisy evolution
        if self.pos_error==None:
            pass
        elif self.pos_error==0:
            qc.x(3)
        elif self.pos_error==1:
            qc.x(1)
        elif self.pos_error==2:
            qc.x(4)
    
        #qc.barrier()
    
        # measure stabilizer
    
        qc.cx(3,0)
        qc.cx(1,0)
    
        qc.cx(1,2)
        qc.cx(4,2)
    
        qc.measure([0,2],c2)
    
        return qc
        
        
        
        