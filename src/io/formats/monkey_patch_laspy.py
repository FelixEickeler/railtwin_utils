# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from typing import Mapping, Iterable, Dict

import laspy
import numpy as np
from laspy.point import dims, format
from laspy.point.dims import SubField


# noinspection PyMissingConstructor
class CustomPointFormat(format.PointFormat):
    FMT_TRACKER = {}

    def __init__(self, point_format_id: int):
        fmt = self.FMT_TRACKER.get(point_format_id)
        for name, _dtype in fmt:
            try:
                sub_fields = dims.COMPOSED_FIELDS[name]
            except KeyError:
                dimension = dims.DimensionInfo.from_dtype(
                    name, _dtype, is_standard=True
                )
                self.dimensions.append(dimension)
            else:
                for sub_field in sub_fields:
                    dimension = dims.DimensionInfo.from_bitmask(
                        sub_field.name, sub_field.mask, is_standard=True
                    )
                    self.dimensions.append(dimension)

    @classmethod
    def register_fmt(cls, point_format_id: int, point_format_def: Mapping[str, np.dtype]):
        cls.FMT_TRACKER[point_format_id] = point_format_def


def _build_custom_types(type_def: Dict[str, np.dtype]):
    _dtypes = []
    _composed_fields = {}
    for key, dtype in type_def.items():
        if isinstance(dtype, Dict):
            # this is a subfield
            sub_fields = []
            start_bit = 0
            for member_name, width in dtype.items():
                mask = (1 << width) - 1
                mask <<= start_bit
                sub_fields += [SubField(member_name, mask)]
                start_bit += width
            _composed_fields[key] = sub_fields

            if start_bit <= 8:
                dtype = np.dtype("u1")
            elif start_bit <= 16:
                dtype = np.dtype("u2")
            elif start_bit <= 32:
                dtype = np.dtype("u4")
            elif start_bit <= 64:
                dtype = np.dtype("u8")
            else:
                raise ValueError(f"Bit width exceeds 64 bits for field {key}")
            _dtypes += [(key, dtype)]

        else:
            if not isinstance(dtype, np.dtype):
                raise ValueError(f"Expected np.dtype, got {type(dtype)}")

            _dtypes += [(key, dtype)]

    return np.dtype(_dtypes), _composed_fields


def patch_laspy_types(custom_formats, overwrite: bool = False):
    fmt_versioning = []
    if "CUSTOM" in dims.VERSION_TO_POINT_FMT:
        fmt_versioning = list(dims.VERSION_TO_POINT_FMT["CUSTOM"])

        for record_id, format_defition in custom_formats:
            _dimensions_names = list(format_defition.keys())
            _point_format, _composed_fields = _build_custom_types()

            if record_id in dims.POINT_FORMAT_DIMENSIONS and not overwrite:
                raise ValueError(f"Point format {record_id} already exists")

            dims.ALL_POINT_FORMATS_DIMENSIONS[record_id] = _dimensions_names
            dims.ALL_POINT_FORMATS_DTYPE[record_id] = _point_format
            dims.COMPOSED_FIELDS[record_id] = _composed_fields
            fmt_versioning += [record_id]
            CustomPointFormat.register_fmt(record_id, format_defition)
    dims.VERSION_TO_POINT_FMT["CUSTOM"] = tuple(fmt_versioning)

