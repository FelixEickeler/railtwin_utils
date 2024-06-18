# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from typing import Mapping, Iterable, Dict, List

import laspy
import numpy as np
import pandas as pd
from laspy import PointFormat
from laspy.point import dims, format
from laspy.point.dims import SubField
from logging import getLogger

logger = getLogger("RailtwinUtils")


# noinspection PyMissingConstructor
class CustomPointFormat(format.PointFormat):
    FMT_TRACKER = {}

    def __init__(self, point_format_id: int):
        self.id: int = point_format_id
        self.dimensions: List[dims.DimensionInfo] = []

        fmt = self.FMT_TRACKER.get(point_format_id)
        for name, _dtype in fmt.items():
            try:
                sub_fields = dims.COMPOSED_FIELDS[point_format_id][name]
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

    @staticmethod
    def as_dataframe(source_point_record: "PackedPointRecord", high_accuracy) -> pd.DataFrame:
        """
        Convert a PackedPointRecord to a pandas DataFrame
        """
        data = {}
        for dim in source_point_record.dimensions:
            data[dim.name] = dim.unpack(source_point_record)


        return pd.DataFrame(source_point_record.memoryview())

    @staticmethod
    def from_dataframe(data: pd.DataFrame, xyz_f8: bool = True) -> "PackedPointRecord":
        """
        Convert a pandas DataFrame to a PackedPointRecord
        """
        point_format, mapping = CustomPointFormat.select_point_format(list(data.columns))
        point_record = point_format.zeros(len(data))
        for dim_name, dim in mapping.items():
            point_record[dim] = data[dim_name].values
        return point_record

    @staticmethod
    def select_point_format(dimension_names: Iterable[str]) -> PointFormat:
        voting = {existing_format: 0 for existing_format in dims.ALL_POINT_FORMATS_DIMENSIONS}
        mapping = {}
        for record_id in voting:
            mapping[record_id] = {dim.lower(): dim for dim in PointFormat(record_id).dimension_names}
        this_mapping = {}

        for dim_name in dimension_names:
            for record_id in voting:
                if dim_name.lower() in mapping[record_id]:
                    if record_id not in this_mapping:
                        this_mapping[record_id] = {}
                    this_mapping[record_id][dim_name] = mapping[record_id][dim_name.lower()]
                    voting[record_id] += 1

        best_match_value = max(voting.values())
        best_record_types = [record_id for record_id in voting if voting[record_id] == best_match_value]
        best_record_id = min(best_record_types, key=lambda k: dims.ALL_POINT_FORMATS_DTYPE[k].itemsize)

        diff = set(dimension_names) - set(this_mapping[best_record_id].keys())
        if diff:
            logger.warning(f"Missing dimensions: {diff}")
        return PointFormat(best_record_id), this_mapping[best_record_id]

    def get_format_mapping(self, dimension_names: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for dim_name in dimension_names:
            for dim in self.dimensions:
                if dim.name.lower() == dim_name.lower():
                    mapping[dim_name] = dim.name
        return mapping


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

            dtype = select_width(key, start_bit)
            _dtypes += [(key, dtype)]

        else:
            if not isinstance(dtype, np.dtype):
                raise ValueError(f"Expected np.dtype, got {type(dtype)}")

            _dtypes += [(key, dtype)]

    return np.dtype(_dtypes), _composed_fields


def select_width(text_ref, start_bit):
    if start_bit <= 8:
        dtype = np.dtype("u1")
    elif start_bit <= 16:
        dtype = np.dtype("u2")
    elif start_bit <= 32:
        dtype = np.dtype("u4")
    elif start_bit <= 64:
        dtype = np.dtype("u8")
    else:
        raise ValueError(f"Bit width exceeds 64 bits for field {text_ref}")
    return dtype


def patch_laspy_types(custom_formats, overwrite: bool = False):
    fmt_versioning = []
    if "CUSTOM" in dims.VERSION_TO_POINT_FMT:
        fmt_versioning = list(dims.VERSION_TO_POINT_FMT["CUSTOM"])

        for record_id, format_definition in custom_formats.items():
            _dimensions_names = list(format_definition.keys())
            _point_format, _composed_fields = _build_custom_types(format_definition)

            if record_id in dims.POINT_FORMAT_DIMENSIONS and not overwrite:
                raise ValueError(f"Point format {record_id} already exists")

            dims.ALL_POINT_FORMATS_DIMENSIONS[record_id] = _dimensions_names
            dims.ALL_POINT_FORMATS_DTYPE[record_id] = _point_format
            dims.COMPOSED_FIELDS[record_id] = _composed_fields
            fmt_versioning += [record_id]
            CustomPointFormat.register_fmt(record_id, format_definition)
    dims.VERSION_TO_POINT_FMT["CUSTOM"] = tuple(fmt_versioning)
