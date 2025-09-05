@echo off
echo Cleaning up virtual environment...
if exist flask_env rmdir /s /q flask_env
if exist venv rmdir /s /q venv
if exist env rmdir /s /q env
echo Cleanup complete!
