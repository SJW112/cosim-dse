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

# from adacharge import *

import sys
sys.path.append("src/")
from importlib import reload
# noinspection PyUnresolvedReferences
import Saki_composite_experiment
reload(Saki_composite_experiment)
# noinspection PyUnresolvedReferences
from Saki_composite_experiment import ACNOpenDSSCompositeExperiment



# First, we look at the maximum and minimum voltages in the Test Feeder without any added ACNs or solar. 
# We'll try two configurations; one with transformer voltage regulation and one without. 
# We run each scenario for 24 hours, starting on September 5, 2017. 
# As data from all years is not available, the JPL ACN usage profile is from the same date in 2019, 
# and the solar usage profile is from said date in 2014. September 5th was a weekday in both 2019 and 2017.

# In the following code, we use an ACNOpenDSSCompositeExperiment class that wraps
# an OpenDSS experiment with optional additional ACN loads or solar generation
# added to the feeder. You can view the documentation for this class in the src directory.

# Set default OpenDSS experiment configs.
open_dss_experiment_config = {
    "start": datetime(2017, 9, 5),
    "horizon": 24 * 60,
    "period": 5,
    "reg_control": True,
}

open_dss_experiment_config_without_reg = {
    "start": datetime(2017, 9, 5),
    "horizon": 24 * 60,
    "period": 5,
    "reg_control": False,
}


baseline_model = ACNOpenDSSCompositeExperiment(open_dss_experiment_config)
baseline_model.run_dss()


baseline_model_no_reg = ACNOpenDSSCompositeExperiment(open_dss_experiment_config_without_reg)
baseline_model_no_reg.run_dss()


fig, ax = plt.subplots(1, 2, figsize=(16, 8), sharex=True)
baseline_model.plot_dss_voltages(ax=ax[0], legend=True, title="With regulation")
baseline_model_no_reg.plot_dss_voltages(ax=ax[1], title="Without regulation")
fig.suptitle("Baseline min/max voltages")
plt.show()

acn_base_experiment_configs = {"632c": {
    "site": "jpl",
    "start": datetime(2019, 9, 5),
    "end": datetime(2019, 9, 6),
    "alg_name": None,
    "tariff_name": "sce_tou_ev_4_march_2019",
    "external_load": baseline_model.open_dss_experiment.P[" L632c"].to_numpy(),
    "external_load_name": "load_632_20170905",
    "bus_transformer_cap": 5000,
}}


# Set ACN-Sim Experiment Algorithm.
acn_unctrl_configs = deepcopy(acn_base_experiment_configs)
for config in acn_unctrl_configs.values():
    config["alg_name"] = "unctrl"

# Build composite experiment.
unctrl_632c = ACNOpenDSSCompositeExperiment(
    open_dss_experiment_config, 
    acn_unctrl_configs,
)


# Run ACN-Sim Experiment
unctrl_632c.run_acn()

# Add EV load to the OpenDSS Experiment 
unctrl_632c.add_acn_loads()



# Run OpenDSS Experiment
unctrl_632c.run_dss(detailed_metrics=True)


plt.plot(acnsim.aggregate_current(unctrl_632c.acn_experiments['632c'].sim))
plt.show()

fig, ax = plt.subplots(figsize=(8, 8), sharex=True)
unctrl_632c.plot_dss_voltages(ax, legend=True, title="Uncontrolled with Regulation")
plt.show()

pd.concat(pd.DataFrame(val) for val in unctrl_632c.open_dss_experiment._overload_dict.values())[" %Normal"].groupby("Element").describe()



longer_open_dss_experiment_config = deepcopy(open_dss_experiment_config)
longer_open_dss_experiment_config["horizon"] *= 2
longer_baseline = ACNOpenDSSCompositeExperiment(
    longer_open_dss_experiment_config
)
longer_baseline.run_dss()

 #Set ACN-Sim Experiment Algorithm.
acn_load_flattening_configs = deepcopy(acn_base_experiment_configs)
for config in acn_load_flattening_configs.values():
    config["alg_name"] = "load_flattening"
    config["external_load"] = longer_baseline.open_dss_experiment.P[" L632c"].to_numpy()

# Build composite experiment.
load_flattening_632c = ACNOpenDSSCompositeExperiment(
    open_dss_experiment_config, 
    acn_load_flattening_configs
)


# Run ACN-Sim Experiment
load_flattening_632c.run_acn()

# Add EV load to the OpenDSS Experiment 
load_flattening_632c.add_acn_loads()


load_flattening_632c.run_dss(detailed_metrics=True)




fig, ax = plt.subplots(figsize=(8, 8), sharex=True)
plt.show()
load_flattening_632c.plot_dss_voltages(ax, legend=True, title="Load Flattening with Regulation")
plt.show()

pd.concat(pd.DataFrame(val) for val in load_flattening_632c.open_dss_experiment._overload_dict.values())[" %Normal"]


