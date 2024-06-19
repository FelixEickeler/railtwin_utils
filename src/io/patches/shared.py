# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
from src.io.patches.patch_laspy import claspy
import numpy as np
import pandas as pd
from static_frame import Index

from src.io.formats.header import Header
from src.io.patches.patch_laspy import CustomPointFormat


def _from_las_to_pandas(src: "PackedPointRecord", remove_empty=True) -> pd.DataFrame:
    """
    Convert laspy file to CustomFrame
    """

    dst = pd.DataFrame(index=Index(range(src.header.point_count)))
    header = Header.from_laspy_header(src.header)
    dst.attrs["metadata"] = header.to_dict()
    for dim_name in src.point_format.dimension_names:
        try:
            uniques = np.unique(src[dim_name]) if remove_empty else []
            if len(uniques) == 1 and dim_name.lower() not in ["x", "y", "z"] and np.isclose(np.unique(src[dim_name])[0], 0):
                continue
            dst[dim_name] = np.array(src[dim_name])
        except ValueError:
            pass
    return dst


def _from_pandas_to_las(src: pd.DataFrame, xyz_f8: bool = None) -> pd.DataFrame:
    if xyz_f8 is not None:
        raise NotImplementedError

    point_format, mapping = CustomPointFormat.select_point_format(list(src.columns))
    header = claspy.LasHeader(point_format=point_format)
    header.offsets = np.array(src.attrs["metadata"]["offset"], np.dtype("f8"))
    header.scales = np.array(src.attrs["metadata"]["scale"], np.dtype("f8"))
    header.x_min = src.attrs["metadata"]["x_range"][0]
    header.x_max = src.attrs["metadata"]["x_range"][1]
    header.y_min = src.attrs["metadata"]["y_range"][0]
    header.y_max = src.attrs["metadata"]["y_range"][1]
    header.z_min = src.attrs["metadata"]["z_range"][0]
    header.z_max = src.attrs["metadata"]["z_range"][1]
    header.file_source_id = src.attrs["metadata"]["source"]
    header.uuid = src.attrs["metadata"]["project"]
    header.creation_date = src.attrs["metadata"]["creation_date"]
    # point_record = claspy.ScaleAwarePointRecord.zeros(len(src), header=header)
    lasdata = claspy.LasData(header)

    for pandas_name, las_name in mapping.items():
        lasdata[las_name] = src[pandas_name].to_numpy()
    header.point_count = len(lasdata)

    return lasdata
