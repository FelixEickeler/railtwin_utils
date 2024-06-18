from pathlib import Path

from src.io.formats.patch_laspy import claspy


def read_las(input_path: Path, ):
    las_file = claspy.read(input_path.as_posix())