# event_queue = acnsim.EventQueue.from_json("colab_data.json")
# event_queue_new = unctrl_632c.acn_experiments["632c"].get_events()


# for event_old, event_new in zip(event_queue._queue, event_queue_new._queue):
#     for key in ['session_id', 'arrival']:
#         print(f"Key {key} for old event: {getattr(event_old[1].ev, key)} for new event: {getattr(event_new[1].ev, key)}")

### Solar Data
pv_year = 2014
pv_data = pd.read_csv("data/results_des_moines_autosized_270kWdc.csv")
pv_data["Time stamp"] = [f"{pv_year} {ts}" for ts in pv_data["Time stamp"]]
pv_data["Time stamp"] = pd.to_datetime(pv_data["Time stamp"])
pv_data = pv_data.set_index("Time stamp")
# Rescale PV generation to AC capacity, and follow consumer-perspective sign convention (negative for generation)
pv_data["AC Power | (kW)"] = -1 * pv_data["Array DC power | (kW)"] / 1.22
pv_data = pv_data.resample("5T").ffill()
trunc_gen = pv_data.loc[datetime(pv_year, 9, 5):]["AC Power | (kW)"].to_numpy()
external_load_632c = longer_baseline.open_dss_experiment.P[" L632c"].to_numpy()
external_load_and_gen_632c = external_load_632c + trunc_gen[:len(external_load_632c)]
solar_gen = trunc_gen[:len(external_load_632c)]


# Set default ACN-Sim experiment configs.
acn_solar_experiment_configs = {"632c": {
    "site": "jpl",
    "start": datetime(2019, 9, 5),
    "end": datetime(2019, 9, 6),
    "alg_name": None,
    "tariff_name": "sce_tou_ev_4_march_2019",
    "external_load": external_load_and_gen_632c,
    "external_load_name": "load_gen_632c_20170905",
    "bus_transformer_cap": 5000,
}}



# Set ACN-Sim Experiment Algorithm.
acn_solar_load_flattening_configs = deepcopy(acn_solar_experiment_configs)
for config in acn_solar_load_flattening_configs.values():
    config["alg_name"] = "load_flattening"

# Build composite experiment.
solar_load_flattening_632c = ACNOpenDSSCompositeExperiment(
    open_dss_experiment_config, 
    acn_solar_load_flattening_configs, 
)


# Run ACN-Sim Experiment
solar_load_flattening_632c.run_acn()

# Add EV load to the OpenDSS Experiment 
solar_load_flattening_632c.add_acn_loads()

# Add solar load to the OpenDSS Experiment
solar_load_flattening_632c.add_general_loads(solar_gen)


# Run OpenDSS Experiment
solar_load_flattening_632c.run_dss(detailed_metrics=True)


fig, ax = plt.subplots(figsize=(8, 8), sharex=True)
solar_load_flattening_632c.plot_dss_voltages(ax, legend=True, title="Load Flattening+Solar with Regulation")
plt.show()

pd.concat(pd.DataFrame(val) for val in solar_load_flattening_632c.open_dss_experiment._overload_dict.values())[" %Normal"]


fig, ax = plt.subplots(sharex=True)
style = {
    "linewidth": 2,
    "alpha": .85,
}
baseline_model.open_dss_experiment.voltage_pu.min().plot(**style)
unctrl_632c.open_dss_experiment.voltage_pu.min().plot(**style)
load_flattening_632c.open_dss_experiment.voltage_pu.min().plot(**style)
solar_load_flattening_632c.open_dss_experiment.voltage_pu.min().plot(**style)
ax.set_ylabel("Minimum Voltage Mag. (pu)", fontsize=10.5)
ax.legend(["Baseline", "Uncontrolled", "MPC", "MPC w/Solar"])
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.xlim((25076560.0, 25078495.0))
ax.axhline(0.95, linestyle="--", color="grey")
plt.rc('text', usetex=False)
plt.rcParams.update({'font.size': 11})
ax.grid(alpha=0.5)
ax.grid(alpha=0.5)
fig = plt.gcf()
fig.set_size_inches(6.47, 3.5)
plt.tight_layout()
plt.show()


## Let's check the energy delivered for each scenario with an ACN.


unctrl_energy_delivered = acnsim.proportion_of_energy_delivered(
    unctrl_632c.acn_experiments["632c"].sim
)
load_flattening_energy_delivered = acnsim.proportion_of_energy_delivered(
    load_flattening_632c.acn_experiments["632c"].sim
)
solar_load_flattening_energy_delivered = acnsim.proportion_of_energy_delivered(
    solar_load_flattening_632c.acn_experiments["632c"].sim
)
print(
    f"Energy delivered with Uncontrolled Charging: "
    f"{unctrl_energy_delivered}\n"
    f"Energy delivered with Load Flattening: "
    f"{load_flattening_energy_delivered}\n"
    f"Energy delivered with Load Flattening and Solar: "
    f"{solar_load_flattening_energy_delivered}\n"
)




