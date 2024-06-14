import pandas
from pathlib import Path
# from src.io.formats import BasePCSFormat

#
# def create_csv_reader(pcs_format: BasePCSFormat, row_skip=0, delimiter=r"\s+"):
#     def read_xyz(src: Path):
#         data = pandas.read_csv(src, header=None,
#                                names=pcs_format.cols(),
#                                dtype=pcs_format.dtype(),
#                                delimiter=delimiter,
#                                skiprows=row_skip)
#         return data
#
#     return read_xyz
