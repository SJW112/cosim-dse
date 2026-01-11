import os
import numpy as np
import datetime as dt
import pandas as pd
import opendssdirect as dss
from math import *
import scipy.io as sio
from scipy.sparse import csc_matrix
from collections import OrderedDict
import math as math
import scipy.sparse as sp  # Assuming IEEE13 data is loaded as a sparse matrix
import warnings
simLength = 2
D = 2
pd.set_option('display.precision', 3)      # precision in print statements
pd.set_option('expand_frame_repr', False)  # Keeps results on 1 line
pd.set_option('display.max_rows', 30)      # Shows up to 30 rows of data

"""
Script to test the IEEE13 test feeder
"""
dss.run_command('Redirect "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/IEEE13Nodeckt.dss"')

# voltages = feeder.dss.Circuit.AllBusVMag()
Y = csc_matrix(dss.YMatrix.getYsparse())
ymat= Y.toarray() 
nNodes =len(ymat)
Nodes=nNodes

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

# Remove Pn and Qn if not needed anymore (assuming they're temporary data)
del Pn, Qn


# Save P and Q to .mat format


# Power Flow calculations

# Initialize arrays with zeros (complex data type)
V = np.zeros((Nodes, simLength), dtype=complex)
I1 = np.zeros((Nodes, simLength), dtype=complex)
I2 = np.zeros((Nodes, simLength), dtype=complex)


sio.savemat('P_matrix.mat', {'P_matrix': P})
sio.savemat('Q_matrix.mat', {'Q_matrix': Q})

# Keyset
bus_names = OrderedDict([
    ('sourcebus.1', None), ('sourcebus.2', None), ('sourcebus.3', None),
	('650.1', None), ('650.2', None), ('650.3', None),                     
    ('rg60.1', None), ('rg60.2', None), ('rg60.3', None),                   
    ('633.1', None), ('633.2', None), ('633.3', None), 
    ('634.1', None), ('634.2', None), ('634.3', None),                
    ('671.1', None), ('671.2', None), ('671.3', None),                
    ('645.2', None), ('645.3', None),                
    ('646.2', None), ('646.3', None),                
    ('692.1', None), ('692.2', None), ('692.3', None),                
    ('675.1', None), ('675.2', None), ('675.3', None),
    ('611.3', None),
    ('652.1', None),
    ('670.1', None), ('670.2', None), ('670.3', None), 
    ('632.1', None), ('632.2', None), ('632.3', None),                
    ('680.1', None), ('680.2', None), ('680.3', None),  
    ('684.1', None), ('684.3', None),  
])

terminal2node = {}
terminal2node = {bus_name: i + 1 for i, bus_name in enumerate(bus_names)}

