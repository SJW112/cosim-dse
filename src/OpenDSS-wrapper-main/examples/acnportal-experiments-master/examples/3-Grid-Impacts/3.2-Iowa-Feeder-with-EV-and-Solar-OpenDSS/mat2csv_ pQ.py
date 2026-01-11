## Convert from mat to csv pQ
import os
import opendssdirect as dss
import pandas as pd
import scipy.io as sio
import scipy.sparse as sp
from scipy.sparse import csc_matrix
import numpy as np

dss.run_command('Redirect "acnportal-experiments-master/examples/3-Grid-Impacts/3.2-Iowa-Feeder-with-EV-and-Solar-OpenDSS/IEEE13_dist_feeder/IEEE13Nodeckt.dss')

# voltages = feeder.dss.Circuit.AllBusVMag()
Y = csc_matrix(dss.YMatrix.getYsparse())
ymat= Y.toarray() 
nNodes =len(ymat)
Nodes=nNodes
simLength = 8760

LSRC = 0
L650a = 0
L650b = 0
L650c = 0

LREG = 0

L632a = 100
L632b = 80
L632c = 90

L670a = 20
L670b = 10
L670c = 10

L671a = 10
L671b = 14
L671c = 12

L680a = 90
L680b = 110
L680c = 120

L633a = 25
L633b = 32
L633c = 20

L634a = 30
L634b = 32
L634c = 25

L692a = 0
L692b = 0
L692c = 0

L675a = 40
L675b = 35
L675c = 25

L645b = 20
L645c = 30

L646b = 65
L646c = 80

L684a = 20
L684c = 15

L652a = 50

L611c = 50

homesPerNode = [LSRC, LSRC, LSRC,
				L650a, L650b, L650c,
				LREG, LREG, LREG,
				L633a, L633b, L633c,
				L634a, L634b, L634c,
				L671a, L671b, L671c,
				L645b, L645c,
				L646b, L646c,
				L692a, L692b, L692c,
				L675a, L675b, L675c,
				L611c,
				L652a,
				L670a, L670b, L670c,
				L632a, L632b, L632c,
				L680a, L680b, L680c,
				L684a, L684c]

offset=1
startIndex = offset
endIndex =  simLength
n_nodes = len(homesPerNode)

reactive_power_file = "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/For_python/reactivepower1260homes-1day.mat"
real_power_file   =     "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/For_python/realpower1260homes-1day.mat"
Pn = sio.loadmat(real_power_file)["Pn"]
Qn = sio.loadmat(reactive_power_file)["Qn"]

# Assuming Pn and Qn represent real and reactive power data for individual homes
# (replace this with your actual data access logic)
P = np.zeros((n_nodes, endIndex - startIndex))
Q = np.zeros((n_nodes, endIndex - startIndex))
ind = 1

for i in range(n_nodes):
	P[i, :] = np.sum(Pn[ind:ind + homesPerNode[i] - 1, startIndex:endIndex], axis=0)
	Q[i, :] = np.sum(Qn[ind:ind + homesPerNode[i] - 1, startIndex:endIndex], axis=0)
	ind += homesPerNode[i]


np.savetxt("IEEE_nodal_P.csv", P, delimiter=",", fmt="%d") 
np.savetxt("IEEE_nodal_Q.csv", Q, delimiter=",", fmt="%d") 

