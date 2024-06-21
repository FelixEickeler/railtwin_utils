# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import json
from os import path
from pathlib import Path
from typing import Any, IO

import numpy as np

from src.io.marshalling.base_codec import BaseCodec


# noinspection PyAttributeOutsideInit,PyTypeChecker
class NumpyCodec(BaseCodec):

    def setup(self, *args, **kwargs):
        self.suffix = kwargs.get("suffix", ".np")

    def check_preconditions(self, data: Any):
        assert isinstance(data, np.ndarray), "Data must be a numpy array."
        return True

    def encode_impl(self, data):
        flo: IO = yield self.handle.with_suffix(self.suffix)
        np.save(flo, data)

    def decode_impl(self):
        flo: IO = yield self.handle.with_suffix(self.suffix)
        obj = np.load(flo)
        self.check_preconditions(obj)
        yield obj
