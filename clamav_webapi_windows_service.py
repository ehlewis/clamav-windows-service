import os
import sys
from multiprocessing import freeze_support
from subprocess import Popen
import psutil
import servicemanager
import win32event
import win32service
import win32serviceutil
import socket
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

log_file_path='C:/Program Files/ClamAV/clamav_api_windows_service_' + datetime.now().strftime("%m-%d-%Y") + '_debug.log'
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def kill_proc_tree(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()


class PythonWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ClamAV Web API Server Service"  # service name
    _svc_display_name_ = "ClamAV Web API Service"  # service display name
    _svc_description_ = "This service starts up the ClamAV web API server."  # service description

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        kill_proc_tree(self.process.pid)
        self.process.terminate()
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        try:
            logger.info("Starting Popen 'call C:/Program Files/ClamAV/clamavapiserver.exe'")
            self.process = Popen('call "C:/Program Files/ClamAV/clamavapiserver.exe"', shell=True)
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            rc = win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            logger.debug("Server Popen'ed")
        except Exception as e:
            logger.exception("Unable to Popen")



if __name__ == '__main__':
    freeze_support()  # Needed for pyinstaller for multiprocessing on WindowsOS
    if len(sys.argv) == 1:
        logger.debug("Starting Service option 1")
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
        logger.debug("Service option 1 Started")
    else:
        logger.debug("Starting Service option 2")
        win32serviceutil.HandleCommandLine(PythonWindowsService)
        logger.debug("Service option 2 Started")
