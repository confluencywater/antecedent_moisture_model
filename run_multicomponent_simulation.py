from pathlib import Path

from antecedent_moisture_model.antecedent_moisture_model import (
    run_multicomponent_antecedent_moisture_model,
)

input_path = Path("data/noisy_example")
mcamm = run_multicomponent_antecedent_moisture_model(
    input_path,
    figure_filename="results.png",
    export_filename="results.csv",
)
