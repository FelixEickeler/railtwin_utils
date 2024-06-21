import datetime
import re

import numpy as np
from pathlib import Path

import pandas as pd

from src.model.header import xyz, min_max
from src.io.patches.patch_laspy import claspy

delimiters = [r"\s+", ';', '\t', '|', ',', ' ']


def read_ascii(src: Path, row_skip=0, delimiter="auto", point_format="auto", dimension_names="auto", offset="auto"):
    with open(src) as f:
        header = f.readline()
        header = re.sub(r'\[.*?]', '', header)

    if delimiter == "auto":
        delimiter_counts = {delimiter: header.count(delimiter) for delimiter in delimiters}
        delimiter = max(delimiter_counts, key=delimiter_counts.get)

    if dimension_names == "auto":
        dimension_names = [i.strip() for i in header.split(delimiter)]

    if point_format == "auto":
        # noinspection PyUnresolvedReferences
        point_format, mapping = claspy.PointFormat.select_format(ident_columns)

    else:
        if isinstance(point_format, int):
            point_format = claspy.PointFormat(point_format)
        mapping = point_format.get_format_mapping(dimension_names)

    select_columns, rename_columns = zip(*[(i, dm) for i, dm in enumerate(dimension_names) if dm in mapping])
    # skip_names = [name for name in dimension_names if name not in mapping]

    input_dtypes = {}
    apply_offset_to = []
    output_dtype = {}
    for dt in point_format.dtype().descr:
        if dt[0] in ["X", "Y", "Z", "x", "y", "z"]:
            input_dtypes[dt[0]] = np.dtype("f8")
            output_dtype[dt[0]] = np.dtype(dt[1])
            apply_offset_to.append(dt[0])
        else:
            input_dtypes[dt[0]] = np.dtype(dt[1])

    data = pd.read_csv(src, skiprows=row_skip, delimiter=delimiter, names=dimension_names, dtype=input_dtypes, header=None, usecols=select_columns)

    if offset:
        if offset == "auto":
            offset = data[apply_offset_to].iloc[0]
    else:
        offset = np.zeros(len(apply_offset_to))

    data.attrs["metadata"] = {}
    data.attrs["metadata"]["offset"] = xyz(*offset)
    # noinspection SpellCheckingInspection
    mins = data[apply_offset_to].min()
    # noinspection SpellCheckingInspection
    maxs = data[apply_offset_to].max()
    data[apply_offset_to] -= offset
    diff = data.diff()
    ls = len("{:f}".format(diff[diff > 0.000001].min().min()).split(".")[1])
    data.attrs["metadata"]["scale"] = 10 ** -ls
    data.attrs["metadata"]["x_range"] = min_max(mins["X"], maxs["X"])
    data.attrs["metadata"]["y_range"] = min_max(mins["Y"], maxs["Y"])
    data.attrs["metadata"]["z_range"] = min_max(mins["Z"], maxs["Z"])
    data.attrs["metadata"]["dimension_names"] = dimension_names
    data.attrs["metadata"]["record_length"] = len(data)
    data.attrs["metadata"]["source"] = src.name
    data.attrs["metadata"]["creation_date"] = datetime.datetime.now().isoformat()
    return data
