cd conda
call create_env.bat
call conda activate antecedent_moisture_model-prod
call add_paths.bat
cd ..
pip install -e .
