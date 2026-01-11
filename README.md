# Smart Grid Co-Simulation: Distribution State Estimation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mosaik](https://img.shields.io/badge/Mosaik-3.0-green.svg)](https://mosaik.offis.de/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A smart grid co-simulation platform integrating power flow analysis, communication networks, and Distribution State Estimation (DSE) using the Mosaik framework.

## Acknowledgments

This project is based on the co-simulation platform developed by the **Sustainable Computing Research Group** at the University of Alberta:

> **Co-Simulation Platform**  
> https://github.com/sustainable-computing/co_sim_platform
>
> Original authors: Evandro de Souza, Amrinder S. Grewal  
> University of Alberta - Computing Science


## Caveat
This project was undertaken to understand the concept of cosimulation between several systems and the author claims no original knowledge of the ideas in this project. This project is currently unfinished and paused.

## Overview

This platform enables:
- **Power Flow Simulation** via OpenDSS
- **Communication Network Simulation** via NS-3
- **Distribution State Estimation** using Weighted Least Squares (WLS)
- **Coordinated Simulation** via Mosaik framework





### Scenarios

1. **Tap Control (Scenario 1)**: Voltage regulation via transformer tap control
2. **State Estimation (Scenario 2)**: WLS-based distribution state estimation with PMU and smart meter measurements

## Project Structure

```
cosim-dse/
├── README.md
├── requirements.txt
├── LICENSE
│
├── src/
│   ├── simulator_demo_mine.py    # Main Mosaik orchestration script
│   └── simulator_dse_saki.py     # Distribution State Estimation module
│
└── data/
    ├── IEEE13/                   # IEEE 13-bus test feeder files
    └── SIMDSE_IEEE13/            # DSE configuration files
```

## Dependencies

### Python Packages
```
mosaik>=3.0
mosaik-api>=3.0
numpy
pandas
scipy
dss-python
```

### External Software
- **NS-3** (v3.33): Network simulator for communication delays
- **OpenDSS**: Power flow solver

### Required Files from Original Repository

You need the following files from [co_sim_platform](https://github.com/sustainable-computing/co_sim_platform):

#### Python Simulators (place in `src/`)
| File | Description |
|------|-------------|
| `simulator_pflow_3.py` | Power flow simulator (OpenDSS wrapper) |
| `simulator_collector_3.py` | Data collection and monitoring |
| `simulator_controltap_3.py` | Tap control simulator |

#### Data Files for IEEE 13-Bus (place in `data/IEEE13/`)
| File | Description |
|------|-------------|
| `outfile.dss` | OpenDSS network topology |
| `IEEE13Nodeckt_NodeWithLoad.csv` | Nodes with load data |
| `IEEE13Nodeckt_InelasticLoadPQ.csv` | Load P/Q values |
| `IEEE13_Devices.csv` | Device configuration |
| `gen_nodes.json` | NS-3 network configuration |

#### Data Files for DSE (place in `data/SIMDSE_IEEE13/`)
| File | Description |
|------|-------------|
| `outfile2.dss` | OpenDSS network for DSE |
| `IEEE13Nodeckt_NodeWithLoad.csv` | Node/load mapping |
| `IEEE13Nodeckt_InelasticLoadPQ.csv` | Load values |
| `IEEE13_Devices1.csv` | Device configuration for DSE |
| `IEEE13ymatnew.npy` | Admittance matrix |
| `loadPseudo133.mat` | Pseudo load data |

## Installation

1. **Clone this repository**:
```bash
git clone https://github.com/SJW112/cosim-dse.git
cd cosim-dse
```

2. **Clone the original co_sim_platform** (for dependent files):
```bash
git clone https://github.com/sustainable-computing/co_sim_platform.git
```

3. **Copy required files** from co_sim_platform to this project:
```bash
# Copy simulator files
cp co_sim_platform/MosaikSim/simulator_pflow_3.py src/
cp co_sim_platform/MosaikSim/simulator_collector_3.py src/
cp co_sim_platform/MosaikSim/simulator_controltap_3.py src/

# Copy data files
cp -r co_sim_platform/SmartGridMain/IEEE13/* data/IEEE13/
cp -r co_sim_platform/SmartGridMain/SIMDSE_IEEE13/* data/SIMDSE_IEEE13/
```

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

5. **Install NS-3** (optional, for communication simulation):
   - Follow instructions at https://www.nsnam.org/

## Configuration

Edit `src/simulator_demo_mine.py` to set paths:

```python
# Set your base directory
BASE_DIR = "/path/to/your/project/"

# Select scenario
Scenario = 1  # 1 = Tap Control, 2 = State Estimation
```

## Usage

### Run Tap Control Scenario
```bash
cd src
python simulator_demo_mine.py
```

### Run State Estimation Scenario
```python
# Edit simulator_demo_mine.py
Scenario = 2
```
Then run:
```bash
python simulator_demo_mine.py
```

### Command Line Options
```bash
python simulator_demo_mine.py --help

# Options:
#   --json_file     NS-3 configuration file
#   --devs_file     Device connections file
#   --random_seed   NS-3 random seed
#   --influxdb      Enable InfluxDB logging
```

## State Estimation Details

The `simulator_dse_saki.py` implements WLS-based Distribution State Estimation:

### Measurements Used
- **PMU (Phasor)**: Voltage magnitude and angle
- **Smart Meters**: Active and reactive power (P, Q)
- **Current Phasors**: Line current magnitude and angle

### Algorithm
1. Collect measurements from sensors
2. Build measurement vector Z
3. Solve WLS: minimize (Z - h(x))ᵀ R⁻¹ (Z - h(x))
4. Output estimated system state

## License

MIT License - See [LICENSE](LICENSE) file.

## Citation

If you use this code, please cite:

```bibtex
@software{cosim_dse_2024,
  author = {Sakirat Wolly},
  title = {Smart Grid Co-Simulation: Distribution State Estimation},
  year = {2024},
  url = {https://github.com/SJW112/cosim-dse}
}
```

Also cite the original co-simulation platform:
```bibtex
@software{cosim_platform,
  author = {de Souza, Evandro and Grewal, Amrinder S.},
  title = {Co-Simulation Platform},
  institution = {University of Alberta},
  url = {https://github.com/sustainable-computing/co_sim_platform}
}
```

## Contact

Sakirat Wolly - McGill University, Electrical Engineering
