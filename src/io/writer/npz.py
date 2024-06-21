# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
from typing import Any, Type, Tuple

from src.io.writer.data_container_interface import DataContainerInterface
from src.io.writer.filesystem_container import FilesystemContainer
from src.io.marshalling.registry import serialization_registry


def write_to_folder(file_path, data: Tuple[Tuple[str, Type[Any], Any]]):
    fc = FilesystemContainer(file_path)
    _write_to_structure(fc, data)


def _write_to_structure(fc: DataContainerInterface,  data: Tuple[Tuple[str, Type[Any], Any]]):

    for _rel_path, _type, _content in data:
        serializer = serialization_registry[_type]
        fc.write(_rel_path, serializer, _content)


# def write_npz(file_path, compression_level=0, **kwargs):
#     archive = ZipFile(file_path,  mode='w', compression=compression_level)
