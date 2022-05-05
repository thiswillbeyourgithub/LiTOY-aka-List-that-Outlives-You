#!/usr/bin/env python3.9
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import sys
import time
from tqdm import tqdm

def create_logger():
    """
    initializes the logger at startup
    source:
    https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    """
    Path("../.. /logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO,
                        filename='logs/rotating_log',
                        filemode='a',
                        format='')
    handler = RotatingFileHandler("logs/rotating_log",
                                  maxBytes=20*1024*1024,
                                  backupCount=20)
    log = logging.getLogger()
    log.handlers.pop()  # otherwise all lines are duplicated
    log.addHandler(handler)
    return log
log = create_logger()


def log_(string, onlyLogging=True):
    """
    Append string to the logging file, if onlyLogging=False then
    will also print to user using tqdm.write
    """
    caller_name = str(sys._getframe().f_back.f_code.co_name)
    if not caller_name.startswith("<"):
        prefix = f"{caller_name}: "
    else:
        prefix = ""
    log.info(f"{time.asctime()}: {prefix}{string}")
    if onlyLogging is False: # or args["verbose"] is True:
        tqdm.write(string)



