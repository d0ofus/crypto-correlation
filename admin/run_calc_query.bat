@echo off
setlocal

:: Change the script name as necessary
set "scanner=r_sq.py"
set "query=query.py"

:: Get the batch file's drive and path
set "batch_path=%~dp0"

:: Build the full paths
set "venv_path=%batch_path%..\\.venv"
set "script_path=%batch_path%.."

:: Run the Python script in terminal
"%venv_path%\Scripts\python.exe" "%script_path%\%scanner%"
"%venv_path%\Scripts\python.exe" "%script_path%\%query%"


pause