# 21/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseCodec(ABC):

    def __init__(self, handle: Path, *args, **kwargs):
        if "unsafe" in kwargs:
            self.unsafe = kwargs["unsafe"]
        else:
            self.unsafe = False
        self.handle = handle
        self.setup(*args, **kwargs)

    @abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError

    def encode(self, data: Any):
        if not self.check_preconditions(data):
            raise ValueError("Preconditions not met")
        return self.encode_impl(data)

    def decode(self):
        yield from self.decode_impl()

    @abstractmethod
    def check_preconditions(self, data: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def encode_impl(self, data):
        raise NotImplementedError

    @abstractmethod
    def decode_impl(self):
        raise NotImplementedError

    # @abstractmethod
    # def get_codec_id(self):
    #     return self.codec_id

def iter_codec(codec_func):
    yield codec_func()
