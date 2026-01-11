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



# class_contents = dir(baseline_model)
# ['__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', 
# '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', 
# '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', 
# '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
# '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'acn_buses', 
# 'acn_experiments', 'add_acn_load', 'add_acn_loads', 'add_general_load', 
# 'add_general_loads', 'ev_load_offset', 'open_dss_experiment', 'plot_dss_voltages', 
# 'run_acn', 'run_dss', 'unbalanced']


# def plot_dss_voltages(self, ax=None, legend=False, title=None):
#     """ Plot maximum and minimum voltage in the distribution feeder. """
#     self.open_dss_experiment.plot_voltage(ax=ax, legend=legend, title=title)