def runPF(P,Q,terminal2node,dss):

	DSSText = dss.Text
	DSSCircuit = dss.Circuit
	DSSSolution = dss.Solution

	node_list = list(terminal2node.keys())
	phaseIndex = ['a', 'b', 'c']


	for node_index in range(1, n_nodes):  
		current_key = node_list[node_index - 1]  # Access list element using index (0-based)
		current_node = terminal2node[current_key]

		# Assuming P has one row per node (row index = current_node - 1)
		if P[current_node - 1,] != 0:  # Access first column (assuming active power)
			bus_number, remain = current_key.split('.', 1)
			phase_number = int(remain.split('.', 1)[0])
			# Edit existing load (assuming loads exist)
			DSSText.Command = f"Edit Load.{bus_number}{phaseIndex[phase_number-1]} kW={P[current_node - 1,]/1000} kvar={Q[current_node-1]/1000}"

	DSSText.Command = 'vsource.source.enabled = yes'
	DSSSolution.Solve
	vckt = dss.Circuit.YNodeVArray()
	# print(vckt)
	vckt_len = len(vckt)
	V = np.zeros(int(vckt_len / 2), dtype=complex)
	for i in range(int(vckt_len / 2)):
		V[i] = vckt[2 * i] + 1j * vckt[2 * i + 1]  

	# Sender-end currents
	I_1 = np.zeros(nNodes, dtype=complex)  # Use complex for currents

	# Receiving-end currents
	I_2 = np.zeros(nNodes, dtype=complex)  # Use complex for currents

	# Loop through all Line
	lelem = dss.Lines.First()

	while lelem > 0:
		# Set active element as the current line
		DeviceIndex= DSSCircuit.SetActiveElement("Line." + dss.Lines.Name())

		# Get connected buses as a list
		# blist = dss.CktElement(DeviceIndex).BusNames()
		blist = dss.CktElement.BusNames()

		# Extract sender and receiver buses
		sender_bus = blist[0].split(".")[0]
		receiver_bus = blist[1].split(".")[0]

		# Get currents (real and imaginary components)
		# currents = dss.CktElement(DeviceIndex).Currents
		CArray = dss.CktElement.Currents()
		OArray=dss.CktElement.NodeOrder()
		num_phases = len(CArray) // 4
		start_index = 1 + len(CArray) // 4  # Starting index (inclusive)
		end_index = len(CArray) // 2  # Ending index (exclusive)

		# Loop through phases

		for p in range(1, len(CArray) // 4):  # Iterate using range and integer division
			
			bus_tuple = [sender_bus, '.', str(OArray[p - 1])]
			node_string = ''.join(bus_tuple)
			index = terminal2node.get(node_string)  # Call terminal2Node with string construction
			real_part = CArray[2 * p - 2].real
			imag_part = CArray[2 * p - 1].imag  # Extract imaginary part using imag()
			# I_1[index] = I_1.get(index, 0) + complex(real_part, imag_part)  # Handle potential missing key
			I_1[index] += complex(real_part, imag_part)
			
		for phase in range(start_index, end_index):
			bus_tuple = [receiver_bus, '.', str(OArray[phase - 1])]
			node_string = ''.join(bus_tuple)
			index = terminal2node.get(node_string) 
			# index = terminal2node([receiver_bus, '.', str(OArray[phase - 1])])
			real_part = CArray[2 * phase - 2].real
			imag_part = CArray[2 * phase - 1].imag  # Extract imaginary part using imag()
			# I_2[index] = I_2.get(index, 0) + complex(real_part, imag_part)  # Handle potential missing key
			I_2[index] += complex(real_part, imag_part)

		# Move to the next line
		lelem = dss.Lines.Next()


	telem = dss.Transformers.First()

	while telem > 0:
		# Set active element as the current transformer
		DSSCircuit.SetActiveElement("Transformer." +dss.Transformers.Name())

		# Get connected buses as a list
		# blist = dss.CktElement(DSSCircuit.ActiveElementIndex).BusNames
		blist = dss.CktElement.BusNames()

		# Extract sender and receiver buses
		sender_bus = blist[0].split(".")[0]
		receiver_bus = blist[1].split(".")[0]

		# Get currents (real and imaginary components)
		# currents = dss.CktElement(DSSCircuit.ActiveElementIndex).Currents
		CArray = dss.CktElement.Currents()
		num_elements = int(len(CArray) / 4 - 1)
		num_elements_2=int(1+len(CArray)/4)
		num_elements_3=int(len(CArray)/2-1)
		num_elements_4=int(len(CArray)/4)
		num_elements_5=int(1+len(CArray)/4)
		num_elements_6=int(len(CArray)/2)
		# Check if neutral conductor exists
		# has_neutral = any(dss.CktElement(DSSCircuit.ActiveElementIndex).NodeOrder == 0)
		has_neutral=any(node_order == 0 for node_order in dss.CktElement.NodeOrder())
		# Loop through phases based on neutral presence
		if has_neutral:
			# Transformer with neutral conductor
			for phase in range(1, num_elements):  # Exclude neutral phase
				# Sender-end current
				node_order = dss.CktElement.NodeOrder()[phase]
				sender_index=terminal2node[f"{sender_bus}.{node_order}"]
				I_1[sender_index] += CArray[2 * phase] + 1j * CArray[2 * phase + 1]

			for phase in range(num_elements_2,num_elements_3):
				# Receiver-end current
				node_order = dss.CktElement.NodeOrder()[phase]
				receiver_index=terminal2node[f"{receiver_bus}.{node_order}"]
				I_2[receiver_index] += CArray[2 * phase] + 1j * CArray[2 * phase + 1]
		else:
			# Transformer without neutral conductor
			for phase in range(1,num_elements_4):
				# Sender-end current
				node_order = dss.CktElement.NodeOrder()[phase]
				sender_index = terminal2node[f"{sender_bus}.{node_order}"]
				I_1[sender_index] += CArray[2 * phase] + 1j * CArray[2 * phase + 1]

			for phase in range(num_elements_5,num_elements_6):
				# Receiver-end current
				node_order = dss.CktElement.NodeOrder()[phase]
				receiver_index=terminal2node[f"{receiver_bus}.{node_order}"]
				I_2[receiver_index] += CArray[2 * phase] + 1j * CArray[2 * phase + 1]

		# Move to the next transformer
		telem = dss.Transformers.Next()

	for node_index in range(1, n_nodes):  
		current_key = node_list[node_index - 1]  # Access list element using index (0-based)
		current_node = terminal2node[current_key]

		# Assuming P has one row per node (row index = current_node - 1)
		if P[current_node - 1,] != 0:  # Access first column (assuming active power)
			bus_number, remain = current_key.split('.', 1)
			phase_number = int(remain.split('.', 1)[0])
			# Edit existing load (assuming loads exist)
			DSSText.Command = f"Edit Load.{bus_number}{phaseIndex[phase_number-1]} kW= 0 kvar= 0"

	return V,I_1,I_2


for i in range(simLength-1):
    # Call runPF and unpack results (assuming it returns a list or tuple)
    results = runPF(P[:, i], Q[:, i], terminal2node, dss)
    V[:, i], I1[:, i], I2[:, i] = results

I=I2-I1


def insert_missing_Yphases(Y):

  missing_phases = np.array([18, 21, 30, 31, 34, 35, 46])
  
  # Insert columns with zeros at missing phase indices
  for i in range(7):
    desired_cols_ids = np.array([missing_phases[i]], dtype=np.int64)
    zero_arr_row = np.zeros((1, Y.shape[1]))
    Y = np.insert(Y, desired_cols_ids, zero_arr_row, axis=0)
    zero_arr_col = np.zeros((Y.shape[0], 1))
    Y = np.insert(Y, desired_cols_ids, zero_arr_col, axis=1)
  return Y

def insert_missing_phases(X):
    # missing_phases = [18, 21, 30, 31, 34, 35, 46]
    missing_phases = np.array([18, 21, 30, 31, 34, 35, 46])
    X = X.T
    zero_arr_col = np.zeros((1,))
    for i in range(7):
        desired_cols_ids = np.array([missing_phases[i]], dtype=np.int64)
        X = np.insert(X, desired_cols_ids, zero_arr_col, axis=0)
    X = X.T
    # missing_phases = np.array([18, 21, 30, 31, 34, 35, 46])
    # for desired_col_id in missing_phases:
    #     num_existing_cols = X.shape[1]
    #     zero_arr_col = np.zeros((num_existing_cols, 1), dtype=X.dtype)
    #     X = np.insert(X, desired_col_id, zero_arr_col, axis=1)
    
    return X


def wrap_to_pi(angle):
  """Wraps an angle to the interval (-pi, pi].
  """
  (angle + math.pi) % (2 * math.pi) - math.pi
  return angle

def Griddata(Y):
    base_power = np.full((48,), 1e8)
    base_voltage = np.concatenate(([4160 * np.sqrt(3)] * 3,[2400] * 9,[(480 / np.sqrt(3))] * 3,[2400] * 33))
    #base_voltage = base_voltage.reshape(-1, 1)
    Nodes = np.arange(0, 16)  
    impedance_factor = base_power / (base_voltage**2)
    # impedance_factor = impedance_factor[3:] 
    Z_matrix = sp.linalg.inv(Y)
    Z_matrix =  Z_matrix.toarray()
    Z_all = insert_missing_Yphases(Z_matrix)
    # Z_all = Z_all[3:, 3:]
    R_all = Z_all.real * impedance_factor
    X_all = Z_all.imag * impedance_factor
  
    topology_initial = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [40, 41, 42],
        [37, 38, 39],
        [16, 17, 18],
        [40, 41, 42],
        [40, 41, 42],
        [10, 11, 12],
        [19, 20, 21],
        [25, 26, 27],
        [16, 17, 18],
        [46, 47, 48],
        [46, 47, 48],
        [16, 17, 18]
    ])
    topology_final = np.array([
        [4, 5, 6],
        [7, 8, 9],
        [37, 38, 39],
        [16, 17, 18],
        [43, 44, 45],
        [10, 11, 12],
        [19, 20, 21],
        [13, 14, 15],
        [22, 23, 24],
        [28, 29, 30],
        [46, 47, 48],
        [31, 32, 33],
        [34, 35, 36],
        [25, 26, 27]
    ])
    topology_initial = topology_initial-1
    topology_final = topology_final - 1

    topology_initial=np.array(topology_initial)
    topology_final=np.array(topology_final)
    topology_initial=topology_initial.T
    topology_final=topology_final.T
    topology_initial_a = topology_initial[0]
    topology_initial_b = topology_initial[1]
    topology_initial_c = topology_initial[2]
    topology_final_a = topology_final[0]
    topology_final_b = topology_final[1]
    topology_final_c = topology_final[2]
    cols = len(topology_initial_a)

    # Define Raa as an empty NumPy array with specified dimensions
    Raa = np.empty((1, cols))
    Rbb = np.empty((1, cols))
    Rab = np.empty((1, cols))
    Rbc = np.empty((1, cols))
    Rac = np.empty((1, cols))
    Rcc = np.empty((1, cols)) 
    Xaa = np.empty((1, cols))
    Xbb = np.empty((1, cols)) 
    Xab = np.empty((1, cols))
    Xbc = np.empty((1, cols)) 
    Xac = np.empty((1, cols))
    Xcc = np.empty((1, cols)) 


    for i in range(len(topology_initial_a)):  # Iterate through elements in the first row
        Raa_ = R_all[topology_initial_a[i], topology_final_a[i]]
        Rab_ = R_all[topology_initial_a[i], topology_final_b[i]]
        Rac_ = R_all[topology_initial_a[i], topology_final_c[i]]
        Rbb_ = R_all[topology_initial_b[i], topology_final_b[i]]
        Rbc_ = R_all[topology_initial_b[i], topology_final_c[i]]
        Rcc_ = R_all[topology_initial_c[i], topology_final_c[i]]

        Xaa_ = X_all[topology_initial_a[i], topology_final_a[i]]
        Xab_ = X_all[topology_initial_a[i], topology_final_b[i]]
        Xac_ = X_all[topology_initial_a[i], topology_final_c[i]]
        Xbb_ = X_all[topology_initial_b[i], topology_final_b[i]]
        Xbc_ = X_all[topology_initial_b[i], topology_final_c[i]]
        Xcc_ = X_all[topology_initial_c[i], topology_final_c[i]]

        Raa[:, i] = Raa_ 
        Rab[:, i] = Rab_
        Rac[:, i] = Rac_
        Rbb[:, i] = Rbb_
        Rbc[:, i] = Rbc_
        Rcc[:, i] = Rcc_

        Xaa[:, i] = Xaa_
        Xab[:, i] = Xab_
        Xac[:, i] = Xac_
        Xbb[:, i] = Xbb_
        Xbc[:, i] = Xbc_
        Xcc[:, i] = Xcc_  
        
    topology_initial = np.array([1, 2, 14, 13, 6, 14, 14, 4, 7, 9, 6, 16, 16, 6])
    topology_initial=topology_initial-1
    topology_final = np.array([2, 3, 13, 6, 15, 4, 7, 5, 8, 10, 16, 11, 12, 9])
    topology_final=topology_final-1

    Nodes_num = len(Nodes)  # Number of nodes in the grid
    Lines_num = len(topology_initial)  # Number of lines in the grid
    topology = [[i for i in range(1, Lines_num + 1)], topology_initial, topology_final]

    R1 = np.zeros((3, 3*Lines_num))
    X1 = np.zeros((3, 3*Lines_num))
    B1 = np.zeros((3, 3*Lines_num))
    G1 = np.zeros((3, 3*Lines_num))
    R2 = np.zeros((3, 3*Lines_num))
    X2 = np.zeros((3, 3*Lines_num))


    for i in range(Lines_num):
         R1[0, i] =     Raa[0,i]  
         R1[0, i + 1] = Rab[0,i] 
         R1[1, i] =     Rab[0,i]  
         R1[0, i + 2] = Rac[0,i]  
         R1[2, i] =     Rac[0,i]  
         R1[1, i + 1] = Rbb[0,i]  
         R1[1, i + 2] = Rbc[0,i]  
         R1[2, i + 1] = Rbc[0,i]  
         R1[2, i + 2] = Rcc[0,i]  
    for i in range(Lines_num):
        X1[0, i] =     Xaa[0,i]
        X1[0, i + 1] = Xab[0,i]
        X1[1, i] =     Xab[0,i]
        X1[0, i + 2] = Xac[0,i]
        X1[2, i] =     Xac[0,i]
        X1[1, i + 1] = Xbb[0,i]
        X1[1, i + 2] = Xbc[0,i]
        X1[2, i + 1] = Xbc[0,i]
        X1[2, i + 2] = Xcc[0,i]

   
    Raa = Raa.T 
    Rab = Rab.T
    Rac = Rac.T
    Rbb = Rbb.T
    Rbc = Rbc.T
    Rcc = Rcc.T

    Xaa = Xaa.T
    Xab = Xab.T
    Xac = Xac.T
    Xbb = Xbb.T
    Xbc = Xbc.T
    Xcc = Xcc.T    
    present_node = np.zeros((3, Nodes_num))
    present_line = np.zeros((3, Lines_num))
    topology=np.array(topology)

    #based on the the three phase information (aa,bb,cc,ab,ac,bc) of the PI
    #models, some matrices based on the connection of [3x3] blocks are
    #built. THese 3x3 blocks are the R,X,B,G components of the PI model of
    #that particular line. Depending on the missing phases there could be
    #some zeros in the matrices.

    # if (Raa[x] != 0 or Xaa[x] != 0) and (Rbb[x] != 0 and Xbb[x] != 0) and (Rcc[x] != 0 or Xcc[x] != 0):
    for x in range(Lines_num):
       if (np.any([Raa[x] != 0 , Xaa[x] != 0]) and np.all([Rbb[x] != 0, Xbb[x] != 0]) and np.any([Rcc[x] != 0, Xcc[x] != 0])):
         # Three-phase case
           Z1 = R1[:, 3 * (x - 1):3 * x] + 1j * X1[:, 3 * (x - 1):3 * x]  
           R2[:, 3 * (x - 1):3 * x] = np.real(1/(Z1))  
           X2[:, 3 * (x - 1):3 * x] = np.imag(1/(Z1)) 
           present_line[:, x] = [1, 1, 1]  
           present_node[:, topology[1, x]] += present_line[:, x]  
           present_node[:, topology[2, x]] += present_line[:, x]    

 #   if (np.any([Raa[x] != 0 or Xaa[x] != 0) and (Rbb[x] != 0 and Xbb[x] != 0) and (Rcc[x] == 0 or Xcc[x] == 0):

       if (np.any([Raa[x] != 0 , Xaa[x] != 0]) and np.all([Rbb[x] != 0,Xbb[x] != 0]) and np.any([Rcc[x] == 0 , Xcc[x] == 0])):
           # Two-phases (A and B)
           Z1 = R1[0:1, 3 * (x - 1):3 * (x - 1) + 2] + 1j * X1[0:2, 3 * (x - 1):3 * (x - 1) + 2]
           R2[0:1, 3 * (x - 1):3 * (x - 1) + 2] = np.real(1/(Z1))
           X2[0:1, 3 * (x - 1):3 * (x - 1) + 2] = np.imag(1/(Z1))   
           present_line[:, x] = [1, 1, 0]  
           present_node[:, topology[1, x]] += present_line[:, x]  
           present_node[:, topology[2, x]] += present_line[:, x]     
    
       # if (Raa[x] != 0 or Xaa[x] != 0) and (Rbb[x] == 0 and Xbb[x] == 0) and (Rcc[x] != 0 or Xcc[x] != 0):

       if (np.any([Raa[x] != 0,Xaa[x] != 0]) and np.all([Rbb[x] == 0, Xbb[x] == 0]) and np.any([Rcc[x] != 0,Xcc[x] != 0])):
           # Two-phases (A and C)
           Z1 = R1[[0, 2], slice(3 * (x - 1), 3 * (x - 1) + 4)] + 1j * X1[[0, 2], slice(3 * (x - 1), 3 * (x - 1) + 4)]
           R2[[0, 2], slice(3 * (x - 1), 3 * (x - 1) + 4)] = np.real(1/(Z1))
           X2[[0, 2], slice(3 * (x - 1), 3 * (x - 1) + 4)] = np.imag(1/(Z1))
           present_line[:, x] = [1, 0, 1]  
           present_node[:, topology[1, x]] += present_line[:, x]  
           present_node[:, topology[2, x]] += present_line[:, x]  
        # if (Raa[x] == 0 or Xaa[x] == 0) and (Rbb[x] != 0 or Xbb[x] != 0) and (Rcc[x] != 0 or Xcc[x] != 0):

       if (np.any([Raa[x] == 0, Xaa[x] == 0]) and np.any([Rbb[x] != 0, Xbb[x] != 0]) and np.any([Rcc[x] != 0,Xcc[x] != 0])):
           
           # Two-phases (B and C)
           Z1 = R1[1:3, 3 * (x - 1) + 1:3 * (x - 1) + 3] + 1j * X1[1:3, 3 * (x - 1) + 1:3 * (x - 1) + 3] 
           R2[1:3, 3 * (x - 1) + 1:3 * (x - 1) + 3] = np.real(1/(Z1))  
           X2[1:3, 3 * (x - 1) + 1:3 * (x - 1) + 3] = np.imag(1/(Z1)) 
           present_line[:, x] = [0, 1, 1]
           present_node[:, topology[1, x]] += present_line[:, x] 
           present_node[:, topology[2, x]] += present_line[:, x]   

    #    if (Raa[x] != 0 or Xaa[x] != 0) and (Rbb[x] == 0 and Xbb[x] == 0) and (Rcc[x] == 0 and Xcc[x] == 0):
       if (np.any([Raa[x] != 0, Xaa[x] != 0]) and np.all([Rbb[x] == 0, Xbb[x] == 0]) and np.all([Rcc[x] == 0, Xcc[x] == 0])):
          # Single-phase case (A)

           Z1 = R1[0, 3 * (x - 1) + 1] + 1j * X1[0, 3 * (x - 1) + 1]  
           R2[0, 3 * (x - 1) + 1] = np.real(1/(Z1))  
           X2[0, 3 * (x - 1) + 1] = np.imag(1/(Z1))  
           present_line[:, x] = [1, 0, 0]  
           present_node[:, topology[1, x]] += present_line[:, x]  
           present_node[:, topology[2, x]] += present_line[:, x]  
    
    #    if (Raa(x) == 0 or Xaa(x) == 0) and (Rbb[x] != 0 or Xbb[x] != 0) and (Rcc[x] == 0 and Xcc[x] == 0):
       if (np.any([Raa[x] == 0, Xaa[x] == 0]) and np.all([Rbb[x] != 0, Xbb[x] != 0]) and np.all([Rcc[x] == 0, Xcc[x] == 0])):
           # Single-phase case (B)
           Z1 = R1[1, 3 * (x - 1) + 1] + 1j * X1[1, 3 * (x - 1) + 1] 
           R2[1, 3 * (x - 1) + 1] = np.real(1/(Z1)) 
           X2[1, 3 * (x - 1) + 1] = np.imag(1/(Z1))  
           present_line[:, x] = [0, 1, 0] 
           present_node[:, topology[1, x]] += present_line[:, x] 
           present_node[:, topology[2, x]] += present_line[:, x] 
       
    #  if (Raa(x) == 0 or Xaa(x) == 0) and (Rbb(x) == 0 and Xbb(x) == 0) and (Rcc[x] != 0 or Xcc[x] != 0):

       if (np.any([Raa[x] == 0, Xaa[x] == 0]) and np.all([Rbb[x] == 0, Xbb[x] == 0]) and np.any([Rcc[x] != 0, Xcc[x] != 0])):
           # Single-phase case (C)
           
           Z1 = R1[2, 3 * (x - 1) + 2] + 1j * X1[2, 3 * (x - 1) + 2]  # Impedance (complex)
           R2[2, 3 * (x - 1) + 2] = np.real(1/(Z1))  
           X2[2, 3 * (x - 1) + 2] = np.imag(1/(Z1))  
           present_line[:, x] = [0, 0, 1] 
           present_node[:, topology[1, x]] += present_line[:, x]  
           present_node[:, topology[2, x]] += present_line[:, x]  

    missing_node_phase = []
    for node in range(Nodes_num):  
        for phase in range(3):  # Loop through phases (A, B, C)
            if present_node[phase, node] == 0:
                missing_node_phase.append(6 * node + 2 * phase + 1)  
            missing_node_phase.append(6 * node + 2 * phase + 2)  

    missing_line_phase = []
    for line in range(Lines_num):  
        for phase in range(3):  # Loop through phases (A, B, C)
            if present_line[phase, line] == 0:
                missing_line_phase.append(6 + 6 * line + 2 * phase + 1)  
                missing_line_phase.append(6 + 6 * line + 2 * phase + 2)     

    GridData = {}  # Create an empty dictionary
    GridData["missing_node_phase"] = np.sort(missing_node_phase) 
    GridData["missing_line_phase"] = np.sort(missing_line_phase)  
    GridData["present_node"] = present_node  
    GridData["present_line"] = present_line 

    A=np.zeros((Lines_num,Nodes_num))
    for m in range(Lines_num):
        for n in range(Nodes_num):
            if topology[2, m] == n:  
                A[m, n] = 1
            else:
                if topology[1, m] == n:  
                    for t in range(Lines_num):
                        if A[t, topology[1, m]] == 1:  
                            A[m, n] = 1  
                            break  
                        
    # Assign values to GridData dictionary
    GridData["Nodes_num"] = Nodes_num
    GridData["Lines_num"] = Lines_num
    GridData["topology"] = topology
    GridData["base_power"] = base_power
    GridData["base_voltage"] = base_voltage
    GridData["base_current"] = GridData["base_power"] / GridData["base_voltage"]
    GridData["base_impedance"] = GridData["base_voltage"] / GridData["base_current"]
    GridData["R1"] = R1
    GridData["X1"] = X1
    GridData["B1"] = B1
    GridData["G1"] = G1
    GridData["R2"] = R2
    GridData["X2"] = X2
    GridData["A"] = A
    GridData["inj_status"] = 0
    GridData["rm_column "]=0
    return GridData



