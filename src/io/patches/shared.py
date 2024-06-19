# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
from static_frame import Index

from src.io.formats.header import Header
from src.io.patches.patch_laspy import CustomPointFormat
from src.io.patches.patch_static_frame import custom_static_frame


def _from_las_to_csf(src: "PackedPointRecord") -> custom_static_frame.Frame:
    """
    Convert laspy file to CustomFrame
    """

    dst = custom_static_frame.Frame(index=Index(range(src.header.point_count)))
    header = Header.from_laspy_header(src.header)
    dst.metadata.update(header.to_dict())
    for dim_name in src.point_format.dimension_names:
        try:
            dst = dst[dim_name](custom_static_frame.Series(np.array(src[dim_name])))
        except ValueError:
            pass
    return dst


def _from_csf_to_las(src: custom_static_frame.Frame, xyz_f8: bool = True) -> "PackedPointRecord":
    point_format, mapping = CustomPointFormat.select_point_format(list(src.columns))
    point_record = point_format.zeros(len(src))

    for csf_name, las_name in mapping.items():
        point_record[las_name] = src[csf_name].values

    return point_record
