# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pytest

from src.io.formats.monkey_patch_laspy import _build_custom_types


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