def PowerDData(GridData,V,P,Q,I):
    V_all = V[:, 0]
    I_all = I[:, 0]
    P_all = P[:, 0]
    Q_all = Q[:, 0]
    V_all=insert_missing_phases(V_all)
    I_all=insert_missing_phases(I_all)
    P_all=insert_missing_phases(P_all)
    Q_all=insert_missing_phases(Q_all)
    base_voltage = np.concatenate(([4160 * np.sqrt(3)] * 3,[2400] * 9,[(480 / np.sqrt(3))] * 3,[2400] * 33))
    V_all=V_all/base_voltage
    # V_all=np.delete(V_all, np.arange(3), axis=0) 
    # I_all=np.delete(I_all, np.arange(3), axis=0)
    # P_all=np.delete(P_all, np.arange(3), axis=0)
    # Q_all=np.delete(Q_all, np.arange(3), axis=0)
    Vmagn = np.abs(V_all)  
    Vph = np.angle(V_all)  
    V_magn = Vmagn.reshape(3, -1) 
    V_ph = Vph.reshape(3, -1)    # Reshape Vph to 3x (any number of columns)
    Pinj = np.reshape(P_all, (3, -1))  
    Qinj = np.reshape(Q_all, (3, -1))  
    Amps = np.reshape(I_all, (3, -1))  
    base_power = 1e8
    GridData["base_current"] = base_power / 2400
    PowerData = {}  
    PowerData["Pinj"] = Pinj / base_power  
    PowerData["Qinj"] = Qinj / base_power  
    PowerData["Vmagn"] = V_magn  # Voltage magnitude
    PowerData["Vph"] = V_ph  # Voltage phase angle
    Volts = V_all.reshape(3, -1)  # Reshape Volts to 3x (any number of columns)
    
    PowerData["Pflow"] = np.zeros((len(Volts), len(GridData["topology"][2, :]))) 
    PowerData["Qflow"] = np.zeros((len(Volts), len(GridData["topology"][2, :]))) 
    PowerData["Iph"]   = np.zeros((np.shape(Amps))) 

    for m in range(GridData["Lines_num"]):
        PowerData["Pflow"][:, m] = np.real(Volts[:, GridData["topology"][2, m]] * np.conj(Amps[:, m]))
        PowerData["Qflow"][:, m] = np.imag(Volts[:, GridData["topology"][2, m]] * np.conj(Amps[:, m]))
        PowerData["Vph"] = np.where(PowerData["Vph"] > np.pi, PowerData["Vph"] - 2 * np.pi, PowerData["Vph"])
    PowerData["Imagn"] = np.abs(Amps)
    PowerData["Iph"][0, :] = np.where(np.angle(Amps[0, :]) > np.pi, np.angle(Amps[0, :]) - 2 * np.pi, np.angle(Amps[0, :]))
    PowerData["Iph"][1, :] = np.where(np.angle(Amps[1, :]) > np.pi, np.angle(Amps[1, :]) - 2 * np.pi, np.angle(Amps[1, :]))
    PowerData["Iph"][2, :] = np.where(np.angle(Amps[2, :]) > np.pi, np.angle(Amps[2, :]) - 2 * np.pi, np.angle(Amps[2, :]))
    return PowerData


