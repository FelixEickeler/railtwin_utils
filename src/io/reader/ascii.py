import re

import numpy as np
from pathlib import Path

import pandas as pd

from src.io.formats import claspy

delimiters = [r"\s+", ';', '\t', '|', ',', ' ']


def read_ascii(src: Path, row_skip=0, delimiter="auto", point_format="auto", dimension_names="auto", offset="auto"):
    with open(src) as f:
        header = f.readline()
        header = re.sub(r'\[.*?\]', '', header)

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

    # data = CustomFrame.from_delimited(src,
    #                                   columns_depth=0, skip_header=row_skip, columns_select=select_columns,
    #                                   delimiter=delimiter, dtypes=input_dtypes).relabel(columns=rename_columns)

    data = pd.read_csv(src, skiprows=row_skip, delimiter=delimiter, names=dimension_names, dtype=input_dtypes, header=None, usecols=select_columns)

    if offset:
        if offset == "auto":
            offset = data[apply_offset_to].iloc[0]
    else:
        offset = csf.form_records(np.zeros(len(apply_offset_to)), columns=apply_offset_to)
    data.attrs["metadata"] = {}
    data.attrs["metadata"]["offset"] = offset
    data[apply_offset_to] -= offset

    return data
