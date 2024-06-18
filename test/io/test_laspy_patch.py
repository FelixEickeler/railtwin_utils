# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import laspy
import numpy as np
import pytest

from src.io.patches.monkey_patch_laspy import _build_custom_types


def test_build_custom_types():
    TEST_FORMAT = {
        "X": np.dtype("f4"),
        "Y": np.dtype("f4"),
        "Z": np.dtype("f4"),
        "FIELD": np.dtype("f8"),
        "BITFIELD": {
            "subfield1": 2,
            "subfield2": 5,
            "subfield3": 1
        },
        "BYTE": np.dtype("u1"),
    }
    # "{:03b}".format(composed["BITFIELD"][2][1])
    custom, composed = _build_custom_types(TEST_FORMAT)

    assert composed["BITFIELD"][0][1] == 3
    assert composed["BITFIELD"][1][1] == 124
    assert composed["BITFIELD"][2][1] == 128
    assert custom == np.dtype([('X', '<f4'), ('Y', '<f4'), ('Z', '<f4'), ('FIELD', '<f8'), ('BITFIELD', 'u1'), ('BYTE', 'u1')])


def test_CustomPointFormat_SelectPointFormat_CorrectSelection():
    from src.io.formats import CustomPointFormat
    point_format, mapping = CustomPointFormat.select_point_format(["x", "y", "z"])
    assert point_format.id == 0

    point_format, mapping = CustomPointFormat.select_point_format(["x", "y", "z", "intensity"])
    assert point_format.id == 0

    point_format, mapping = CustomPointFormat.select_point_format(["x", "y", "z", "red"])
    assert point_format.id == 2

    point_format, mapping = CustomPointFormat.select_point_format(["x", "y", "z", "gps_time", "red"])
    assert point_format.id == 3

    point_format, mapping = CustomPointFormat.select_point_format(["x", "y", "z", "sCannER_chaNNel", "red"])
    assert point_format.id == 7



def test_CustomPointFormat_AsDataframe():
    # tesdata as las ?
    raise NotImplementedError
def test_FromDataframe():
    # testdata as dataframe
    raise NotImplementedError
