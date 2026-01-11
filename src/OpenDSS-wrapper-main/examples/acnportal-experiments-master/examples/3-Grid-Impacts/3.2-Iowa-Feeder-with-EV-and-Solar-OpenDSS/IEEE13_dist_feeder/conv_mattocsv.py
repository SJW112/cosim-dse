## Convert from mat to csv pQ
import os
import opendssdirect as dss
import pandas as pd
import scipy.io as sio
import scipy.sparse as sp
from scipy.sparse import csc_matrix
import numpy as np
import csv
from datetime import datetime, timedelta

# dss.run_command('Redirect "acnportal-experiments-master/examples/3-Grid-Impacts/3.2-Iowa-Feeder-with-EV-and-Solar-OpenDSS/IEEE13_dist_feeder/IEEE13Nodeckt.dss')
# voltages = feeder.dss.Circuit.AllBusVMag()
"""
Script to test the IEEE13 test feeder
"""
dss.run_command('Redirect "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/IEEE13Nodeckt.dss"')
# voltages = feeder.dss.Circuit.AllBusVMag()
Y = csc_matrix(dss.YMatrix.getYsparse())
ymat= Y.toarray() 
# shhh=np.shape(ymat)
# print(shhh)
nNodes =len(ymat)
Nodes=nNodes
# print(Nodes)
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

offset=0
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

P=P.T
Q=Q.T
# column_headings = buses.ToList() 
column_headings=["LSRCa", "LSRCb", "LSRCc",
                "L650a", "L650b", "L650c",
                "LREGa", "LREGb", "LREGc",
                "L633a", "L633b", "L633c",
                "L634a", "L634b", "L634c",
                "L671a", "L671b", "L671c",
                "L645b", "L645c",
                "L646b", "L646c",
                "L692a", "L692b", "L692c",
                "L675a", "L675b", "L675c",
                "L611c",
                "L652a",
                "L670a", "L670b", "L670c",
                "L632a", "L632b", "L632c",
                "L680a", "L680b", "L680c",
                "L684a", "L684c"]
# df = pd.DataFrame(P, columns=column_headings)
# df2 = pd.DataFrame(Q, columns=column_headings)

# # df.to_csv("IEEE13_nodal_P.csv", index=False)  # Don't include index column
# # df2.to_csv("IEEE13_nodal_Q.csv", index=False)  # Don't include index column

# np.savetxt("IEEE_nodal_P.csv", P, delimiter=",", fmt="%d") 
# np.savetxt("IEEE_nodal_Q.csv", Q, delimiter=",", fmt="%d") 


# # Open the CSV file in write mode with '.csv' extension
# with open("P.csv", "w", newline="") as csvfile:
#   # Create a csv writer object
#   writer = csv.writer(csvfile)

#   # Write column headings if provided
#   if column_headings:
#     writer.writerow(column_headings)

#   # Write each row of data from the NumPy array
#   writer.writerows(P)
# with open("Q.csv", "w", newline="") as csvfile:
#   # Create a csv writer object
#   writer = csv.writer(csvfile)

#   # Write column headings if provided
#   if column_headings:
#     writer.writerow(column_headings)

#   # Write each row of data from the NumPy array
#   writer.writerows(Q)
# # Open the CSV file in write mode with '.csv' extension



# # Define starting and ending dates

# start_date = datetime(year=2017, month=1, day=1, hour=1)
# time_increment = timedelta(hours=1)  # Increment by 3 seconds
# end_date = datetime(year=2018, month=1, day=1, hour=0)

# # Number of hours (8760 hours in a year)
# num_hours = 8760

# date_list = [start_date + i * time_increment for i in range(num_hours)]  # Integer division for efficiency


# # Assuming your NumPy array is named 'data' (replace if different)
data = P
data2 = Q
# # Combine data and dates into a single array
# combined_data_P = np.column_stack((date_list, data))
# combined_data_Q = np.column_stack((date_list, data2))

# # Save combined data to a CSV file (optional)
# # np.savetxt("data_P.csv", combined_data_P, delimiter=",", fmt="%s", header=column_headings)
# header_string = ", ".join(column_headings)  # Join column names with commas
# # np.savetxt("data_P_new.csv", combined_data_P, delimiter=",", fmt="%s", header=header_string)
# # np.savetxt("data_Q_new.csv", combined_data_Q, delimiter=",", fmt="%s", header=header_string)
# np.savetxt("data_P_new.csv", combined_data_P, delimiter=",", fmt="%g", header=header_string)
# np.savetxt("data_Q_new.csv", combined_data_Q, delimiter=",", fmt="%g", header=header_string)

df = pd.DataFrame(data)
df2 = pd.DataFrame(data2)
# Save as CSV with automatic conversion
df.to_csv("data_P_new.csv", index=False)  # index=False to avoid row numbers
df2.to_csv("data_Q_new.csv", index=False)  # index=False to avoid row numbers

loads={}
LOAD_DIR="/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/acnportal-experiments-master/examples/3-Grid-Impacts/3.2-Iowa-Feeder-with-EV-and-Solar-OpenDSS/IEEE13_dist_feeder"
loads=pd.read_csv(f"{LOAD_DIR}//data_P_new.csv", parse_dates=True, index_col=0)


