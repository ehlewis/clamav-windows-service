echo Create environment if does not exist
conda env list | find /i "windows-service"
if ERRORLEVEL 1 (
call conda env create -f environment.yml)
echo Build server executable folder
call conda activate windows-service
call pyinstaller clamdapiserver.spec --noconfirm
echo Build windows_server executable folder
call pyinstaller --onefile --hidden-import win32timezone windows_service.py
echo Successfully built the windows service install folder