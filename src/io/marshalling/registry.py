# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pandas as pd

from src.model.spline_2d import Spline2D
from src.model.spline_xd import SplineXD
from src.io.marshalling.dict_codec import DictCodec
from src.io.marshalling.numpy_codec import NumpyCodec
from src.io.marshalling.pandas_codec import PandasCodec
from src.io.marshalling.spine2d_codec import Spline2DCodec
from src.io.marshalling.spinexd_codec import SplineXDCodec

serialization_registry = {
    dict: DictCodec,
    np.ndarray: NumpyCodec,
    pd.DataFrame: PandasCodec,
    Spline2D: Spline2DCodec,
    SplineXD: SplineXDCodec,
}