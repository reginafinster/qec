# -*- coding: utf-8 -*-
"""
Script mittelt numerische Ergebnisse. 
Der relative Pfad zum Ordner mit der Numerik sollte vom parent path der Skriptdatei starten.
"""

import sys
import numpy as np
import math as m
import os
from datetime import date

# if script is placed in parent folder of data folder, use:
#directory = sys.argv[2]

# absolute path (optinal)
#directory = 'C:/Users/regin/Nextcloud/Postdoc/numerical_results/QPUResults/NoiseModel12Dez21_withCatState/BitFlip_ErrorQubit1/'

parentdir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
directory = parentdir + '/numerical_results/QPUResults/Ehningen22-06-22/simulator/'
print(directory)
try:
    allfiles = [np.loadtxt(directory+f) for f in os.listdir(directory) if (os.path.isfile(os.path.join(directory, f)) and f.endswith(".dat"))]
    # option for absolute path or if script is placed in parent folder
    #allfiles = [np.loadtxt(os.path.abspath(f)) for f in listdir(directory) if (isfile(join(directory, f)) and f.endswith(".dat"))]
except:
    print(("check input dir {}. The following error occured").format(directory))
    raise

averaged_results = sum(allfiles)/len(allfiles)
np.savetxt((directory+"averaged_results"+str(date.today())+".dat"), averaged_results)
