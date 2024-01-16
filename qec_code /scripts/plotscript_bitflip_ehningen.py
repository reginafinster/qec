# -*- coding: utf-8 -*-
"""
Created on Thu May 12 17:40:20 2022

@author: regina
"""

# plot results (optionally from file)
qpu_results = np.loadtxt('BitFlipDetectionQPUErrorQubit0_62021-12-21.dat')
sim_results = np.loadtxt('BitFlipDetectionMySimErrorQubit0_72021-12-21.dat')
#qpu_results = np.loadtxt('numerical_results/QPUResults/SydneyBitFlip_Qubit0_16Dez21/Results/averaged_results2021-12-20.dat')
#qpu_results = np.loadtxt('numerical_results/QPUResults/SydneyBitFlip_Qubit0_16Dez21/Results/BitFlipDetectionQPUErrorQubit0_52021-12-17.dat')


def plot_array(aresults):
    x = np.arange(len(aresults[:]))

    plt.figure(figsize=(12.0, 4.0))
    plt.xlabel('number of iteration over layout')
    plt.ylabel('logical error rates')
    plt.bar(x, qpu_results[:, 1],
            label='logical error rate qpu', fc=(1, 0, 0, 0.5))
    plt.bar(x, sim_results[:, 1], label='logical error rate my simulator', fc=(
        0, 1, 0, 0.5))
    plt.bar(
        x, aresults[:, 1], label='logical error rate IBM simulator', fc=(0, 0, 1, 0.5))
    #plt.bar(x,sortedsimresults[:,1], label='logical error IBM noise model', fc=(1, 0, 0, 0.5))
    plt.legend()
    plt.show()

    plt.figure(figsize=(12.0, 4.0))
    plt.bar(x, aresults[:, 2], label='average CNOT error')
    #plt.plot(aresults[:,2], linestyle='--', marker='o', label='average CNOT error')
    plt.xlabel('number of iteration over layout')
    plt.ylabel('average CNOT error')
    plt.legend()
    plt.show()

    plt.figure(figsize=(12.0, 4.0))
    plt.bar(x, aresults[:, 3], label='average T2')
    #plt.plot(aresults[:,3], linestyle='--', marker='o', label='average T2')
    plt.xlabel('number of iteration over layout')
    plt.ylabel('average T2')
    plt.legend()
    plt.show()

    plt.figure(figsize=(12.0, 4.0))
    plt.bar(x, aresults[:, 4], label='X Error')
    #plt.plot(aresults[:,4], linestyle='--', marker='o', label='average X Error')
    plt.xlabel('number of iteration over layout')
    plt.ylabel('X Error')
    plt.legend()
    plt.show()

    plt.figure(figsize=(12.0, 4.0))
    plt.bar(x, aresults[:, 5], label='Readout Error')
    #plt.plot(aresults[:,4], linestyle='--', marker='o', label='average X Error')
    plt.xlabel('number of iteration over layout')
    plt.ylabel('average readout error')
    plt.legend()
    plt.show()


plot_array(aresults[:])
