# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from typing import Any, IO

import numpy as np

from src.io.marshalling.base_codec import BaseCodec
from src.io.marshalling.dict_codec import DictCodec
from src.io.marshalling.numpy_codec import NumpyCodec
from src.model.spline_xd import SplineXD


# noinspection PyAttributeOutsideInit,PyTypeChecker
class SplineXDCodec(BaseCodec):

    def setup(self, *args, **kwargs):
        self.t_suffix = kwargs.get("t_suffix", ".npt")
        self.c_suffix = kwargs.get("c_suffix", ".npc")
        self.metadata_suffix = kwargs.get("metadata_suffix", ".metadata")

    def check_preconditions(self, data: Any):
        assert isinstance(data, SplineXD), "Data must be a SplineXD object."
        return True

    def encode_impl(self, data):
        dict_encoder = DictCodec(self.handle, suffix=".metadata").encode({
            "count": len(data.tck[0]),
            "mse_error": data.mse_error,
            "max_error": data.max_error,
            "requested_mse_threshold": data.requested_mse_threshold,
            "requested_error_threshold": data.requested_error_threshold,
            "degree_of_fit": data.tck[2],
        })
        yield from dict_encoder
        t_encoder = NumpyCodec(self.handle, suffix=".npt").encode(data.tck[0])
        yield from t_encoder
        c_encoder = NumpyCodec(self.handle, suffix=".npc").encode(np.array(data.tck[1]))
        yield from c_encoder

    def decode_impl(self):
        json_decoder = DictCodec(self.handle, suffix=".metadata").decode()
        flo: IO = yield next(json_decoder)
        _dict = json_decoder.send(flo)

        t_encoder = NumpyCodec(self.handle, suffix=".npt").decode()
        flo: IO = yield next(t_encoder)
        _t = t_encoder.send(flo)
        c_encoder = NumpyCodec(self.handle, suffix=".npc").decode()
        flo: IO = yield next(c_encoder)
        _c = c_encoder.send(flo)
        spline2d = SplineXD((_t, _c, _dict["degree_of_fit"]),
                            mse=_dict["mse_error"],
                            max_error=_dict["max_error"],
                            mse_threshold=_dict["requested_mse_threshold"],
                            error_threshold=_dict["requested_error_threshold"])

        self.check_preconditions(spline2d)
        yield spline2d

        # flo: IO = yield self.handle.with_suffix(self.main_suffix)
        # _dataframe = pd.read_feather(flo)
        # dict_decoder = DictCodec(self.handle, suffix=".metadata").decode()
        # flo: IO = yield next(dict_decoder)
        # _dict = dict_decoder.send(flo)
        # _dataframe.attrs = _dict
        # self.check_preconditions(_dataframe)
        # yield _dataframe
