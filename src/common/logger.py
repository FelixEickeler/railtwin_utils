# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import logging


class Logger(logging.Logger):
    pass


logging.setLoggerClass(Logger)


def getLogger(name: str = "RailtwinUtils") -> Logger:
    return logging.getLogger(name)
