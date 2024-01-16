# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 10:10:20 2021

@author: regina
"""



class AccessQPU:

def __init__(self):
    pass
        
def get_backend(self):
    provider = IBMQ.get_provider(project='ticket-ext')
    backend_name = 'ibmq_sydney' # oder toronto (gleicher Chip, Falcon4)
    backend = provider.get_backend(backend_name)

def _get_backend_properties(self):
    self.configuration = backend.configuration()
    self.coupling_map = configuration.coupling_map
    self.noise_model = NoiseModel.from_backend(backend)
    self.basis_gates = noise_model.basis_gates
    self.properties = backend.properties()

def dump_noise_model(self):
    # dump noise model for later use
    pickle_noise_model = [noise_model, configuration, properties]
    with open("noisemodel_" + backend_name + str(date.today()) + ".dat", "bw") as f:
        pickle.dump(pickle_noise_model,f)
        
def _load_noise_model_from_binary(self):
    with open("numerical_results/QPUResults/SydneyBitFlip_Qubit0_16Dez21/noisemodel_2_ibmq_sydney2021-12-21.dat", "br") as f:
    noise_data = pickle.load(f)
    self.noise_model = noise_data[0]
    self.configuration = noise_data[1]
    self.properties = noise_data[2]
    self.coupling_map = configuration.coupling_map
    self.basis_gates = noise_model.basis_gates

def _load_account_for_us_system(self):
    IBMQ.load_account()
    
def _load_account_for_ehningen(self):
    #IBMQ.disable_account()
    IBMQ.enable_account('807285e4f347ace42ec1d9020bd10ba9b708ec43e6394de8efb6ac412427e1a7ac87c1ab91bc7a7ca2ca67f02c708d371243234a58021d4017a7e6e223ac30a3', 'https://auth.de.quantum-computing.ibm.com/api')

def print_backend_info(self, backend):
    print(backend.name(), end=': ')
    print('simulator: ' + str(backend.configuration().simulator), end=', ')
    print(str(backend.configuration().n_qubits) + ' qubits', end=', ')
    print(str(backend.status().pending_jobs) + ' jobs', end=', ')
    print(backend.status().status_msg, end=', ')
    if 'runtime' in backend.configuration().input_allowed:
        print("supports Runtime: yes")
    else:
        print("supports Runtime: no")

def print_all_backend_info(self, provider):
    print("Provider:",provider)
    print("Infos for available backends:")
    for backend in provider.backends():
        self.print_backend_info(backend)
        
def run_qc_on_qpu(self):
    job_manager = IBMQJobManager()
    tqcs = []

    for l, layout in enumerate(layout_list):
        tqc = transpile(qc, backend=backend, optimization_level=0, initial_layout=layout[0])
        tqcs.append(tqc)
        
    job_set1 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set2 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set3 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set4 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set5 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set6 = job_manager.run(tqcs, backend=backend, shots=shots)
    job_set7 = job_manager.run(tqcs, backend=backend, shots=shots)