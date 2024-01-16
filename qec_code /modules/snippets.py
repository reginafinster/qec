# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:11:19 2022

@author: regina
"""

import numpy as np


class Input_Statevector:
    
    def __init__(self,stepsize_theta,stepsize_phi):
        self.stepsize_theta=stepsize_theta
        self.stepsize_phi=stepsize_phi
        
    def input_state_array_complex(self):
        input_state_list=[]
        for theta in np.linspace(start=0.0,stop=np.pi,num=self.stepsize_theta):
            for phi in np.linspace(start=0.0,stop=2.0*np.pi,num=self.stepsize_phi,endpoint=False):
                input_state_list.append([np.cos(theta*0.5),
                                         np.sin(theta*0.5)*np.exp(phi*1j)])
        #print("philist:", np.linspace(start=0.0,stop=2.0*np.pi,num=self.stepsize_phi,endpoint=False))
        #print("thetalist:", np.linspace(start=0.0,stop=np.pi,num=self.stepsize_theta))
        # crop all double input values with one coefficient = 0
        input_state_list = input_state_list[self.stepsize_phi-1:]
        input_state_array = np.array(input_state_list,dtype=complex)
        return input_state_array
        # use this line for rounding
        #return [[complex(np.round(x[0].real,5),np.round(x[0].imag,5)),complex(np.round(x[1].real,5),np.round(x[1].imag,5))] for x in input_state_list]
    
    def input_state_list_real_values(self):
        stepsize = 0.01
        polarization_values = np.arange(0.0,(1.0+stepsize),stepsize)
        return list(zip(polarization_values,list(reversed(polarization_values))))

import snippets

input_state = Input_Statevector(3,2).input_state_array_complex()
print(input_state)

