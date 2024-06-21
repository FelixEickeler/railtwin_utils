# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import json
from typing import Any, IO

from src.io.marshalling.base_codec import BaseCodec


# noinspection PyAttributeOutsideInit,PyTypeChecker
class DictCodec(BaseCodec):

    def setup(self, *args, **kwargs):
        self.suffix = kwargs.get("suffix", ".json")

    def check_preconditions(self, data: Any):
        assert isinstance(data, dict), "Data must be a dictionary."
        return True

    def encode_impl(self, data):
        flo: IO = yield self.handle.with_suffix(self.suffix)
        json_str = json.dumps(data, indent=4)
        json_bytes = json_str.encode('utf-8')
        flo.write(json_bytes)

    def decode_impl(self):
        flo: IO = yield self.handle.with_suffix(self.suffix)
        json_bytes = flo.read()
        json_str = json_bytes.decode('utf-8')
        obj = json.loads(json_str)
        self.check_preconditions(obj)
        yield obj
