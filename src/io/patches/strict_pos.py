# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pandas as pd


def ensure_strict_pos(arr: np.array, delta=1e-12):
    _arr = pd.Series(arr)
    perp = {pos: index for pos, index in _arr.groupby(_arr).groups.items() if len(index) > 1}
    for pos, index in perp.items():
        for n, i in enumerate(index):
            _arr[i] += n * delta

    arr[:] = _arr.to_numpy()
    return arr
