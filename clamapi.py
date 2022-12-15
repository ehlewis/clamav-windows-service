import clamd
import os
from fastapi import FastAPI,File, UploadFile
import random
import string
import time
import logging
import logging.handlers
from datetime import datetime

log_file_path='C:/Program Files/ClamAV/clamapi.log'
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(log_file_path)
logger.addHandler(handler)
logtime = datetime.now().strftime("%m/%d/%Y %H:%M:%S:")

logger.info(logtime + " Attempting to start server")
app = FastAPI()
logger.info(logtime + " Server started")

try:
    logger.info(logtime + " Connecting to CLAMD deamon")
    clamav = clamd.ClamdNetworkSocket()
    print(clamav.ping())
    print(clamav.version())
    logger.info(logtime + " Connected to CLAMD deamon")
except Exception as e:
    logger.exception(logtime + " Unable to connect to CLAMD")

@app.get("/healthcheck")
def healthcheck(ping=None):
    if ping == None:
        return {"healthy"}
    return {ping}


@app.get("/clamav-ping")
def clamav_ping():
    return {clamav.ping()} 

@app.get("/clamav-version")
def clamav_version():
    return {clamav.version()} 

@app.post("/scan-file")
def scan_file(file: UploadFile = File(...)):
    logger.info(logtime + " File received for scan...")
    t0= time.time()
    temp_filename = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits , k=15))
    save_file = r"C:\\temp\\" + temp_filename
    print(file.filename + " : " + temp_filename)
    logger.info("Accepted file to scan: " + file.filename + " : " + temp_filename)
    try:
        contents = file.file.read()

        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        with open(save_file, 'wb') as f:
            f.write(contents)
        print("File: " + file.filename + " aka " + save_file + " written.")
    except Exception as e:
        logger.exception(logtime + " Unable to write file to disk")
        print(e)
        return {"message": e }
        
    finally:
        file.file.close()
        
    try:
        scan_results = clamav.scan(save_file)
        clean_result = scan_results.values()
        print("File: " + file.filename + " aka " + save_file + " scanned.")
        print(scan_results)
    except Exception as e:
        logger.exception(logtime + " Unable to scan file with CLAMD")
        print(e)
        return {"message": "There was an error scanning the file " + e }
    finally:
        os.remove(save_file)
        print("File: " + save_file + " removed")
    t1=time.time()
    print(t1-t0)
    logger.info(logtime + " Returned scan status in " + str(t1-t0) + " seconds")
    logger.info(scan_results)
    return {"result": clean_result}

'''
clamav = clamd.ClamdNetworkSocket()
print(clamav.ping())
print(clamav.version())
print(clamav.scan(r"clamapi.py"))
'''