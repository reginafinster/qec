# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 15:33:25 2022

@author: regina
"""

from qiskit.providers.aer.noise import *
from qiskit.quantum_info import *

class SimpleNoiseModel:
    
    def __init__(self, n_qubits, p_dephasing=0.0, bool_thermal_error=False):
        self.p_dephasing = p_dephasing
        self.bool_thermal_error = bool_thermal_error
        self.n_qubits = n_qubits
            
    def build_model(self):
        '''
        Builds a simple noise model for the NV center geometry
        with identical dephasing and/or relaxation errors on all gates.
        @params:
            n_qubits: number of qubits
            p_dephasing: error probability for the phase flip channel
            bool_thermal_error: if True, relaxation errors including amplitude
                                and phase damping are added from t1,t2 params 
                                of the model

        Returns
        -------
        my_noise_model : simple noise model
        '''
        my_noise_model = NoiseModel()
      
        if (self.bool_thermal_error and self.p_dephasing==0):
            single_thermal_error = thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.singlegatetime)
            print('adding single qubit relaxation error with average gate fidelity: ',\
                  average_gate_fidelity(single_thermal_error))
            for i in range(self.n_qubits):
                my_noise_model.add_quantum_error(single_thermal_error,self.single_qubit_gates,[i])
            single_thermal_error = thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.doublegatetime)
            double_thermal_error = single_thermal_error.tensor(single_thermal_error)
            print('adding relaxation error on CNOT with average gate fidelity: ',\
                  average_gate_fidelity(double_thermal_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_thermal_error,['cx'],pair)
                
        elif (self.p_dephasing>0 and not self.bool_thermal_error):
            single_phase_error = pauli_error([('Z', p_error), ('I', 1 - p_error)])
            single_depol_error = depolarizing_error(self.p_dephasing,1)
            print('adding single qubit dephasing error with average gate fidelity: ',\
                  average_gate_fidelity(single_depol_error))
            for i in range(self.n_qubits):
                my_noise_model.add_quantum_error(single_depol_error,self.single_qubit_gates,[i])
            double_phase_error = single_phase_error.tensor(single_phase_error)
            print('adding dephasing error on CNOT with average gate fidelity: ',\
                  average_gate_fidelity(double_depol_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_depol_error,['cx'],pair)
                
        elif (self.bool_thermal_error and self.p_dephasing>0):
            phase_flip = pauli_error([('Z', p_error), ('I', 1 - p_error)])
            single_phase_error = depolarizing_error(self.p_dephasing,1)
            single_thermal_error = thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.singlegatetime)
            single_total_error = single_depol_error.compose(single_thermal_error)
            print('adding single qubit relaxation and dephasing error with average gate infidelity: ',\
                  average_gate_fidelity(single_total_error))
            for i in range(self.n_qubits):
                my_noise_model.add_quantum_error(single_total_error,self.single_qubit_gates,[i])
                
            single_thermal_error = thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.doublegatetime)
            double_thermal_error = single_thermal_error.tensor(single_thermal_error)
            double_phase_error = single_phase_error.tensor(single_phase_error)
            double_total_error = double_phase_error.compose(double_thermal_error)
            print('adding relaxation error on CNOT with average gate infidelity: ',\
                  average_gate_fidelity(double_depol_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_total_error,['cx'],pair)
        
        return my_noise_model
   
class SimpleNoiseModel_NVCenter(SimpleNoiseModel):
    
    def __init__(self, n_qubits, p_dephasing=0.0, bool_thermal_error=0.0):
        super().__init__(n_qubits, p_dephasing, bool_thermal_error)
        self.basis_gates = ['x','y','rx','ry','id','cx','measure','reset']
        self.single_qubit_gates = ['x','y','rx','ry','id']
        self.two_qubit_gates = ['cx']
        self.coupling_map = [ [i+1,0] for i in range(n_qubits-1)] + [ [0,i+1] for i in range(n_qubits-1)]
        self.properties = {'t1':0.125,'t2':0.009, 'gatetime':{'sg':0.00000005,'cx':0.0000005}}
        if (self.t==0.0):
            self.t2 = self.properties.get('t2')
            self.t1 = self.properties.get('t1')
        else:
            self.t2 = self.t
            self.t1 = self.t
            print('Using t1,t2=',self.t)
        self.singlegatetime = self.properties['gatetime'].get('sg')
        self.doublegatetime = self.properties['gatetime'].get('cx')