@echo off
if "" == "%1" (
    call mamba env create -f %~dp0environment.yml -n xf
) ELSE (
    call mamba env create -f %~dp0environment.yml -n %1
)

pause
