# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 11:07:18 2022

@author: regina
"""

from qiskit.providers.aer import AerSimulator
from qiskit import transpile, QuantumCircuit,\
    QuantumRegister, ClassicalRegister, IBMQ
from qiskit.visualization import plot_histogram
from qiskit.providers.aer.noise import NoiseModel
from qiskit.quantum_info import Pauli, Operator
import numpy as np


q = QuantumRegister(3,"q")
c = ClassicalRegister(3, "c")
qc = QuantumCircuit(q,c)

qc.x(0)
qc.cx(0,1)
qc.cx(1,2)

display(qc.draw('mpl',style='bw', initial_state=True))




