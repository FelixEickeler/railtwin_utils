# # 18/06/2024$ -----------------------------------------------------------------------------------------------------
# #  created by: felix
# #              felix@eickeler.com
# # ----------------------------------------------------------------------------------------------------------------
# #
#
#
# import pytest
# import numpy as np
# from src.io.formats import CustomFrame
#
#
# def test_metadata_update():
#     array = np.random.random_sample((10, 10))
#     frame = CustomFrame(array)
#
#     metadata = {
#         'key1': 'value1',
#         '__private1': 'hidden1',
#         'key2': 'value2',
#         '__private2': 'hidden2'
#     }
#
#     frame.metadata.update(metadata)
#
#     assert 'key1' in frame.metadata
#     assert frame.metadata['key1'] == 'value1'
#     assert 'key2' in frame.metadata
#     assert frame.metadata['key2'] == 'value2'
#     # assert '__private1' not in frame.metadata
#     # assert '__private2' not in frame.metadata
#
#
# def test_to_npz_and_from_npz(tmp_path):
#     # TODO this fails with bigger scope unsure why
#     array = np.random.random_sample((10, 10))
#     frame = CustomFrame(array)
#     frame.metadata['key'] = 'value'
#     frame.metadata['whatever'] = 5
#
#     output_path = (tmp_path / "test.npz").as_posix()
#     frame.to_npz(output_path)
#     loaded_frame = CustomFrame.from_npz(output_path)
#
#     assert np.array_equal(frame.values, loaded_frame.values)
#     assert loaded_frame.metadata['key'] == 'value'
#     assert loaded_frame.metadata['whatever'] == 5
#
#
# if __name__ == "__main__":
#     pytest.main()
