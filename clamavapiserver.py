import uvicorn
from multiprocessing import cpu_count, freeze_support
import clamd
import os
import logging
import logging.handlers

log_file_path='C:/Program Files/ClamAV/clamavapiserver.log'
logger = logging.getLogger("ServerLogger")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(log_file_path)
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
    logger.info("Freezing support")
    freeze_support()  # Needed for pyinstaller for multiprocessing on WindowsOS
    logger.info("Support frozen")
    num_workers = int(cpu_count() * 0.75)
    
    start_server(num_workers=num_workers)
