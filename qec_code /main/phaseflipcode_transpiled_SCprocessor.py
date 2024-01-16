# -*- coding: utf-8 -*-
"""
Created on Sun May 29 08:04:08 2022

@author: regin
"""
from qiskit import transpile, QuantumCircuit,\
    QuantumRegister, ClassicalRegister, IBMQ
from qiskit.visualization import plot_histogram
from qiskit.providers.aer.noise import NoiseModel
from qiskit.quantum_info import Pauli, Operator, state_fidelity
import numpy as np
from qiskit.visualization import plot_bloch_multivector, array_to_latex
import sys
import os
from qiskit.providers.aer import AerSimulator

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
#sys.path.append('C:/Users/regin/Nextcloud/Postdoc/Code/modules')
import my_noise_models
import codes

#IBMQ.disable_account()
#BMQ.enable_account('807285e4f347ace42ec1d9020bd10ba9b708ec43e6394de8efb6ac412427e1a7ac87c1ab91bc7a7ca2ca67f02c708d371243234a58021d4017a7e6e223ac30a3', 'https://auth.de.quantum-computing.ibm.com/api')

# =============================================================================
# class TranspiledPhaseFlip_SCProcessor:
#     
#     def __init__(self,pos_error): 
#         self.pos_error = pos_error
#     
#     def circuit(self):
#         #define initial layout
#         # initial layout (3,2,4,1,0) also heißen die qubits (4,3,1,0,2)
#         q0=4
#         q1=3
#         q2=1
#         q3=0
#         q4=2
#         
#         q = QuantumRegister(5)
#         c = ClassicalRegister(2)
#         qc = QuantumCircuit(q,c)
#         
# # =============================================================================
# #         qc.cx(q3,q1)
# # =============================================================================
#         
#         qc.save_statevector(label='init_statevector')
# 
#         qc.cx(q3,q2)
# 
#         qc.cx(q1,q2)
#         qc.cx(q2,q1)
#         qc.cx(q1,q2)
#         
#         qc.rz(np.pi/2,q3)
#         qc.sx(q3)
#         qc.rz(np.pi/2,q3)
#         
#         qc.cx(q1,q4)
#         
#         qc.rz(np.pi/2,q1)
#         qc.sx(q1)
#         qc.rz(np.pi/2,q1)
#         
#         qc.rz(np.pi/2,q4)
#         qc.sx(q4)
#         qc.rz(np.pi/2,q4)
#         
#         
#         #qc.save_density_matrix([q3,q1,q4],label='init_dmatrix')
#         
#         qc.barrier()
#         
#         # noisy evolution
#         if self.pos_error==None:
#             pass
#         elif self.pos_error==0:
#             qc.z(q3)
#         elif self.pos_error==1:
#             qc.z(q1)
#         elif self.pos_error==2:
#             qc.z(q4)
#         
#         qc.barrier()
#         
#         qc.rz(np.pi/2,q1)
#         qc.sx(q1)
#         qc.rz(np.pi/2,q1)
#         
#         qc.rz(np.pi/2,q3)
#         qc.sx(q3)
#         qc.rz(np.pi/2,q3)
#         
#         qc.rz(np.pi/2,q4)
#         qc.sx(q4)
#         qc.rz(np.pi/2,q4)
#         
#         qc.cx(q3,q2)
#         
#         qc.rz(np.pi/2,q3)
#         qc.sx(q3)
#         qc.rz(np.pi/2,q3)
#         
#         qc.cx(q1,q2)
#         qc.cx(q0,q1)
#         qc.cx(q1,q0)
#         qc.cx(q4,q1)
#         
#         qc.rz(np.pi/2,q0)
#         qc.sx(q0)
#         qc.rz(np.pi/2,q0)
#         
#         qc.rz(np.pi/4,q1)
#         qc.cx(q2,q1)
#         qc.rz(-np.pi/4,q1)
#         
#         qc.cx(q0,q1)
#         
#         qc.rz(np.pi/2,q4)
#         qc.sx(q4)
#         qc.rz(np.pi/2,q4)
#         
#         qc.rz(np.pi/4,q1)
#         qc.cx(q2,q1)
#         qc.rz(-np.pi/4,q1)
#         qc.cx(q0,q1)
#         qc.cx(q1,q2)
#         qc.cx(q2,q1)
#         qc.cx(q1,q2)
#         
#         qc.rz(np.pi/4,q1)
#         
#         qc.x(q2)
#         qc.rz(np.pi/4,q2)
#         qc.cx(q0,q1)
#         qc.rz(-np.pi/4,q1)
#         qc.cx(q0,q1)
#         qc.rz(np.pi/4,q0)
#         qc.cx(q1,q2)
#         
#         qc.rz(-np.pi/4,q2)
#         qc.cx(q3,q2)
#         qc.rz(np.pi/4,q2)
#         qc.cx(q1,q2)
#         qc.rz(-np.pi/4,q2)
#         qc.cx(q3,q2)
#         qc.cx(q1,q2)
#         qc.cx(q2,q1)
#         qc.cx(q1,q2)
#         qc.x(q1)
#         
#         qc.rz(np.pi/4,q2)
#         qc.rz(np.pi/4,q1)
#         qc.cx(q3,q2)
#         qc.rz(-np.pi/4,q2)
#         qc.cx(q3,q2)
#         
#         qc.x(q2)
#         qc.rz(np.pi/4,q3)
#         qc.cx(q2,q1)
#         qc.rz(-np.pi/4,q1)
#         qc.cx(q4,q1)
#         qc.rz(np.pi/4,q1)
#         qc.cx(q2,q1)
#         
#         qc.rz(-np.pi/4,q1)
#         qc.rz(np.pi/4,q2)
#         
#         qc.cx(q1,q4)
#         qc.cx(q4,q1)
#         
#         qc.cx(q1,q2)
#         qc.rz(-np.pi/4,q2)
#         qc.cx(q1,q2)
#         qc.rz(np.pi/4,q1)
#         qc.x(q2)
#         
#         #qc.measure([q2,q4],c)
#         #qc.save_density_matrix([q3,q0,q1],label='result_dmatrix')
#         #qc.save_statevector(label='result_statevector')
# 
#         return qc
# =============================================================================
        

if __name__ == "__main__":
    #qc = PhaseFlipUnitaryCorrection_without_transpilation_SC(pos_error=2).circuit()
    qc = codes.TranspiledPhaseFlip_SCProcessor(pos_error=2,input_statevector=[np.sqrt(0.5),np.sqrt(0.5)],use_input_statevector=True).circuit()
    simulator = AerSimulator()
    hex_coupling_map_1 = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2],[1,4],[4,1]]
    tqc = transpile(qc,coupling_map = hex_coupling_map_1, initial_layout=(3,2,4,1,0))
    display(tqc.draw('mpl'))
    result = simulator.run(qc,shots=1,memory=True).result()
    statevector = result.data()['init_statevector']
    print(statevector)
    #print(tqc.count_ops()['cx'])
    
    init_dmatrix = result.data()['init_dmatrix']
    final_dmatrix = result.data()['result_dmatrix']
    fid = state_fidelity(init_dmatrix, final_dmatrix)
    print(fid)
    
# =============================================================================
#     
#     print(init_dmatrix)
#     display(plot_bloch_multivector(init_dmatrix))
#     print(final_dmatrix)
#     display(plot_bloch_multivector(final_dmatrix))
# =============================================================================


    #unitary = simulator.run(qc).result().get_unitary()
    #array_to_latex(unitary, prefix="\\text{Circuit = }\n")
    
    
    
    
    
    