def DSSEConfData(GridData): #here the test configuration data are set: measurement devices location and accuracy
   Test_SetUp = {}
   Test_SetUp["N_MC"] = 1500; #number of MC simulation, for reliable results set between 1000 and 10 000
   Test_SetUp["limit1"] = 0.000001; #treshold accuracy to interrupt newton rapson
   Test_SetUp["limit2"] = 50; #maximum number of iterations
   Test_SetUp["time_steps"] = 1; #number of time step in each MC simulation 
   Combination_P = np.array(range(2, 16))  
   Combination_Q = np.array(range(2, 16)) 
   Combination_Pseudo = np.array(range(1, GridData["Nodes_num"]))  
   Combination_Vmagn = np.array(range(2, 15))
   Combination_Vph=    np.array(range(2, 15))
   Combination_Imagn =   np.zeros(GridData["Lines_num"])
   Combination_Iph =     np.zeros(GridData["Lines_num"]) 
   Combination_Pflow =   np.zeros(GridData["Lines_num"]) 
   Combination_Qflow =   np.zeros(GridData["Lines_num"])
   unc_dev = 0.01/3
   unc_pseudo = 0.5/3
   #the structure with the information of the measurements available
   Combination_devices= {}
   Combination_devices["Combination_P "]= Combination_P
   Combination_devices["Combination_Q"] = Combination_Q
   Combination_devices["Combination_Vmagn"] = Combination_Vmagn
   Combination_devices["Combination_Vph"] = Combination_Vph
   Combination_devices["Combination_Imagn"] = Combination_Imagn
   Combination_devices["Combination_Iph"] = Combination_Iph
   Combination_devices["Combination_Pflow"] = Combination_Pflow
   Combination_devices["Combination_Qflow"] = Combination_Qflow
   Combination_devices["Combination_Pseudo"] = Combination_Pseudo

   #the accuracy for each class of device is assigned
   Accuracy_P = np.sqrt(2 * unc_dev**2) #accuracy of active power injection measurement
   Accuracy_Q = np.sqrt(2 * unc_dev**2) #accuracy of reactive power injection measurement
   Accuracy_Vmagn = unc_dev #accuracy of  voltage magnitude measurement
   Accuracy_Vph = unc_dev #accuracy of  voltage phase measurement
   Accuracy_Imagn = unc_dev #accuracy of  current magnitude measurement
   Accuracy_Iph = unc_dev #accuracy of  current phase measurement
   Accuracy_Pflow = np.sqrt(2 * unc_dev**2) #accuracy of active power flow measurement
   Accuracy_Qflow = np.sqrt(2 * unc_dev**2) #accuracy of reactive power flow measurement
   Accuracy_pseudo = unc_pseudo


   # structure with the accuracies of the measurements
   Accuracy={}
   Accuracy["Accuracy_P"]=Accuracy_P
   Accuracy["Accuracy_Q"]=Accuracy_Q
   Accuracy["Accuracy_Vmagn"]=Accuracy_Vmagn
   Accuracy["Accuracy_Vph"]=Accuracy_Vph
   Accuracy["Accuracy_Imagn"]=Accuracy_Imagn
   Accuracy["Accuracy_Iph"]=Accuracy_Iph
   Accuracy["Accuracy_Pflow"]=Accuracy_Pflow   
   Accuracy["Accuracy_Qflow"]=Accuracy_Qflow  
   Accuracy["Accuracy_pseudo"]=Accuracy_pseudo  


   Pseudo_measure=np.zeros((1, GridData["Nodes_num"]))
   P_measure=np.zeros((1, GridData["Nodes_num"]))
   Q_measure=np.zeros((1, GridData["Nodes_num"]))
   Vmagn_measure=np.zeros((1, GridData["Nodes_num"]))
   Vph_measure=np.zeros((1, GridData["Nodes_num"]))
   Imagn_measure=np.zeros((1, GridData["Lines_num"]))
   Iph_measure=np.zeros((1, GridData["Lines_num"]))
   Pflow_measure=np.zeros((1, GridData["Lines_num"]))
   Qflow_measure=np.zeros((1, GridData["Lines_num"]))

   for n in range(1, GridData["Nodes_num"] + 1):  
        if  np.size(Combination_P) != 0:  
            if  np.any(np.isin(Combination_P[0], n)):
                P_measure[0, n - 1] = 1

        if np.size(Combination_Q) != 0:   
            if  np.any(np.isin(Combination_Q[0], n)):  
                Q_measure[0, n - 1] = 1 

        if np.size(Combination_Pseudo) !=0:  
            if  np.any(np.isin(Combination_Pseudo[0], n)):  
                Pseudo_measure[0, n - 1] = 1 

        if np.size(Combination_Vmagn) != 0:  
            if  np.any(np.isin(Combination_Vmagn[0], n)): 
                Vmagn_measure[0, n - 1] = 1 

        if np.size(Combination_Vph)!=0:  
            if  np.any(np.isin(Combination_Vph[0], n)):  
                Vph_measure[0, n - 1] = 1 

   for n in range(1, GridData["Lines_num"] + 1):  
       if np.size(Combination_Imagn) !=0:  
           if  np.any(np.isin(Combination_Imagn[0], n)): 
               Imagn_measure[0, n - 1] = 1  
     
       if np.size(Combination_Iph) != 0:  
           if  np.any(np.isin(Combination_Iph[0], n)):  
               Iph_measure[0, n - 1] = 1 

       if np.size(Combination_Pflow) != 0:  
           if  np.any(np.isin(Combination_Pflow[0], n)):  
               Pflow_measure[0, n - 1] = 1 

       if np.size(Combination_Qflow) != 0:  
           if  np.any(np.isin(Combination_Qflow[0], n)):  
               Qflow_measure[0, n - 1] = 1 

   Combination_devices["P_measure"] = np.vstack([P_measure, np.zeros_like(P_measure)])
   Combination_devices["Q_measure"] = np.vstack([Q_measure, np.zeros_like(Q_measure)])
   Combination_devices["Vmagn_measure"] = np.vstack([Vmagn_measure, np.zeros_like(Vmagn_measure)])
   Combination_devices["Vph_measure"] = np.vstack([Vph_measure, np.zeros_like(Vph_measure)])
   Combination_devices["Imagn_measure"] = np.vstack([Imagn_measure, np.zeros_like(Imagn_measure)])
   Combination_devices["Iph_measure"] = np.vstack([Iph_measure, np.zeros_like(Iph_measure)])
   Combination_devices["Pflow_measure"] = np.vstack([Pflow_measure, np.zeros_like(Pflow_measure)])
   Combination_devices["Qflow_measure"] = np.vstack([Qflow_measure, np.zeros_like(Qflow_measure)])
   Combination_devices["Pseudo_measure"] = np.vstack([Pseudo_measure, np.zeros_like(Pseudo_measure)])
   
   return  Test_SetUp,Combination_devices,Accuracy


