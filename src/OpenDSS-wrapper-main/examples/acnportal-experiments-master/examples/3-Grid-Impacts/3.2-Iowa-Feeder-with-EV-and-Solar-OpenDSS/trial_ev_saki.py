
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz
from datetime import datetime, date, timedelta
from datetime import timedelta
from copy import deepcopy
from tqdm import tqdm

import opendssdirect as dss

from acnportal import acnsim
from acnportal import algorithms
import os
import tempfile


CIRCUIT_DIR = "IEEE13_dist_feeder"
LOAD_DIR = "IEEE13_data"

start = datetime(2017, 9, 5),
horizon = 24 * 60
period = 5,
reg_control= False

def export_to_df(measurement: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"{measurement}.csv")
        saved_file = dss.run_command(f"export {measurement} {path}")
        return pd.read_csv(saved_file, index_col=0)


def __init__(self, start, horizon, period, reg_control=True):
    self.start = start
    self.horizon = horizon  # minutes
    self.period = period  # minutes
    self.end = self.start + timedelta(minutes=horizon)
    self.reg_control = reg_control
    self.P, self.Q = self.get_load_data()

    self.build_circuit()

    # Information Storage Variables
    self.voltage_pu = pd.DataFrame(index=dss.Circuit.AllNodeNames())
    self._taps_dict = defaultdict(dict)
    self._wdg_dict = defaultdict(dict)

    self._summary_dict = dict()
    self._overload_dict = dict()
    self._capacity_dict = dict()
    self._currents_dict = dict()
    self._profile_dict = dict()

def build_circuit(self):
    """ Set up the IEEE13 test circuit in OpenDSS. """
    dss.run_command("Clear")

    # Initiate a new circuit called "13_node_test_system"
    dss.run_command('Redirect "/Users/saki/cosimul/co_sim_platform/SmartGridMain/OpenDSS-wrapper-main/examples/acnportal-experiments-master/examples/3-Grid-Impacts/3.2-Iowa-Feeder-with-EV-and-Solar-OpenDSS/IEEE13_dist_feeder/IEEE13Nodeckt.dss"')
    if self.reg_control:
        dss.run_command(f"Redirect {CIRCUIT_DIR}/REG_Control_13.dss")
    dss.run_command(f"Redirect {CIRCUIT_DIR}/Linecode.dss")
    dss.run_command("New EnergyMeter.FeederB Load.671  1")
    # dss.run_command("CalcVoltageBases")

def step_loads(self, t):
    """ Update loads within the OpenDSS model using the dataframes P and Q. """
    for load_name in dss.utils.Iterator(dss.Loads, "Name"):
        name = load_name()
        if name in self.P:
            dss.Loads.kW(dss.Loads.kW() + self.P[name][t])
        else:
            dss.Loads.kW(0)

        if name in self.Q:
            dss.Loads.kvar(dss.Loads.kvar() + self.Q[name][t])
        else:
            dss.Loads.kvar(0)
    print(dss.Loads.kW)
    print(dss.Loads.kvar)


def store_voltages(self, time):
        """ Store per unit voltage for each node. """
        names = []
        volts = []
        for name in dss.Circuit.AllBusNames():
            # Set the Active bus
            dss.Circuit.SetActiveBus(name)
            # Compute the voltage
            voltages = [
                abs(complex(i[0], i[1])) for i in zip(*[iter(dss.Bus.PuVoltage())] * 2)
            ]
            for i, node in enumerate(dss.Bus.Nodes()):
                names.append(f"{name}.{node}")
                volts.append(voltages[i])
        self.voltage_pu[time] = pd.Series(volts, names)


def store_transformer_info(self, time):
    """ Store winding and tap position for transformer. """
    for name in dss.utils.Iterator(dss.Transformers, "Name"):
        if name() in set(f"sub_regulator_{p}" for p in "abc"):
            self._taps_dict[time][name()] = dss.Transformers.Tap()
            self._wdg_dict[time][name()] = dss.Transformers.Wdg()



def run(self, detailed_metrics=True):
        """ Run the experiment. """
        steps = self.horizon // self.period
        for t in tqdm(range(steps)):
            self.build_circuit()
            self.step_loads(t)
            dss.run_command("Solve")
            time = self.P.index[t]
            self.store_voltages(time)
            self.store_transformer_info(time)
            if detailed_metrics:
                self._summary_dict[time] = export_to_df("summary")
                self._overload_dict[time] = export_to_df("overload")
                self._capacity_dict[time] = export_to_df("capacity")
                self._currents_dict[time] = export_to_df("currents")
                self._profile_dict[time] = export_to_df("profile")


def run_dss(self, detailed_metrics=True):
        """ Run the OpenDSS experiment. """
        self.open_dss_experiment.run(detailed_metrics=detailed_metrics)


def plot_dss_voltages(self, ax=None, legend=False, title=None):
    """ Plot maximum and minimum voltage in the distribution feeder. """
    self.open_dss_experiment.plot_voltage(ax=ax, legend=legend, title=title)


