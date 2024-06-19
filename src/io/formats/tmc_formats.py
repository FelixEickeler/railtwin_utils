# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np

POINT_FORMAT_TMC = {
    "gps_time": np.dtype("f8"),
    "roll": np.dtype("f8"),
    "pitch": np.dtype("f8"),
    "yaw": np.dtype("f8"),
    "X": np.dtype("f4"),
    "Y": np.dtype("f4"),
    "Z": np.dtype("f4")
}