def Weightm(GridData,PowerData,Combination_devices, Accuracy):
    
    LM = 1e-12 #minimum acceptable variance
    Gx = 0

    if Combination_devices["Vph_measure"][0, 0] == 1:  # Assuming dictionary access
        Gx += 1

    n = 0
    LocationMeas = [ ]
    TypeMeas = [ ]
    PhaseMeas= [ ]
    DelayMeas =[ ]


    W = np.zeros((0, 0))  
    R = np.zeros((0, 0)) 
    for x in range(1, GridData["Nodes_num"] + 1): 
        for f in range(1, 4):  
            if GridData["present_node"][f - 1, x - 1] != 0: 
                if Combination_devices["P_measure"][0, x - 1] == 1:  # Active power measurement
                    Rtemp = (Accuracy["Accuracy_P"] * PowerData["Pinj"][f - 1, x - 1])**2
                    Rtemp = max(LM, Rtemp)  
                    if n + 1 > R.shape[0]:
                        new_size = max(2 * R.shape[0], n + 1)  # Ensure enough space
                        R = np.pad(R, ((0, new_size - R.shape[0]), (0, new_size - R.shape[0])), mode='constant')
                        W = np.pad(W, ((0, new_size - W.shape[0]), (0, new_size - W.shape[0])), mode='constant')
                    R[n, n] = Rtemp
                    W[n, n] = 1 / Rtemp
                    n += 1
                    LocationMeas.append(x)
                    TypeMeas.append(1)  
                    PhaseMeas.append(f)  # Append f to PhaseMeas
                    DelayMeas.append(Combination_devices["P_measure"][0, x-1])  
                elif Combination_devices["Pseudo_measure"][0, x - 1] == 1 :  
                    Rtemp = (Accuracy["Accuracy_pseudo"] * PowerData["Pinj"][f - 1, x - 1])**2
                    Rtemp = max(LM, Rtemp)  
                    if Rtemp < LM:
                        Rtemp = LM
                    if n + 1 > R.shape[0]:
                        new_size = max(2 * R.shape[0], n + 1)  # Ensure enough space
                        R = np.pad(R, ((0, new_size - R.shape[0]), (0, new_size - R.shape[0])), mode='constant')
                        W = np.pad(W, ((0, new_size - W.shape[0]), (0, new_size - W.shape[0])), mode='constant')
                    R[n, n] = Rtemp
                    W[n, n] = 1 / Rtemp
                    n += 1
                    LocationMeas.append(x)
                    TypeMeas.append(1)  
                    PhaseMeas.append(f)  # Append f to PhaseMeas
                    DelayMeas.append(Combination_devices["Pseudo_measure"][0, x-1])  
                
                if Combination_devices["Q_measure"][0, x - 1] == 1:  # Active power measurement
                    Rtemp = (Accuracy["Accuracy_Q"] * PowerData["Qinj"][f - 1, x - 1])**2
                    Rtemp = max(LM, Rtemp)  
                    R[n, n] = Rtemp
                    W[n, n] = 1 / Rtemp
                    n += 1
                    LocationMeas.append(x-1)
                    TypeMeas.append(2)  
                    PhaseMeas.append(f-1)  
                    DelayMeas.append(Combination_devices["Pseudo_measure"][1, x-1])  

                elif  Combination_devices["Pseudo_measure"][0, x - 1] == 1 :  
                    Rtemp = (Accuracy["Accuracy_pseudo"] * PowerData["Qinj"][f - 1, x - 1])**2
                    Rtemp = max(LM, Rtemp)  
                    if Rtemp < LM:
                        Rtemp = LM
                    if n + 1 > R.shape[0]:
                        new_size = max(2 * R.shape[0], n + 1)  # Ensure enough space
                        R = np.pad(R, ((0, new_size - R.shape[0]), (0, new_size - R.shape[0])), mode='constant')
                        W = np.pad(W, ((0, new_size - W.shape[0]), (0, new_size - W.shape[0])), mode='constant')

                    R[n, n ] = Rtemp
                    W[n, n] = 1 / Rtemp
                    n += 1
                    LocationMeas.append(x-1)
                    TypeMeas.append(2)  
                    PhaseMeas.append(f-1)  
                    DelayMeas.append(Combination_devices["Pseudo_measure"][1, x-1])  
                
                if (Combination_devices["Vmagn_measure"][0, x - 1] == 1 and Combination_devices["Vph_measure"][0, x - 1] == 1):
                    if x == 1:  # Remove phase measurement from the first bus
                        rot_v = np.cos(PowerData["Vph"][f - 1, x - 1])  # Assuming PowerData is a NumPy array
                        Rtemp = rot_v * ((Accuracy["Accuracy_Vmagn"] * PowerData["Vmagn"][f - 1, x - 1])**2) * rot_v
                        Rtemp = max(LM, Rtemp)  # Ensure Rtemp is at least LM (vectorized)
                        R[n + 1, n + 1] = Rtemp
                        W[n + 1, n + 1] = 1 / Rtemp
                        n += 1
                        LocationMeas[n, 0] = x
                        TypeMeas[n, 0] = 3  # Voltage magnitude measurement
                        PhaseMeas[n, 0] = f
                        DelayMeas[n, 0] = Combination_devices["Vmagn_measure"][1, x - 1]
                        
                    else:  # Other buses (including voltage magnitude and phase angle)
                        rot_v = np.array([[np.cos(PowerData["Vph"][f - 1, x - 1]), -sin(PowerData["Vph"][f - 1, x - 1]) * PowerData["Vmagn"][f - 1, x - 1]],[sin(PowerData["Vph"][f - 1, x - 1]),cos(PowerData["Vph"][f - 1, x - 1]) * PowerData["Vmagn"][f - 1, x - 1]]])
                        Rtemp = rot_v @ np.diag([Accuracy["Accuracy_Vmagn"]**2 * PowerData["Vmagn"][f - 1, x - 1]**2,
                                          Accuracy["Accuracy_Vph"]**2]) @ rot_v
                        
                    
                        if n + 1 > R.shape[0]:
                            new_size = max(2 * R.shape[0], n + 1)  # Ensure enough space
                            R = np.pad(R, ((0, new_size - R.shape[0]), (0, new_size - R.shape[0])), mode='constant')
                            W = np.pad(W, ((0, new_size - W.shape[0]), (0, new_size - W.shape[0])), mode='constant')

                        # Rtemp[0, 0] = max(LM, Rtemp[0, 0])  # Ensure diagonal elements are at least LM
                        # Rtemp[1, 1] = max(LM, Rtemp[1, 1])
                        # R[n:n + 1, n:n + 1] = Rtemp
                        # W[n:n + 1, n:n + 1] = np.linalg.inv
                        R[n, n] = max(LM, Rtemp[0, 0])
                        # W[n, n] = np.linalg.inv(Rtemp)  
                        weight = 1 / (Accuracy["Accuracy_Vmagn"]**2 * PowerData["Vmagn"][f - 1, x - 1]**2 + Accuracy["Accuracy_Vph"]**2)
                        W[n, n] = weight   
                        # Measurement 1: Voltage Magnitude
                        n += 1
                        LocationMeas.append(x-1)
                        TypeMeas.append(3)  
                        PhaseMeas.append(f-1)  
                        DelayMeas.append(Combination_devices["Vmagn_measure"][0, x-1])  

                        
                        # Measurement 1: Voltage Angle
                        n += 1
                        LocationMeas.append(x-1)
                        TypeMeas.append(4)  
                        PhaseMeas.append(f-1)  
                        DelayMeas.append(Combination_devices["Vmagn_measure"][0, x-1])  
       

     #now we search for measurements in the lines
    
    for b in range(1, GridData["Lines_num"]+ 1):  # Loop through lines (1 to Lines_num)
        for f in range(1, 4):  # Loop through phases (1 to 3)
            if GridData["present_line"][f - 1, b - 1] != 0:  # Check for line presence (adjusted indexing)

                # Current magnitude and phase angle measurement (combined)
                if (Combination_devices["Imagn_measure"][0, b - 1] != 0 and
                        Combination_devices["Iph_measure"][0, b - 1] != 0):
                    rot_i = np.array([[np.cos(PowerData["Iph"][f - 1, b - 1]),
                                    -sin(PowerData["Iph"][f - 1, b - 1]) * PowerData["Imagn"][f - 1, b - 1]],
                                    [sin(PowerData["Iph"][f - 1, b - 1]),
                                    cos(PowerData["Iph"][f - 1, b - 1]) * PowerData["Imagn"][f - 1, b - 1]]])

                    std_dev = np.diag([Accuracy["Accuracy_Imagn"]**2 * PowerData["Imagn"][f - 1, b - 1]**2,
                                    Accuracy.Accuracy_Iph**2])
                    Rtemp = rot_i @ std_dev @ rot_i.T

                    Rtemp[0, 0] = max(LM, Rtemp[0, 0])  # Ensure diagonal elements are at least LM
                    Rtemp[1, 1] = max(LM, Rtemp[1, 1])

                    R[n + 1:n + 2, n + 1:n + 2] = Rtemp
                    W[n + 1:n + 2, n + 1:n + 2] = np.linalg.inv(Rtemp)  # Inverse for weights

                    # Measurement 1: Current Magnitude
                    n += 1
                    LocationMeas[n, 0] = b
                    TypeMeas[n, 0] = 5  # Current magnitude measurement
                    PhaseMeas[n, 0] = f
                    DelayMeas[n, 0] = Combination_devices["Imagn_measure"][1, b - 1]

                    # Measurement 2: Current Phase Angle
                    n += 1
                    LocationMeas[n, 0] = b
                    TypeMeas[n, 0] = 6  # Current phase angle measurement
                    PhaseMeas[n, 0] = f
                    DelayMeas[n, 0] = Combination_devices["Iph_measure"][1, b - 1]

                # Active power flow measurement
                if Combination_devices["Pflow_measure"][0, b - 1] != 0:
                    Rtemp = (Accuracy.Accuracy_Pflow * PowerData.Pflow[f - 1, b - 1])**2
                    Rtemp = max(LM, Rtemp)  # Ensure Rtemp is at least LM (vectorized)

                    R[n + 1, n + 1] = Rtemp
                    W[n + 1, n + 1] = 1 / Rtemp
                    n += 1

                    LocationMeas[n, 0] = b
                    TypeMeas[n, 0] = 7  # Active power flow measurement
                    PhaseMeas[n, 0] = f
                    DelayMeas[n, 0] = Combination_devices["Pflow_measure"][1, b - 1]

                # Reactive power flow measurement
                if Combination_devices["Qflow_measure"][0, b - 1] != 0:
                    Rtemp = (Accuracy.Accuracy_Qflow * PowerData.Qflow[f - 1, b - 1])**2
                    Rtemp = max(LM, Rtemp)  # Ensure Rtemp is at least LM (vectorized)

                    R[n + 1, n + 1] = Rtemp
                    W[n + 1, n + 1] = 1 / Rtemp
                    n += 1

                    LocationMeas[n, 0] = b
                    TypeMeas[n, 0] = 8  # Reactive power flow measurement
                
    GridData["MeasNum"] = n
    GridData["TypeMeas"] = TypeMeas
    GridData["LocationMeas"] = LocationMeas
    GridData["DelayMeas"] = DelayMeas
    GridData["PhaseMeas"] = PhaseMeas

    return W,GridData,R


