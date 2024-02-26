@echo off
call mamba env create -f %~dp0prod_environment.yml -n antecedent_moisture_model-prod
pause
