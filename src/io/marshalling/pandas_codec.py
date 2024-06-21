# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from typing import Any, IO

import pandas as pd

from src.io.marshalling.dict_codec import DictCodec
from src.io.marshalling.base_codec import BaseCodec


# noinspection PyAttributeOutsideInit,PyTypeChecker
class PandasCodec(BaseCodec):

    def setup(self, *args, **kwargs):
        self.main_suffix = kwargs.get("output_name", ".feather")
        self.metadata_suffix = kwargs.get("metadata_name", ".feather")

    def check_preconditions(self, data: Any):
        assert isinstance(data, pd.DataFrame), "Data must be a pandas dataframe."
        return True

    def encode_impl(self, data):
        flo: IO = yield self.handle.with_suffix(self.main_suffix)
        data.to_feather(flo)

        dict_encoder = DictCodec(self.handle, suffix=".metadata").encode(data.attrs)
        yield from dict_encoder

    def decode_impl(self):
        flo: IO = yield self.handle.with_suffix(self.main_suffix)
        _dataframe = pd.read_feather(flo)
        dict_decoder = DictCodec(self.handle, suffix=".metadata").decode()
        flo: IO = yield next(dict_decoder)
        _dict = dict_decoder.send(flo)
        _dataframe.attrs = _dict
        self.check_preconditions(_dataframe)
        yield _dataframe