def calc_hx_VRIDSSE(Vmagn_status,Vph_status,GridData,inj_status):

    # Steps:
    # 1) Calculate the branch currents based on the voltage differences and the
    # model-parameters of the lines
    # 2) calculate the injection currents based on the branch currents and kirckoff law
    hx = np.zeros((GridData['MeasNum'], 1))
    I_branch = np.zeros((3, GridData['Lines_num']))
    I_load = np.zeros((3, GridData['Nodes_num']))
    Volts = np.zeros((3, GridData['Nodes_num']))
    isinjection=inj_status #this is for dynamic programming
    for x in range(GridData['Nodes_num']):
        for f in range(3):
            Volts[f, x] = Vmagn_status[f, x] * np.exp(1j * Vph_status[f, x])  # Complex exponential

    I_branch = np.zeros((3, GridData['Lines_num']), dtype=complex)
    for m in range(GridData['Lines_num']):
        n_i = GridData['topology'][1, m] - 1  # Adjust for zero-based indexing
        n_f = GridData['topology'][2, m] - 1  # Adjust for zero-based indexing 
        V_i = Volts[:, n_i]
        V_f = Volts[:, n_f]
        R = GridData['R2'][:, 3*m-2:3*m]
        X = GridData['X2'][:, 3*m-2:3*m]
        B = GridData['B1'][:, 3*m-2:3*m]
        G = GridData['G1'][:, 3*m-2:3*m]
        Y = G + 1j * B  # Combined admittance matrix
        Z = R + 1j * X  # Impedance matrix
        I_branch[:, m] = 0.5 * Y * (V_i + V_f) - 0.5 * Y * (V_f + V_i) + 0.5 * Z * (V_i - V_f)
   
    # Calculate Injection Currents
    for x in range(GridData['Nodes_num']):
        for m in range(GridData['Lines_num']):
            if GridData['topology'][2,m]-1== x:
                I_load[:, x] += I_branch[:, GridData['topology'][2, m] - 1]
            else:
                if  GridData['topology'][3,m]-1== x:
                    I_load[:, x] += I_branch[:, GridData['topology'][3, m] - 1]

    # calculate h(x)
    for n in range(GridData['MeasNum']):
        if GridData['TypeMeas'][n, 0] == 1:  # real current measurement (adjusted for zero-based indexing)
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.real(I_load[phase, location])  # Extract real part of load current
        
        if GridData['TypeMeas'][n, 0] == 2:  #  imag current measurement (adjusted for zero-based indexing)
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.imag(I_load[phase, location])  # Extract real part of load current
        
        if GridData['TypeMeas'][n, 0] == 3:  # Voltage magnitude measurement -translated to Vreal
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.real(Volts[phase, location])  # Extract real part of load current
        
        if GridData['TypeMeas'][n, 0] == 4:  # Voltage phase angle measurement -translated to Vimag
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.imag(Volts[phase, location])  # Extract real part of load current

        if GridData['TypeMeas'][n, 0] == 5:  # current magnitude -translated to Ireal
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.real(I_branch[phase, location])  # Extract real part of load current
        
        if GridData['TypeMeas'][n, 0] == 6:  # current phase-translated to Iimag
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.imag(I_branch[phase, location])  # Extract real part of load current

        if GridData['TypeMeas'][n, 0] == 7:  # pflow translated to Ireal
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.real(I_branch[phase, location])  # Extract real part of load current
        
        if GridData['TypeMeas'][n, 0] == 8:  # qflow translatded to Iimag
            phase = GridData['PhaseMeas'][n, 0] - 1  # Adjust for zero-based indexing
            location = GridData['LocationMeas'][n, 0] - 1  # Adjust for zero-based indexin
            hx[n, 0] = np.imag(I_branch[phase, location])  # Extract real part of load current

    return hx 


