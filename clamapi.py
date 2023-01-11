import clamd
import os
from fastapi import FastAPI,File, UploadFile
import random
import string
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

os.makedirs("C:/Program Files/ClamAV/logs/", exist_ok=True)
log_file_path='C:/Program Files/ClamAV/logs/clamapi_' + datetime.now().strftime("%m-%d-%Y") + '.log'
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



logger.debug("Attempting to start server")
app = FastAPI()
logger.debug("DEBUG: Server started")

while True:
    try:
        logger.info("Attempting to connect to CLAMD deamon")
        clamav = clamd.ClamdNetworkSocket()
        print(clamav.ping())
        print(clamav.version())
        logger.info("Connected to CLAMD deamon")
        break
    except Exception as e:
        logger.exception("ERROR: Unable to connect to CLAMD. Retrying in 10 seconds...")
        time.sleep(10)

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
    logger.debug("File + " + file.filename + " received for scan...")
    t0 = time.time() # Timing scans for performance purposes in debug
    temp_filename = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits , k=15))
    save_file = r"C:\\temp\\" + temp_filename
    logger.info("Accepted file to scan: " + file.filename + " : " + temp_filename)

    # Read the file and write it to a temporary, randomly named, file on the local disk
    try:
        contents = file.file.read()

        os.makedirs(os.path.dirname(save_file), exist_ok=True)
        with open(save_file, 'wb') as f:
            f.write(contents)
        logger.debug("file: " + file.filename + " aka " + save_file + " to disk")

    except Exception as e:
        logger.exception(" Unable to write " + save_file + " to disk")
        return {"message": "Unable to write file to disk" }
        
    finally:
        file.file.close()
        
    # Try to scan the file with the ClamAV Deamon
    try:
        scan_results = clamav.scan(save_file)
        clean_result = scan_results.values()
        logger.debug("File: " + file.filename + " aka " + save_file + " scanned.")

    except Exception as e:
        logger.exception("unable to scan " + save_file + " with CLAMD")
        return {"message": "Unable to scan file with CLAMD" }
    
    finally:
        # Remove the file after scanning or failure
        os.remove(save_file)
        logger.debug("File: " + file.filename + " aka " + save_file + " removed")

    t1=time.time()
    print(t1-t0)
    logger.debug("Returned scan status in " + str(t1-t0) + " seconds")
    logger.info(scan_results)
    return {"result": clean_result}

'''
clamav = clamd.ClamdNetworkSocket()
print(clamav.ping())
print(clamav.version())
print(clamav.scan(r"clamapi.py"))
'''