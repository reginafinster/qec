# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 10:44:49 2021

@author: regina
"""
from qiskit.providers.aer.noise import *
from qiskit.quantum_info import *
import logging
import copy
import pickle
import sys

#sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'\modules')
sys.path.append('C:/Users/regin/anaconda3/Lib/site-packages/qiskit/providers/aer/noise/errors')
import m_standard_errors as mse


class NoiseModel_NVCenter:
    
    def __init__(self, n_qubits, p_depol=0.0, t=0, fill_up_gate_error=True, change_coherence_times=False):
        """
        This class builds the noise model for a NV center.
        Times are in units of seconds.
        Frequencies are in units of kHz.
        @params: 'epsbg' is the error per single basis gate.
        'fill_up_gate_error': bool; if true, gate errors are filled up with depolarizing errors
        'p_depol': if 'fill_up_gate_error' is false, all gates get a uniform depolarizing error 
        with error probability p_depol
        'eptbg' is the error per two simultaneously executed basis gates.
        'epcx' is the error of the entangling gate cnot.
        'gatetimes' for cx are given for the control qubit (as they depend on its direction)
        'coupling map': spin 5 is central electron spin, 
                        qubit 0 is 14N, qubit 1 13C1, qubit 2 13C2, qubit 3 and 4 are two additional carbon spins
        reset error for electron was taken from nuclear spins due to the lack of data for it
        ACHTUNG: reset error ist 0.01 für electron spin, aber hier wg. circuitlogik auf 0 gesetzt
        da der gesamte Fehler beim messfehler drinsteht.
        'Coupling Map':
        physical layout: [e,14N,13C_1,13C_2,13C_3,13C_4]
        die Reihenfolge ordnet den Codequbits 0,1,2,... 
        (also so wie im Code bezeichnet) ihre Position
        in der Coupling Map zu!
        layout positions in code: [codequbit 0, codequbit 1, codequbit 2, ancilla 1, ancilla 2, electron spin]
        """
        self.p_depol = p_depol
        self.t = t
        self.change_coherence_times = change_coherence_times
        self.fill_up_gate_error = fill_up_gate_error
        self.n_qubits = n_qubits
        self.basis_gates = ['x','y','rx','ry','id','cx','measure','reset', 'z', 'rz']
        self.coupling_map = [ [i+1,0] for i in range(n_qubits-1)] + [ [0,i+1] for i in range(n_qubits-1)]
        self.single_qubit_gates = ['x','y','rx','ry']
        self.two_qubit_gates = ['cx']
        self.qubit_list = self.make_qubit_list()
        self.gate_fidelities= {}
        self.properties = [
                        {'qubit':0, 'type':'electron', \
                        't1':0.0057, 't2hahn':0.0005,\
                        't2star':0.00003,\
                        'freq':0.0, 'gatetimes':{'cxN':0.00015,'cxC':0.000015,\
                                                'x':0.0, 'rx':0.5*0.0,\
                                                'y':0.0, 'ry':0.5*0.0},\
                        'temperature':293, 'rabi':0, 'error_readout':0.0, 'error_reset':0.0,\
                        'epsbg':0.0, 'eptbg':0.0, 'epcx':0.02503},
                        {'qubit':1, 'type':'14N', 't1':0.125, \
                        't2hahn':0.00857,'t2star':0.00857, \
                        'freq':-4828.5, 'gatetimes':{'x':0.00007751937, 'rx':0.5*0.00007751937,\
                                                     'y':0.00007751937, 'ry':0.5*0.00007751937,\
                                                         'cx':0.0000026}, \
                        'temperature':293, 'rabi':6.45,\
                        'error_readout':0.042, 'error_reset':0.01,\
                        'epsbg':0.0058, 'eptbg':0.0091, 'epcx':0.02503},
                        {'qubit':2, 'type':'13C1', \
                        't1':0.5, 't2hahn':0.00857,\
                        't2star':0.00857,'freq':-7216.5,\
                        'gatetimes':{'x':0.000028248587, 'rx':0.5*0.000028248587,\
                                    'y':0.000028248587, 'ry':0.5*0.000028248587, 'cx':0.000005},\
                        'temperature':293, 'rabi':35.40, 'error_readout':0.031, 'error_reset':0.01,\
                        'epsbg':0.0445, 'eptbg':0.0091, 'epcx':0.02503},
                        {'qubit':3, 'type':'13C2', \
                        't1':25.0, 't2hahn':0.00857,\
                        't2star':0.00857,\
                        'freq':-7540.5, 'gatetimes':{'x':0.0000137287, 'rx':0.5*0.0000137287,\
                                                     'y':0.0000137287, 'ry':0.5*0.0000137287,\
                                                         'cx':0.00001},\
                        'temperature':293, 'rabi':36.42, 'error_readout':0.004, 'error_reset':0.01,\
                        'epsbg':0.026, 'eptbg':0.0091, 'epcx':0.02503}
                        ]
    
    def make_qubit_list(self):
        '''
        Das hier legt eine Liste an, die beliebig häufig auf die Eigenschaften 
        der beiden Kohlenstoff-Nuklearspins zugreift. 
        Achtung, der Fehler muss dann trotzdem der richtigen Position zugewiesen werden.

        Returns
        -------
        qubit_list : TYPE
            DESCRIPTION.

        '''
        qubit_list = [0,1,2,3]
        while len(qubit_list)<self.n_qubits:
            qubit_list.extend([2,3])
        return qubit_list
    
    def build_model(self):
        '''
        This function builds a noise model for a spin qubit NV-center
        from calibrated data. 
        Loops over qubits and assigns specific parameters.
        @params:

        Returns
        -------
        my_noise_model : device-specific noise model based on input params

        '''
        my_noise_model = NoiseModel()
        my_noise_model.add_basis_gates(['unitary'])
        
        print("set up single qubit errors\n")
        for j, i in enumerate(self.qubit_list):
            self.gate_fidelities.update({str(j):{}})
            prop_dict = self.properties[i]
            t2 = prop_dict.get('t2hahn')
            t1 = prop_dict.get('t1')
            if self.change_coherence_times:
                t2 = self.t2
                t1 = t1+self.t
                print(t1)
            print("qubit", prop_dict.get('type'))
            for gate in self.single_qubit_gates:
                gateerror = prop_dict['epsbg']
                #print("gate: ", gate, "gateerror: ", gateerror)
                gatetime = prop_dict['gatetimes'][str(gate)]
                print(t1,t2,gatetime)
                thermal_error = mse.thermal_relaxation_error(t1=t1, t2=t2, time=gatetime)
                fid_therm = average_gate_fidelity(thermal_error)
                print("thermal error: ", (1-fid_therm))
                if(self.fill_up_gate_error==True):
                    fidelity_diff = fid_therm-(1-gateerror)
                    p_depol = 2*fidelity_diff
                    if (p_depol<=0.0):
                        p_depol=0
                        print(("for qubit {} and gate {} thermal error {} larger than gate error {}. \n")\
                              .format(i,gate, (1-fid_therm),gateerror))
                    single_depol_error = depolarizing_error(p_depol,1)
                    fid_depol = average_gate_fidelity(single_depol_error)
                    #print("filled up depol error: ", (1-fid_depol))
                else:
                    single_depol_error = depolarizing_error(self.p_depol,1)
                    fid_depol = average_gate_fidelity(single_depol_error)
                # compose operators, depolarizing error first, followed by thermal relaxation
                total_error = single_depol_error.compose(thermal_error)
                # check if gate fidelity of the model is equal to the measured gate fidelity 
                gate_fidelity = average_gate_fidelity(total_error)
                self.gate_fidelities[str(j)].update({gate: gate_fidelity})
                diff_gateerror = (gateerror-(1-gate_fidelity))
                #if abs(diff_gateerror)>=0.000001:
                    #print(('total gate infidelity: {}').format(1-gate_fidelity))
                    #print("difference of calculated and calibrated gate error: ", diff_gateerror, "\n")
    
                # add error on ith qubit to error model
                my_noise_model.add_quantum_error(total_error,[gate],[j])
                
            # add readout error
            p10 = prop_dict.get('error_readout')
            p01 = prop_dict.get('error_readout')
            prob_list = [[1-p10,p10],[p01,1-p01]]
            ro_error = ReadoutError(prob_list,i)
            my_noise_model.add_readout_error(ro_error,[j])
            self.gate_fidelities[str(j)].update({'ro_error': 1-((p10+p01)*0.5)})
            
            # add reset error
            p_reseterror = prop_dict.get('error_reset')
            reset_error = pauli_error([('X', p_reseterror), ('I', 1-p_reseterror)])
            #my_noise_model.add_quantum_error(reset_error,['measure'],[j])
            
        #my_noise_model.add_all_qubit_quantum_error(triple_total_error,'logicalH')
        # build two-qubit errors:Two-qubit gate errors consisting of a two-qubit depolarizing
        # error followed by single-qubit thermal relaxation errors on both qubits in the gate.
        print("set up cnot errors\n")
        gate = 'cx' 
        for orig_pair in self.coupling_map:
            self.gate_fidelities.update({str(orig_pair):{}})
            pair = copy.deepcopy(orig_pair)
            for k in [0,1]:
                while pair[k]>3:
                    pair[k]-=2
            prop_dict0 = self.properties[pair[0]]
            prop_dict1 = self.properties[pair[1]]
            t2_0 = prop_dict0.get('t2hahn')
            t1_0 = prop_dict0.get('t1')
            t2_1 = prop_dict1.get('t2hahn')
            t1_1 = prop_dict1.get('t1')
            if self.change_coherence_times:
                #t2 = self.t2
                t1_0 = t1_0 + self.t
                t1_1 = t1_1 + self.t
            
            # error for cnot - native only for electron-nuclear spin-coupling!
            gateerror = prop_dict1.get('epcx')
            #print(("cx_error for pair {} is {}").format(pair, gateerror))
            
            # gatetimes for controlled gates depend on the qubits and direction 
            if pair[0] != 0:
                gatetime = prop_dict0['gatetimes'].get('cx')
            elif pair[0] == 0:
                if pair[1] == 1:
                    gatetime = prop_dict0['gatetimes'].get('cxN')
                elif pair[1] != 1:
                    gatetime = prop_dict0['gatetimes'].get('cxC')
            
            print(t1_0, t2_0,gatetime)
            print(t1_1, t2_1, gatetime)
            print(gatetime)
            thermal_error_0 = mse.thermal_relaxation_error(t1=t1_0, t2=t2_0, time=gatetime)
            thermal_error_1 = mse.thermal_relaxation_error(t1=t1_1, t2=t2_1, time=gatetime)
    
            # so hat qubit 0 den thermal error 0.
            # Aber ist das auch das erste des Paars, wenn ich dann das paar mit dem two-qubit-quantum error belege?
            thermal_error = thermal_error_0.tensor(thermal_error_1)
    
            fid_therm = average_gate_fidelity(thermal_error)
            print(("thermal error {}").format(1.0-fid_therm))
            print("thermal fidelity ", fid_therm)
            print("gatetime", gatetime)
            error_diff = gateerror - 1+fid_therm
            #print(("difference of calculated and calibrated gate error {}").format(error_diff))
    
            
            if(self.fill_up_gate_error==True):
                # Formel für Fehler nur auf erstem Qubit:
                #p_depol = (5.0/3.0)*error_diff
        
                # Formel für depol-Fehler auf beiden Qubits:
                p_depol = (4.0/3.0)*error_diff
        
                if (p_depol<=0.0):
                    p_depol=0
                    print(("for qubit {} and gate {} thermal error {} larger than gate error {}.")\
                          .format(i,gate, (1-fid_therm),gateerror))
                elif (p_depol>=1.0666666666666667):
                    print(("for qubit {} and gate {} depolarizing error {} not big enough. Difference is {}. ")\
                          .format(i,gate, p_depol, (p_depol-1.0666666666666667)))
                    p_depol=1.0666666666666667
                # das hier ist die Variante, bei der der depol-Fehler im 4-dim Raum beider Qubits stattfindet
                #print(("depolarizing error {} \n").format(p_depol))
                double_depol_error = depolarizing_error(p_depol,2)
            else:
                double_depol_error = depolarizing_error(self.p_depol,2)
            
            # hier ist der Fehler nur auf dem Kontrollqubit
            #single_depol_error = depolarizing_error(p_depol,1)
            #no_error = pauli_error([('I', 1.0)])
            #double_depol_error = no_error.tensor(single_depol_error)
    
            fid_depol = average_gate_fidelity(double_depol_error)
    
            total_error = double_depol_error.compose(thermal_error)
    
            # check if gate fidelity of the model is equal to the measured gate fidelity 
            gate_fidelity = average_gate_fidelity(total_error)
            print(gate_fidelity)
            
            self.gate_fidelities[str(orig_pair)].update({gate: gate_fidelity})
            
            #print("Total gate infidelity is: ", 1-gate_fidelity)
            diff_gateerror = (gateerror-(1-gate_fidelity))
            if abs(diff_gateerror)>=0.00000001:
                print("difference of calculated and calibrated gate error: ", diff_gateerror, "\n")
    
            my_noise_model.add_quantum_error(total_error,[gate],orig_pair)

            
        return my_noise_model


class NoiseModel_IBM:
    
    def __init__(self, path_to_binary, change_coherence_times=False, t=0,\
                 fill_up_gate_error=True, check_model=False, p_depol=0):
        self.path_to_binary = path_to_binary
        with open(self.path_to_binary, "br") as f:
              noise_data = pickle.load(f)
              self.noise_model = noise_data[0]
              self.configuration = noise_data[1]
              self.properties = noise_data[2]
        self.coupling_map = self.configuration.coupling_map
        self.basis_gates = self.noise_model.basis_gates
        self.check_model = check_model
        self.change_coherence_times = change_coherence_times
        self.t = t
        self.p_depol = p_depol
        self.fill_up_gate_error = fill_up_gate_error
        self.gate_fidelities= {}

    
    def build_model(self):
        '''
        This function builds the noise model for an IBM chip
        from calibrated data
        Returns
        -------
        my_noise_model : device-specific noise model based on input params

        '''
        single_qubit_gates = ['id', 'sx', 'x']
        two_qubit_gates = ['cx']
        measure_reset = ['reset', 'measure']
        # instantiate model
        my_noise_model = NoiseModel()
        # Build single qubit errors: ich nehme vorläufig die fertigen, dann gleiche ich daran ab. 
        for i in range(self.configuration.n_qubits):
            self.gate_fidelities.update({str(i):{}})
            t2 = self.properties.t2(i)
            t1 = self.properties.t1(i)
            # die Idee ist, hier etwas zu addieren, dh. ich muss die Zeiten schon zuvor einlesen.
            # achtung aber ich muss t2 dann auch entsprechend verändern,
            # damit t2=2t1 als obere Grenze nicht verletzt wird.
            if self.change_coherence_times:
                t1 += self.t
            if (t2 >= 2*t1):
                logging.info("t2 of qubit ",i," is too large:", t2)
                t2 = 2*t1
                logging.info("Truncated to :", t2, "\n")
            for gate in single_qubit_gates:
                # get calibrated gate properties from backend
                gateerror = self.properties.gate_error(gate,i)
                ###################print("gateerror: ", gateerror)
                gatetime = self.properties.gate_length(gate,i)
                # set up appropriate thermal error
                thermal_error = mse.thermal_relaxation_error(t1=t1, t2=t2, time=gatetime)
                # calc fidelity and difference to total gate error
                
                if self.fill_up_gate_error==True:
                    fid_therm = average_gate_fidelity(thermal_error)
                    fidelity_diff = fid_therm-(1-gateerror)
                    p_depol = 2*fidelity_diff
                    if (p_depol<=0.0):
                        p_depol=0
                        logging.info(("for qubit {} and gate {} thermal error {} larger than gate error {}. \n")\
                              .format(i,gate, (1-fid_therm),gateerror))
                    single_depol_error = depolarizing_error(p_depol,1)
                    fid_depol = average_gate_fidelity(single_depol_error)
                else:
                    single_depol_error = depolarizing_error(self.p_depol,1)
                    fid_depol = average_gate_fidelity(single_depol_error)
                total_error = single_depol_error.compose(thermal_error)
                
                #default_data.update({'item3': 3})
                gate_fidelity = average_gate_fidelity(total_error)
                self.gate_fidelities[str(i)].update({gate: gate_fidelity})
                if self.check_model:
                    # check if gate fidelity of the model is equal to the measured gate fidelity 
                    diff_gateerror = (gateerror-(1-gate_fidelity))
                    if abs(diff_gateerror)>=0.000001:
                        logging.info("difference of calculated and calibrated gate error: ", diff_gateerror, "\n")
    
                # add error on ith qubit to error model
                my_noise_model.add_quantum_error(total_error,[gate],[i])
    
                # compare with build-in model:
                if self.check_model:
                    compareerror = Kraus((noise_model.__dict__)['_local_quantum_errors'][gate][str(i)])
                    if (1-process_fidelity(Kraus(total_error),compareerror))>=0.00000001:
                        logging.info("operator deviation for qubit nr and gate ", i, gate, "\n")
                        logging.info(process_fidelity(Kraus(total_error),compareerror))
    
        # build two-qubit errors:Two-qubit gate errors consisting of a two-qubit depolarizing
        # error followed by single-qubit thermal relaxation errors on both qubits in the gate.
        for pair in self.coupling_map:
            self.gate_fidelities.update({str(pair):{}})
            t2_0 = self.properties.t2(pair[0])
            t1_0 = self.properties.t1(pair[0])
            if self.change_coherence_times:
                t1_0 += self.t
            if (t2_0 >= 2*t1_0):
                print("t2 of qubit ", pair[0]," is too large:", t2_0)
                t2_0 = 2*t1_0
                logging.info("Truncated to :", t2_0)
            t2_1 = self.properties.t2(pair[1])
            t1_1 = self.properties.t1(pair[1])
            if self.change_coherence_times:
                t1_1 += self.t
            if (t2_1 >= 2*t1_1):
                print("t2 of qubit ",pair[1]," is too large:", t2_1)
                t2_1 = 2*t1_1
                logging.info("Truncated to :", t2_1)
            for gate in two_qubit_gates:
                gateerror = self.properties.gate_error(gate,pair)
                ###################print(("gateerror {}").format(gateerror))
                gatetime = self.properties.gate_length(gate,pair)
                thermal_error_0 = mse.thermal_relaxation_error(t1=t1_0, t2=t2_0, time=gatetime)
                thermal_error_1 = mse.thermal_relaxation_error(t1=t1_1, t2=t2_1, time=gatetime)
               
                # so hat qubit 0 den thermal error 0.
                # Aber ist das auch das erste des Paars, wenn ich dann das paar mit dem two-qubit-quantum error belege?
                thermal_error = thermal_error_0.tensor(thermal_error_1)
    
                 
                if self.fill_up_gate_error==True:
        
                    fid_therm = average_gate_fidelity(thermal_error)
                    error_diff = gateerror - 1+fid_therm
        
                    # Formel für Fehler nur auf erstem Qubit:
                    #p_depol = (5.0/3.0)*error_diff
        
                    # Formel für depol-Fehler auf beiden Qubits:
                    p_depol = (4.0/3.0)*error_diff
        
                    if (p_depol<=0.0):
                        p_depol=0
                        logging.info(("for qubit {} and gate {} thermal error {} larger than gate error {}. \n")\
                              .format(i,gate, (1-fid_therm),gateerror))
                    elif (p_depol>=1.0666666666666667):
                        logging.info(("for qubit {} and gate {} depolarizing error {} not big enough. Difference is {}. \n")\
                              .format(i,gate, p_depol, (p_depol-1.0666666666666667)))
                        p_depol=1.0666666666666667
                    # das hier ist die Variante, bei der der depol-Fehler im 4-dim Raum beider Qubits stattfindet
                    #####################print(("p_depol {} \n").format(p_depol))
                    double_depol_error = depolarizing_error(p_depol,2)
                    
                    # hier ist der Fehler nur auf dem Kontrollqubit
                    #single_depol_error = depolarizing_error(p_depol,1)
                    #no_error = pauli_error([('I', 1.0)])
                    #double_depol_error = no_error.tensor(single_depol_error)
                else:
                    double_depol_error = depolarizing_error(self.p_depol,2)
        
                
                fid_depol = average_gate_fidelity(double_depol_error)
    
                total_error = double_depol_error.compose(thermal_error)
                
                gate_fidelity = average_gate_fidelity(total_error)
                print(t1_0,t1_1)
                print(gatetime)
                print(gate_fidelity)
                self.gate_fidelities[str(pair)].update({gate: gate_fidelity})
                
                if self.check_model:
                    # check if gate fidelity of the model is equal to the measured gate fidelity 
                    diff_gateerror = (gateerror-(1-gate_fidelity))
                    if abs(diff_gateerror)>=0.00000001:
                        logging.info("difference of calculated and calibrated gate error: ", diff_gateerror)
        
                my_noise_model.add_quantum_error(total_error,[gate],pair)
    
                if self.check_model:            
                # compare with build-in model:
                    compareerror = Kraus((noise_model.__dict__)['_local_quantum_errors'][gate][str(pair[0])+","+str(pair[1])])
                    if (1-process_fidelity(Kraus(total_error),compareerror))>=0.00000001:
                        logging.info("operator deviation for qubits and gate ", pair, gate, ": ", 1-process_fidelity(Kraus(total_error),compareerror))
                        logging.info("\n")
        # add readout errors
        # get values for each qubit
        for i in range(self.configuration.n_qubits):
            l = self.properties.to_dict()['qubits'][i]
            for r in (d['value'] for d in l if d['name']=='prob_meas0_prep1'):
                p01=r
            for r in (d['value'] for d in l if d['name']=='prob_meas1_prep0'):
                p10=r
            prob_list = [[1-p10,p10],[p01,1-p01]]
            ro_error = ReadoutError(prob_list,i)
            my_noise_model.add_readout_error(ro_error,[i])
            self.gate_fidelities[str(i)].update({'ro_error': 1-((p10+p01)*0.5)})
        return my_noise_model

            
class SimpleNoiseModel:
    
    def __init__(
            self,
            n_qubits,
            t1,
            t2,
            singlegatetime,
            doublegatetime,
            single_qubit_gates,
            two_qubit_gates,
            coupling_map,
            basis_gates,
            p_depol=0.0,
            bool_therror=False,
            t=None, 
            single_gates_noisy=True
        ):
        
        
        self.p_depol = p_depol
        self.bool_therror = bool_therror
        self.single_gates_noisy = single_gates_noisy
        self.n_qubits = n_qubits
        self.t = t
        self.n_qubits = n_qubits
        self.t1 = t1
        self.t2 = t2
        self.singlegatetime = singlegatetime
        self.doublegatetime = doublegatetime
        self.single_qubit_gates = single_qubit_gates
        self.two_qubit_gates = two_qubit_gates
        self.coupling_map = coupling_map
        self.basis_gates = basis_gates
        
            
    def build_model(self):
        '''
        Builds a simple noise model for the NV center geometry
        with identical depolarizing and relaxation errors on all gates.

        Returns
        -------
        my_noise_model : simple noise model
        '''
        my_noise_model = NoiseModel()
        my_noise_model.add_basis_gates(['unitary'])
      
        if (self.bool_therror and self.p_depol==0):
            single_thermal_error = mse.thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.singlegatetime)
            if self.single_gates_noisy==True: 
                print('adding single qubit relaxation error with average gate fidelity: ',\
                      average_gate_fidelity(single_thermal_error))
                for i in range(self.n_qubits):
                   my_noise_model.add_quantum_error(single_thermal_error,self.single_qubit_gates,[i])
            single_thermal_error = mse.thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.doublegatetime)
            double_thermal_error = single_thermal_error.tensor(single_thermal_error)
            triple_thermal_error = double_thermal_error.tensor(single_thermal_error)
            quad_thermal_error = triple_thermal_error.tensor(single_thermal_error)
            print('adding relaxation error on CNOT with average gate fidelity: ',\
                  average_gate_fidelity(double_thermal_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_thermal_error,['cx'],pair)
            my_noise_model.add_all_qubit_quantum_error(triple_thermal_error,'c2rx')
            my_noise_model.add_all_qubit_quantum_error(quad_thermal_error,'c3rx')
                
        elif (self.p_depol>0 and not self.bool_therror):
            single_depol_error = depolarizing_error(self.p_depol,1)
            if self.single_gates_noisy==True:
                print('adding single qubit depolarizing error with average gate fidelity: ',\
                      average_gate_fidelity(single_depol_error))
                for i in range(self.n_qubits):
                    my_noise_model.add_quantum_error(single_depol_error,self.single_qubit_gates,[i])
            double_depol_error = single_depol_error.tensor(single_depol_error)
            triple_depol_error = double_depol_error.tensor(single_depol_error)
            quad_depol_error = triple_depol_error.tensor(single_depol_error)
            print('adding depolarizing error on CNOT with average gate fidelity: ',\
                  average_gate_fidelity(double_depol_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_depol_error,['cx'],pair)
            my_noise_model.add_all_qubit_quantum_error(triple_depol_error,'c2rx')
            my_noise_model.add_all_qubit_quantum_error(quad_depol_error,'c3rx')
                
        elif (self.bool_therror and self.p_depol>0):
            single_depol_error = depolarizing_error(self.p_depol,1)
            single_thermal_error = mse.thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.singlegatetime)
            single_total_error = single_depol_error.compose(single_thermal_error)
            if self.single_gates_noisy==True:
                print('adding single qubit relaxation and depolarizing error with average gate infidelity: ',\
                      average_gate_fidelity(single_total_error))
                for i in range(self.n_qubits):
                    my_noise_model.add_quantum_error(single_total_error,self.single_qubit_gates,[i])
                
            single_thermal_error = mse.thermal_relaxation_error(t1=self.t1, t2=self.t2, time=self.doublegatetime)
            double_thermal_error = single_thermal_error.tensor(single_thermal_error)
            triple_thermal_error = double_thermal_error.tensor(single_thermal_error)
            quad_thermal_error = triple_thermal_error.tensor(single_thermal_error)
            double_depol_error = single_depol_error.tensor(single_depol_error)
            triple_depol_error = double_depol_error.tensor(single_depol_error)
            quad_depol_error = triple_depol_error.tensor(single_depol_error)
            double_total_error = double_depol_error.compose(double_thermal_error)
            triple_total_error = triple_depol_error.compose(triple_thermal_error)
            quad_total_error = quad_depol_error.compose(quad_thermal_error)
            print('adding relaxation error on CNOT with average gate infidelity: ',\
                  average_gate_fidelity(double_depol_error))
            for pair in self.coupling_map:
                my_noise_model.add_quantum_error(double_total_error,['cx'],pair)
            my_noise_model.add_all_qubit_quantum_error(triple_total_error,'c2rx')
            my_noise_model.add_all_qubit_quantum_error(quad_total_error,'c3rx')
        
        return my_noise_model
   
class SimpleNoiseModel_NVCenter(SimpleNoiseModel):
    
    def __init__(self, n_qubits, p_depol=0.0, bool_therror=False, t=None, single_gates_noisy=True):
        basis_gates = ['x','y','rx','ry','id','cx','measure','reset']
        
        coupling_map = [ [i+1,0] for i in range(n_qubits-1)] + [ [0,i+1] for i in range(n_qubits-1)]
        # hier muss ich eigentlich zwischen dem Elekronspin und den Kernspins differenzieren. 
        #self.properties = {'t1':0.125,'t2':0.009, 'gatetime':{'sg':0.00007751937,'cx':0.000002}}
        # typcial properties for the ibm hardware
        self.properties = {'t1':0.0001,'t2':0.00015, 'gatetime':{'sg':0.00000005,'cx':0.0000005}}
        if (t==None):
            t2 = self.properties.get('t2')
            t1 = self.properties.get('t1')
        else:
            t2 = t
            t1 = t
            print('Using t1,t2=', t)
            
        super().__init__(n_qubits=n_qubits, p_depol=p_depol, bool_therror=bool_therror, t=t,
                        t1=t1,
                        t2=t2,
                        single_gates_noisy=single_gates_noisy,
                        singlegatetime=self.properties["gatetime"].get("sg"),
                        doublegatetime=self.properties["gatetime"].get("cx"),
                        single_qubit_gates=["x", "y", "rx", "ry", "id"],
                        two_qubit_gates=["cx","c2rx","c3rx"],
                        coupling_map=coupling_map,
                        basis_gates=basis_gates)
    
    def get_cx_agf_relax(self):
        return average_gate_fidelity(mse.thermal_relaxation_error\
                                     (t1=self.t1, t2=self.t2, time=self.doublegatetime))
    def get_single_agf_relax(self):
        return average_gate_fidelity(mse.thermal_relaxation_error\
                                     (t1=self.t1, t2=self.t2, time=self.singlegatetime))

class SimpleNoiseModel_IBM(SimpleNoiseModel):
    
    def __init__(self, n_qubits, p_depol=0.0, bool_therror=False,t=None,single_gates_noisy=True):

        basis_gates = ['x','sx','id','rz','cx','measure','reset']
        coupling_map = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

        self.properties = {'t1':0.0001,'t2':0.00015, 'gatetime':{'sg':0.00000005,'cx':0.0000005}}
        if (t==None):
            t2 = self.properties.get('t2')
            t1 = self.properties.get('t1')
        else:
            t2 = t
            t1 = t
            print('Using t1,t2=',t)
        
        super().__init__(n_qubits=n_qubits, p_depol=p_depol, bool_therror=bool_therror, t=t,
                        t1=t1,
                        t2=t2,
                        single_gates_noisy=single_gates_noisy,
                        singlegatetime=self.properties["gatetime"].get("sg"),
                        doublegatetime=self.properties["gatetime"].get("cx"),
                        single_qubit_gates=['x','sx','id'],
                        two_qubit_gates=["cx","c2rx","c3rx"],
                        coupling_map=coupling_map,
                        basis_gates=basis_gates)

    def get_agf_relax(self):
        return average_gate_fidelity(mse.thermal_relaxation_error\
                                     (t1=self.t1, t2=self.t2, time=self.doublegatetime))