def Jacobian_m_VRIDSSE(GridData):
    
    R =  GridData["R2"]  
    X =  GridData["X2"]  
    B = GridData["B1"]
    G = GridData["G1"]

    H = np.zeros((GridData["MeasNum"], 6 * GridData["Nodes_num"]))  # Initialize H matrix with zeros
    for n in range(0, GridData["MeasNum"]):
        if GridData["TypeMeas"][n] == 1:  # Check for active power measurement
            for x in range(1, GridData["Lines_num"] + 1):
                f = GridData['PhaseMeas'][n - 1]  # Extract phase measurement
                if f == 1:
                   a = 2
                   b = 3
                elif f == 2:
                    a = 1
                    b = 3
                else:
                    a = 1
                    b = 2

            if GridData['topology'][2-1, x-1] == GridData['LocationMeas'][n]:  #initial node of the branch
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * f] -= (0.5 * G[f, 3 * x + f] + R[f, 3 * x + f])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * a] -= (0.5 * G[f, 3 * x + a] + R[f, 3 * x + a])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * b] -= (0.5 * G[f, 3 * x + b] + R[f, 3 * x + b])

                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * f + 1] += (0.5 * B[f, 3 * x + f] + X[f, 3 * x + f])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * a + 1] += (0.5 * B[f, 3 * x + a] + X[f, 3 * x + a])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * b + 1] += (0.5 * B[f, 3 * x + b] + X[f, 3 * x + b])

                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f] = (-0.5 * G[f, 3 * (x - 1) + f] + R[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * a] = (-0.5 * G[f, 3 * (x - 1) + a] + R[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b] = (-0.5 * G[f, 3 * (x - 1) + b] + R[f, 3 * (x - 1) + b])
                
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f + 1] = (0.5 * B[f, 3 * (x - 1) + f] - X[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * a + 1] = (0.5 * B[f, 3 * (x - 1) + a] - X[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b + 1] = (0.5 * B[f, 3 * (x - 1) + b] - X[f, 3 * (x - 1) + b])
            elif GridData['topology'][3-1, x-1] == GridData['LocationMeas'][n] :  #final node of the branch
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * f] += (0.5 * G[f, 3 * (x - 1) + f] - R[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * a] += (0.5 * G[f, 3 * (x - 1) + a] - R[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * b] += (0.5 * G[f, 3 * (x - 1) + b] - R[f, 3 * (x - 1) + b])
                
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * f] -= (0.5 * B[f, 3 * (x - 1) + f] - X[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * a] -= (0.5 * B[f, 3 * (x - 1) + a] - X[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['LocationMeas'][n, 0] - 1) + 2 * b] -= (0.5 * B[f, 3 * (x - 1) + b] - X[f, 3 * (x - 1) + b])
               
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f] = (0.5 * G[f, 3 * (x - 1) + f] + R[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * a] = (0.5 * G[f, 3 * (x - 1) + a] + R[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b] = (0.5 * G[f, 3 * (x - 1) + b] + R[f, 3 * (x - 1) + b])
                
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f + 1] = (-0.5 * B[f, 3 * (x - 1) + f] + X[f, 3 * (x - 1) + f])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * a + 1] = (-0.5 * B[f, 3 * (x - 1) + a] + X[f, 3 * (x - 1) + a])
                H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b + 1] = (-0.5 * B[f, 3 * (x - 1) + b] + X[f, 3 * (x - 1) + b])

        if GridData['TypeMeas'][n] == 2:  # Reactive power measurements
            for x in range(GridData['Lines_num']):
                f = GridData['PhaseMeas'][n]
                if f == 1:
                   a = 2
                   b = 3
                elif f == 2:
                    a = 1
                    b = 3
                else:
                    a = 1
                    b = 2 
                if GridData['topology'][2-1, x] == GridData['LocationMeas'][n]:
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * f] -= (0.5 * B[f, 3 * (x - 1) + f] + X[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * a] -= (0.5 * B[f, 3 * (x - 1) + a] + X[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * b] -= (0.5 * B[f, 3 * (x - 1) + b] + X[f, 3 * (x - 1) + b])
                    
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * f + 1] -= (0.5 * G[f, 3 * (x - 1) + f] + R[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * a + 1] -= (0.5 * G[f, 3 * (x - 1) + a] + R[f, 3 * (x - 1) + a]) 
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * b + 1] -= (0.5 * G[f, 3 * (x - 1) + b] + R[f, 3 * (x - 1) + b])
                    
                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f]  = -(0.5 * B[f, 3 * (x - 1) + f] - X[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * a]  = -(0.5 * B[f, 3 * (x - 1) + a] - X[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b]  = -(0.5 * B[f, 3 * (x - 1) + b] - X[f, 3 * (x - 1) + b])

                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f + 1] = -(0.5 * G[f, 3 * (x - 1) + f] - R[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * f + 1] =- (0.5 * G[f, 3 * (x - 1) + a] - R[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['topology'][2, x] - 1) + 2 * b + 1] = -(0.5 * G[f, 3 * (x - 1) + b] - R[f, 3 * (x - 1) + b])

                elif GridData['topology'][3-1, x] == GridData['LocationMeas'][n] : 
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * f] += (0.5 * B[f, 3 * (x - 1) + f] - X[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * a] += (0.5 * B[f, 3 * (x - 1) + a] - X[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * b] += (0.5 * B[f, 3 * (x - 1) + b] - X[f, 3 * (x - 1) + b])
                    
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * f] += (0.5 * G[f, 3 * (x - 1) + f] - R[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * a] += (0.5 * G[f, 3 * (x - 1) + a] - R[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * b] += (0.5 * G[f, 3 * (x - 1) + b] - R[f, 3 * (x - 1) + b])
                
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * f] = (0.5 * B[f, 3 * (x - 1) + f] + X[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * a] = (0.5 * B[f, 3 * (x - 1) + a] + X[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * b] = (0.5 * B[f, 3 * (x - 1) + b] + X[f, 3 * (x - 1) + b])
                    
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * f + 1] = (0.5 * G[f, 3 * (x - 1) + f] + R[f, 3 * (x - 1) + f])
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * a + 1] = (0.5 * G[f, 3 * (x - 1) + a] + R[f, 3 * (x - 1) + a])
                    H[n, 6 * (GridData['topology'][1, x] - 1) + 2 * b + 1] = (0.5 * G[f, 3 * (x - 1) + b] + R[f, 3 * (x - 1) + b])


                if GridData['TypeMeas'][n]  == 3:
                    H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * (GridData['PhaseMeas'][n] - 1)] = 1  # Assuming dV_re_i_1/dV_re_i_1 = 1 for voltage magnitude
                    
                if GridData['TypeMeas'][n] == 4:
                   H[n, 6 * (GridData['LocationMeas'][n] - 1) + 2 * (GridData['PhaseMeas'][n] - 1)]  # Assuming dV_im_i_1/dV_im_i_1 = 1 for voltage phase angle                   

  
                if GridData['TypeMeas'][n] == 5:  # Current magnitude measurements
                    in1 = GridData['topology'][2, GridData['LocationMeas'][n]] 
                    fin1 = GridData['topology'][3, GridData['LocationMeas'][n]] - 1  # Convert indexing

                    f = GridData['PhaseMeas'][n] - 1  # Convert phase index to 0-based indexing
                    a = f + 1 if f < 2 else 0  # Phase a based on f
                    b = (f + 2) % 3  # Phase b based on f

                    H[n, 6 * in1 + 2 * f] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * fin1 + 2 * f] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * fin1 + 2 * f + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]


                if GridData['TypeMeas'][n] == 6:  # Current phase measurements
                    in1 = GridData['topology'][2, GridData['LocationMeas'][n]] - 1  # Convert indexing
                    fin1 = GridData['topology'][3, GridData['LocationMeas'][n]] - 1  # Convert indexing

                    f = GridData['PhaseMeas'][n] - 1  # Convert phase index to 0-based indexing
                    a = f + 1 if f < 2 else 0  # Phase a based on f
                    b = (f + 2) % 3  # Phase b based on f

                    # Initial node updates
                    H[n, 6 * in1 + 2 * f + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    # Final node updates
                    H[n, 6 * fin1 + 2 * f + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * fin1 + 2 * f] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]
                
                if GridData['TypeMeas'][n] == 7:  # Assuming TypeMeas 7 for active power flow
                    in1 = GridData['topology'][2, GridData['LocationMeas'][n]] - 1  # Convert indexing

                    f = GridData['PhaseMeas'][n] - 1  # Convert phase index to 0-based indexing
                    a = f + 1 if f < 2 else 0  # Phase a based on f
                    b = (f + 2) % 3  # Phase b based on f

                   
                    H[n, 6 * in1 + 2 * f] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                if GridData['TypeMeas'][n] == 8:  # Assuming TypeMeas 8 for reactive power flow
                    fin1 = GridData['topology'][3, GridData['LocationMeas'][n]] - 1  # Convert indexing
                    in1 = GridData['topology'][2, GridData['LocationMeas'][n]] - 1  # Convert indexing

                    f = GridData['PhaseMeas'][n] - 1  # Convert phase index to 0-based indexing
                    a = f + 1 if f < 2 else 0  # Phase a based on f
                    b = (f + 2) % 3  # Phase b based on f

                    H[n, 6 * in1 + 2 * f + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b + 1] = 0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * in1 + 2 * f] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * in1 + 2 * a] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * in1 + 2 * b] = 0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] + R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * fin1 + 2 * f + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b + 1] = -0.5 * B[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - X[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

                    H[n, 6 * fin1 + 2 * f] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + f]
                    H[n, 6 * fin1 + 2 * a] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + a]
                    H[n, 6 * fin1 + 2 * b] = -0.5 * G[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b] - R[f, 3 * GridData['LocationMeas'][n, 0] - 1 + b]

        #the imaginary part of the slack bus is not a state (phase angle = 0),
        #therefore it can be deleted 
    delete_1st_bus = [2, 4, 6]
    delete_1st_bus = [bus - 1 for bus in delete_1st_bus] # convert to zero indexing

    delete_columns = np.unique(np.concatenate((delete_1st_bus, GridData['missing_node_phase'] - 1)))
    # Combine real and imaginary parts of slack bus (assuming columns 3 and 4)
    H[:, 2] += 3 / np.sqrt(3) * H[:, 3]
    H[:, 4] -= 3 / np.sqrt(3) * H[:, 5]
    print(np.shape(H))
    H = np.delete(H, delete_columns, axis=1)
    # H = np.delete(H, 3, axis=1)  # Delete imaginary part of slack bus
    return H


