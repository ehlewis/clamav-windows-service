sc.exe delete "ClamAV Web API Server Service"
del "C:\Program Files\ClamAV\clamav_webapi_windows_service.exe"
del "C:\Program Files\ClamAV\clamavapiserver.exe"
del "C:\Program Files\ClamAV\clamav_api_windows_service.log"
del "C:\Program Files\ClamAV\clamavapiserver.log"
del "C:\Program Files\ClamAV\clamavapi.log"

rmdir /s build
rmdir /s dist