cd conda
call create_env.bat
call add_paths.bat
call conda activate antecedent_moisture_model-prod
cd ..
pip install -e .