def calc_Mvector(GridData, PowerData):
  """
  Calculates the measurement vector based on measurement types in GridData.

  Args:
      GridData: A dictionary containing measurement data (TypeMeas, PhaseMeas, LocationMeas).
      PowerData: A dictionary containing power system data (Pinj, Qinj, Vmagn, Vph, Imagn, Iph, Pflow, Qflow).

  Returns:
      Meas_vector: A NumPy array containing the calculated measurement values.
  """

  Meas_vector = np.zeros(GridData['MeasNum'])  # Initialize measurement vector

  for n in range(GridData['MeasNum']):
    meas_type = GridData['TypeMeas'][n]
    phase = GridData['PhaseMeas'][n] - 1  # MATLAB indexing starts from 1, Python from 0
    location = GridData['LocationMeas'][n] - 1

    if meas_type == 1:  # Active power injection
      Meas_vector[n] = PowerData['Pinj'][phase, location]
    elif meas_type == 2:  # Reactive power injection
      Meas_vector[n] = PowerData['Qinj'][phase, location]
    elif meas_type == 3:  # Voltage magnitude (converted to real part)
      Meas_vector[n] = np.real(PowerData['Vmagn'][phase, location] * np.exp(1j * PowerData['Vph'][phase, location]))
    elif meas_type == 4:  # Voltage phase angle (converted to imaginary part)
      Meas_vector[n] = np.imag(PowerData['Vmagn'][phase, location] * np.exp(1j * PowerData['Vph'][phase, location]))
    elif meas_type == 5:  # Current magnitude (converted to real part)
      Meas_vector[n] = np.real(PowerData['Imagn'][phase, location] * np.exp(1j * PowerData['Iph'][phase, location]))
    elif meas_type == 6:  # Current phase angle (converted to imaginary part)
      Meas_vector[n] = np.imag(PowerData['Imagn'][phase, location] * np.exp(1j * PowerData['Iph'][phase, location]))
    elif meas_type == 7:  # Power flow (converted to real part for consistency)
      Meas_vector[n] = PowerData['Pflow'][phase, location]
    elif meas_type == 8:  # Reactive power flow (converted to real part for consistency)
      Meas_vector[n] = PowerData['Qflow'][phase, location]
    else:
      raise ValueError("Invalid measurement type:", meas_type)

  return Meas_vector

def VRIDSSE(PowerData,W,GridData,Test_SetUp):
    
    H = Jacobian_m_VRIDSSE(GridData)
    glue=np.shape(H)
    print(glue)
    rrr=np.shape(W)
    print(rrr)
    HW = np.dot(H.conj().T, W)
    G1 = HW*H; #gain matrix
    G2 = G1
    P_post = np.linalg.inv(G2)

    Vmagn_status = np.ones((3, GridData.Nodes_num))
    Vph_status = np.zeros((3, GridData.Nodes_num))
    Vph_status[1, :] = (4/3) * np.pi  
    Vph_status[2, :] = (2/3) * np.pi 
    inj_status = 0
    max_delta=10 #dummy inizialitazion
    iteration=0
    
    # Newton Rapson calculation of the state
    while max_delta > 1e-12 and iteration < Test_SetUp.limit2:
        iteration += 1
        # Update measurement vector
        Meas_vector = calc_Mvector(GridData, PowerData)
        # Calculate h(x) vector
        hx = calc_hx_VRIDSSE(Vmagn_status, Vph_status, GridData, inj_status)
        # Build residual vector
        res = Meas_vector - hx
        HWres = np.dot(HW, res)
        G1_inv = np.linalg.inv(G1)
        delta = G1_inv @ HWres
        n=1
        # Update voltage states
        # Slack bus (bus 1)
        Volts = Vmagn_status * np.exp(1j * Vph_status)
        Vreal = np.real(Volts)
        Vreal[0, 0] += delta[0]  # Update only magnitude for slack bus
        Volts[0, 0] = Vreal[0, 0]
        Vmagn_status[0, 0] = np.abs(Volts[0, 0])
        Vph_status[0, 0] = np.angle(Volts[0, 0])


        # PQ buses (buses 2 and 3)
        for i in range(1, 3):
            Vreal[i, 0] += delta[i + 1]
            Volts[i, 0] = Vreal[i, 0] + 1j * Vreal[i, 0] * (3 / np.sqrt(3) if i == 1 else -3 / np.sqrt(3))
            Vmagn_status[i, 0] = np.abs(Volts[i, 0])
            Vph_status[i, 0] = np.angle(Volts[i, 0])

        n = 2  # Counter for remaining elements in delta (starts after slack and PQ buses)

        for bus in range(1, GridData.Nodes_num):
            for phase in range(3):
                if GridData.present_node(phase, bus) > 0:
                    Volts[phase, bus] += delta[n]
                    n += 1
                    Volts[phase, bus] += 1j * delta[n]
                    n += 1
                Vmagn_status[phase, bus] = np.abs(Volts[phase, bus])
                Vph_status[phase, bus] = np.angle(Volts[phase, bus])

        # Calculate maximum delta for convergence check
        max_delta = np.max(np.abs(delta))    
        #based on the estimated voltages we calculate also the currents
        Imagn_status = np.ones((3, GridData.Lines_num))
        Iph_status = np.ones((3, GridData.Lines_num))
        I_branch = np.ones((3, GridData.Lines_num))
        for m in range(1, GridData.Lines_num + 1):
            n_i = GridData.topology[2 - 1, m - 1]  
            n_f = GridData.topology[3 - 1, m - 1]  # Convert from 1-based indexing to 0-based

            V_i = Volts[:, n_i]
            V_f = Volts[:, n_f]

            R = GridData.R2[:, 3 * m - 2: 3 * m] 
            X = GridData.X2[:, 3 * m - 2: 3 * m]
            B = GridData.B1[:, 3 * m - 2: 3 * m]
            G = GridData.G1[:, 3 * m - 2: 3 * m]

            I_branch[:, m - 1] = 0.5 * (G + 1j * B) * (V_i + V_f) + (R + 1j * X) * (V_i - V_f)
            # Store current in m-1th column (0-based indexing)

            Imagn_status[:, m - 1] = np.abs(I_branch[:, m - 1])  # Calculate and store magnitude
            Iph_status[:, m - 1] = np.angle(I_branch[:, m - 1])  # Calculate and store phase angle
    
    # for p  in range(Vph_status):
    #     Vph_status = wrap_to_pi(Vph_status(p))
    #     Iph_status = wrap_to_pi(Iph_status(p))

    if iteration == Test_SetUp.limit2:
        max_delta()  # Assuming max_delta is a function


    return Vmagn_status, Vph_status

## State estimation
GridData=Griddata(Y)
PowerData=PowerDData(GridData,V,P,Q,I)
Test_SetUp,Combination_devices,Accuracy=DSSEConfData(GridData)
W,GridData,R=Weightm(GridData,PowerData,Combination_devices,Accuracy)
Vmagn_status, Vph_status = VRIDSSE(PowerData, W, GridData, Test_SetUp)
