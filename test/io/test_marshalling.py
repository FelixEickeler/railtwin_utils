# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pandas as pd

from src.io.marshalling.dict_codec import DictCodec
from src.io.marshalling.numpy_codec import NumpyCodec
from src.io.marshalling.pandas_codec import PandasCodec
from src.io.marshalling.spine2d_codec import Spline2DCodec
from src.io.marshalling.spinexd_codec import SplineXDCodec
from src.model.spline_2d import Spline2D
from src.model.spline_xd import SplineXD

def helper_serialize(serializer):
    path = next(serializer)
    try:
        while path:
            with open(path, "wb") as f:
                path = serializer.send(f)
    except StopIteration:
        f.close()


def helper_deserialize(deserializer):
    try:
        resp = next(deserializer)
        while True:
            with open(resp, "rb") as f:
                resp = deserializer.send(f)
    except (TypeError, StopIteration):
        return resp
    return resp


def test_dict_roundtrip(tmp_path):
    data = {
        "a": 1,
        "b": 2,
        "c": 3,
    }
    path = tmp_path / "data"

    codec = DictCodec(handle=path)
    helper_serialize(codec.encode(data))
    result = helper_deserialize(codec.decode())
    assert data == result


def test_numpy_roundtrip(tmp_path):
    data = np.random.rand(10, 10)
    path = tmp_path / "data.npy"

    codec = NumpyCodec(handle=path)
    helper_serialize(codec.encode(data))
    result = helper_deserialize(codec.decode())

    np.testing.assert_array_equal(data, result)


def test_pandas_roundtrip(tmp_path):
    _data = {
        "a": np.random.rand(10).astype(np.float64),
        "b": (np.random.rand(10) * 10).astype(np.int64),
        "c": (np.random.rand(10) * 100).astype(np.int16),
    }

    _metadata = {
        "a": "float64",
        "b": "int64",
        "c": "int16",
    }
    data = pd.DataFrame(_data)
    data.attrs["metadata"] = _metadata

    path = tmp_path / "data.feather"
    codec = PandasCodec(handle=path)
    helper_serialize(codec.encode(data))
    result = helper_deserialize(codec.decode())

    for col in data.columns:
        np.testing.assert_array_equal(data[col], result[col])

    assert data.attrs["metadata"] == result.attrs["metadata"]


def test_spline2D_roundtrip(tmp_path):
    data = Spline2D.build(np.linspace(0, 1, 10), np.random.rand(10))
    path = tmp_path / "spline2d"
    codec = Spline2DCodec(handle=path)
    helper_serialize(codec.encode(data))
    result = helper_deserialize(codec.decode())

    assert data.mse_error == result.mse_error
    assert data.max_error == result.max_error
    assert data.requested_mse_threshold == result.requested_mse_threshold
    assert data.requested_error_threshold == result.requested_error_threshold
    assert data._spline.k == result._spline.k
    np.testing.assert_array_equal(data._spline.t, result._spline.t)
    np.testing.assert_array_equal(data._spline.c, result._spline.c)


def test_splineXD_roundtrip(tmp_path):
    data = SplineXD.build(
        np.linspace(0, 1, 10),
        np.random.rand(10, 3),
        3
    )
    path = tmp_path / "spline3d"
    codec = SplineXDCodec(handle=path)
    helper_serialize(codec.encode(data))
    result = helper_deserialize(codec.decode())

    assert data.mse_error == result.mse_error
    assert data.max_error == result.max_error
    assert data.requested_mse_threshold == result.requested_mse_threshold
    assert data.requested_error_threshold == result.requested_error_threshold

    np.testing.assert_array_equal(data.tck[0], result.tck[0])
    np.testing.assert_array_equal(data.tck[1], result.tck[1])
    assert data.tck[2] == result.tck[2]

