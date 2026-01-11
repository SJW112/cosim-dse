
import os
import datetime as dt
import pandas as pd
from opendss_wrapper import OpenDSS
import opendssdirect as dss
import numpy as np
import scipy.io as sio
import scipy.sparse as sp
from scipy.sparse import csc_matrix
from collections import OrderedDict

simLength = 10
D = 10
pd.set_option('display.precision', 3)      # precision in print statements
pd.set_option('expand_frame_repr', False)  # Keeps results on 1 line
pd.set_option('display.max_rows', 30)      # Shows up to 30 rows of data
# pd.set_option('max_columns', None)       # Prints all columns

"""
Script to test the IEEE13 test feeder
"""
dss.run_command('Redirect "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/IEEE13Nodeckt.dss"')

# Run 1 timestep
# print()
# print('Running 1 time step...')
# feeder.run_dss()
# print()

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

# Print the mapping dictionary (optional)
# print(mapping_terminal2node)
DSSText = dss.Text
DSSCircuit = dss.Circuit
DSSSolution = dss.Solution

node_list = list(terminal2node.keys())
phaseIndex = ['a', 'b', 'c']


for node_index in range(1, n_nodes):  
    current_key = node_list[node_index - 1]  # Access list element using index (0-based)
    current_node = terminal2node[current_key]

    # Assuming P has one row per node (row index = current_node - 1)
    if P[current_node - 1, 0] != 0:  # Access first column (assuming active power)
        bus_number, remain = current_key.split('.', 1)
        phase_number = int(remain.split('.', 1)[0])
        # Edit existing load (assuming loads exist)
        DSSText.Command = f"Edit Load.{bus_number}{phaseIndex[phase_number-1]} kW={P[current_node - 1, 0]/1000} kvar={Q[current_node]/1000}"

DSSText.Command = 'vsource.source.enabled = yes'
DSSSolution.Solve()
vckt = dss.Circuit.AllBusVolts
print(vckt)
vckt_len = len(vckt)
V = np.zeros(int(vckt_len / 2), dtype=complex)
for i in range(int(vckt_len / 2)):
    V[i] = vckt[2 * i] + 1j * vckt[2 * i + 1]  

# Sender-end currents
I_1 = np.zeros(nNodes, dtype=complex)  # Use complex for currents

# Receiving-end currents
I_2 = np.zeros(nNodes, dtype=complex)  # Use complex for currents

# Loop through all lines
lelem = DSSCircuit.Lines.First

while lelem > 0:
    # Set active element as the current line
    DSSCircuit.SetActiveElement("Line." + DSSCircuit.Lines.Name)

    # Get connected buses as a list
    blist = DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).BusNames

    # Extract sender and receiver buses
    sender_bus = blist[0].split(".")[0]
    receiver_bus = blist[1].split(".")[0]

    # Get currents (real and imaginary components)
    currents = DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).Currents
    num_phases = len(currents) // 2

    # Loop through phases
    for phase in range(num_phases):
        # Sender-end current
        sender_index = terminal2node[f"{sender_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase]}"]
        I_1[sender_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]

        # Receiver-end current
        receiver_index = terminal2node[f"{receiver_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase + num_phases]}"]
        I_2[receiver_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]

    # Move to the next line
    lelem = DSSCircuit.Lines.Next


telem = DSSCircuit.Transformers.First

while telem > 0:
    # Set active element as the current transformer
    DSSCircuit.SetActiveElement("Transformer." + DSSCircuit.Transformers.Name)

    # Get connected buses as a list
    blist = DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).BusNames

    # Extract sender and receiver buses
    sender_bus = blist[0].split(".")[0]
    receiver_bus = blist[1].split(".")[0]

    # Get currents (real and imaginary components)
    currents = DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).Currents
    num_phases = len(currents) // 2

    # Check if neutral conductor exists
    has_neutral = any(DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder == 0)

    # Loop through phases based on neutral presence
    if has_neutral:
        # Transformer with neutral conductor
        for phase in range(num_phases - 1):  # Exclude neutral phase
            # Sender-end current
            sender_index = terminal2node[f"{sender_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase]}"]
            I_1[sender_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]

            # Receiver-end current
            receiver_index = terminal2node[f"{receiver_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase + num_phases]}"]
            I_2[receiver_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]
    else:
        # Transformer without neutral conductor
        for phase in range(num_phases):
            # Sender-end current
            sender_index = terminal2node[f"{sender_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase]}"]
            I_1[sender_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]

            # Receiver-end current
            receiver_index = terminal2node[f"{receiver_bus}.{DSSCircuit.CktElements(DSSCircuit.ActiveElementIndex).NodeOrder[phase + num_phases]}"]
            I_2[receiver_index] += currents[2 * phase] + 1j * currents[2 * phase + 1]

    # Move to the next transformer
    telem = DSSCircuit.Transformers.Next





# DSS_EXE_PATH = BASE_DIR + 'SmartGridMain/'
# TOPO_RPATH_FILE = 'IEEE13/outfile.dss'
# NWL_RPATH_FILE  = 'IEEE13/IEEE13_NodeWithLoadFull.csv'
# ILPQ_RPATH_FILE = 'IEEE13/IEEE13_InelasticLoadPQ.csv'
# DEVS_RPATH_FILE = 'IEEE13/IEEE13_Devices.csv'

# pflowsim    = world.start('PFlowSim',
#                               topofile = DSS_EXE_PATH + TOPO_RPATH_FILE,
#                               nwlfile  = DSS_EXE_PATH + NWL_RPATH_FILE,
#                               ilpqfile = DSS_EXE_PATH + ILPQ_RPATH_FILE,
#                               loadgen_interval = 80, # IEEE13
#                               verbose = 0)  
