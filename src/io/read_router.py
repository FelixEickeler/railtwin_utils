from pathlib import Path

from src.io.reader.las import read_las
from .reader.ply import read_ply
from ..logger.railtwinlogger import RailTwinLogger

logger = RailTwinLogger.create()

# register here (or in code somewhere)
registered_reader = {".las": read_laz, ".laz": read_laz, ".ply": read_ply, ".feather": read_feather}


def read_file(input_path: Path):
    """
    Will read a point cloud and the metadata of a supported format. The formats that are supported are (or must be) added to registered_reader
    :param input_path
    :return:
    """
    if not input_path.exists():
        raise FileNotFoundError("The provided input file, does not exists")
    filetype = input_path.suffix.lower()
    if filetype in registered_reader:
        xyz = registered_reader[filetype](input_path)
    else:
        raise NotImplementedError("This filetype is not supported !")
    return xyz


def scandir_supported(src: Path):
    return [f for f in src.glob("**/*") if f.suffix in registered_reader]