# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 11:52:03 2022

@author: regina
"""


from qiskit.providers.aer import AerSimulator, StatevectorSimulator
from qiskit import transpile, QuantumCircuit,\
    QuantumRegister, ClassicalRegister, BasicAer
from qiskit.visualization import plot_histogram, plot_state_hinton
import numpy as np
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.quantum_info import process_fidelity



if __name__ == "__main__":
       
    shots = 200
    n_qubits = 1
    q = QuantumRegister(n_qubits)
    c = ClassicalRegister(n_qubits)
    qc = QuantumCircuit(q,c)
    
    qc.rz(np.pi*-0.5,0)
    qc.y(0)
    qc.rz(np.pi*0.5,0)
    #qc.ry(np.pi*1.0,0)
    print(Operator(qc))
    
# =============================================================================
#     qc.x([1,2])
#     
#     arr = np.identity(16)
#     arr[7,7] = -1.0
#     arr[15,15] = -1.0
#     
#     c3rx = Operator(arr)
#     qc.append(c3rx,[3,2,1,0])
#     qc.measure(q,c)
#     
#     backend = StatevectorSimulator()
#     job = backend.run(qc)
#     result = job.result()
#     outputstate = result.get_statevector(qc, decimals=3)
#     print(outputstate)
#     
#     display(plot_state_hinton(outputstate))
# =============================================================================

    
# =============================================================================
#     circ = QuantumCircuit(1)
#     circ.h(0)
#     
#     # Compute process fidelity
#     F = process_fidelity(op, Operator(circ))
#     print('Process fidelity =', F)
# =============================================================================
    

   #hier ende ich mit einer globalen phase von exp(-0.125*i*pi)

    #qc.h(2)
    #qc.cz(0,1)
    #qc.h(2)
    
    #qc.h(1)
    #qc.measure([1],[0])
    #display(qc.draw('mpl'))
    
    #print(Operator(qc))
    #print(Operator(circ))
    
# =============================================================================
#     basis_gates_IBM = ['cx','id','rz','sx','x']
# 
#     
#     tqc = transpile(qc, backend, basis_gates=basis_gates)
#     display(tqc.draw('mpl'))
#     #print(Operator(tqc))
#     backend = BasicAer.get_backend('unitary_simulator')
#     job = backend.run(tqc)
#     res_unitary = job.result().get_unitary(qc, decimals=2)
#     print(res_unitary)
#     #print(Operator(res_unitary)==Operator(tqc))
# =============================================================================


    
    basis_gates = ['cx','id','rx','ry']
    simulator = AerSimulator()
    tqc = transpile(qc, backend=simulator, basis_gates=None, \
                    optimization_level=3, coupling_map=None, \
                        initial_layout=None)

    display(tqc.draw('mpl'))
        
    result = simulator.run(tqc,shots=shots,memory=True).result()
    print(result.get_counts())
    display(plot_histogram(result.get_counts()))

# =============================================================================
#     qc.cx(1,2)
#     qc.rz(-np.pi*0.25,2)
#     qc.cx(0,2)
#     qc.rz(np.pi*0.25,2)
#     qc.cx(1,2)
#     qc.rz(-np.pi*0.25,2)
#     qc.rz(np.pi*0.25,1)
#     qc.cx(0,2)
#     qc.rz(np.pi*0.25,2)
#     qc.cx(0,1)
#     qc.rz(np.pi*0.25,0)
#     qc.rz(-np.pi*0.25,1)
#     qc.cx(0,1)
# =============================================================================
    