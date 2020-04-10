#!/bin/bash

python3 build_parameters.py --vehicle AntennaTracker


python update.py --clean --paramversioning --site antennatracker


diff ../new_params_mversion/AntennaTracker/parameters-AntennaTracker-beta-V1.1.0.rst ../old_params_mversion/AntennaTracker/parameters-AntennaTracker-beta-V1.1.0.rst
