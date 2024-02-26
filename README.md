antecedent_moisture_model
=========================

Python implementation of an Antecedent Moisture Model (AMM). The current implementation supports multi-component models that combine a sinusoidal diurnal wastewater flow (DWF) component with multiple AMM components targeting Baseflow or Rainfall-Derived Infiltration & Inflow (RDII).

# Installation
Follow instructions in [installation.md](docs/installation.md)

# Running antecedent_moisture_model
See [run_multicomponent_antecedent_moisture_model.py](run_multicomponent_simulation.py) for an example of how to use the AMM. This script uses the data and configuration files in [data/noisy_example](data/noisy_example/) directory. The three important input files are:

1. timeseries.csv: One year of 5-minute data for precipitation and temperature, as well as observed flows to evaluate the modeled AMM flows. 
2. input_data_config.yaml: Configuration file for input data. See the [InputDataConfig class](antecedent_moisture_model/timeseries/datamodel.py) to see a list of required and optional elements, expected datatypes, and default values.
3. simulation_config.yaml: Configuration file for the AMM simulator. This must include a list of components_to_use, a timestep and timestep units, and then the set of possible components. Each component must have a component_type which is "dwf" (diurnal wastewater flow), "baseflow", or "rdii" (rainfall-derived infiltration and inflow). Each component also has a parameterization. See the [DWFConfig class](antecedent_moisture_model/simulator/dwf.py), [AMMBaseflowConfig class](antecedent_moisture_model/simulator/amm_baseflow.py), and [AMMRDIIConfig class](antecedent_moisture_model/simulator/amm_rdii.py) for a list of required and optional parameters, expected datatypes, and default values.

More examples for running AMM can be found in [tests](tests/).

# Additional resources 
For more information on Antecedent Moisture Models, refer to the following resources:
1. [AMM Learning Library](https://h2ometrics.com/antecedent-moisture-model/): A helpful introduction to AMM with links to other resources.
2. [AMM Users Group](https://groups.google.com/u/1/g/amm-users/): A place to foster questions and discussion around AMM
3. [AMM Companion Spreadsheet](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.h2ometrics.com%2Fwp-content%2Fuploads%2FAMM-Master-Companion-Spreadsheet.xlsx&wdOrigin=BROWSELINK): A simple & clear spreadsheet implementation of the AMM equations.
4. [AMM-for-PCSWMM](https://github.com/RJNGroup/AMM-for-PCSWMM): An implementation of AMM specifically designed to interface with PCSWMM.

	
# Credits

Thanks to David Edgren (RJN Group), Robert Czachorski (OHM Advisors, H2Ometrics), and the rests of the AMM Users Group for generously sharing their AMM resources and knowledge, which were critical to the development of this package.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

