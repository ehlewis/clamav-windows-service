import uvicorn
from multiprocessing import cpu_count, freeze_support
import clamd
import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

os.makedirs("C:/Program Files/ClamAV/logs/", exist_ok=True)
log_file_path='C:/Program Files/ClamAV/logs/clamavapiserver_' + datetime.now().strftime("%m-%d-%Y") + '.log'
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.info('clamavapiserver.py opened')

def start_server(host="0.0.0.0", port=5000, num_workers=4, loop="asyncio", reload=False):
    logger.info("Starting server with " + str(num_workers) + " workers on " + host + ":" + str(port))
    uvicorn.run("clamapi:app",
                host=host,
                port=port,
                workers=num_workers,
                loop=loop,
                reload=reload)


if __name__ == "__main__":
    logger.debug("Freezing support")
    freeze_support()  # Needed for pyinstaller for multiprocessing on WindowsOS
    logger.debug("Support frozen")
    num_workers = int(cpu_count() * 0.75)
    
    start_server(num_workers=num_workers)
