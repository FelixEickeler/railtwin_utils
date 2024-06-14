# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#

#     "X": np.dtype("i4"),
#     "Y": np.dtype("i4"),
#     "Z": np.dtype("i4"),
#     "intensity": np.dtype("u2"),
#     "bit_fields": np.dtype("u1"),
#     "raw_classification": np.dtype("u1"),
#     "scan_angle_rank": np.dtype("i1"),
#     "user_data": np.dtype("u1"),
#     "point_source_id": np.dtype("u2"),
#     "gps_time": np.dtype("f8"),
#     "red": np.dtype("u2"),
#     "green": np.dtype("u2"),
#     "blue": np.dtype("u2"),
#     # Waveform related dimensions
#     "wavepacket_index": np.dtype("u1"),
#     "wavepacket_offset": np.dtype("u8"),
#     "wavepacket_size": np.dtype("u4"),
#     "return_point_wave_location": np.dtype("f4"),
#     "x_t": np.dtype("f4"),
#     "y_t": np.dtype("f4"),
#     "z_t": np.dtype("f4"),
#     # Las 1.4
#     "classification_flags": np.dtype("u1"),
#     "scan_angle": np.dtype("i2"),
#     "classification": np.dtype("u1"),
#     "nir": np.dtype("u2"),



helios_format = (
    "X",
    "Y",
    "Z",
    "intensity",
    "echoWidth",
    "returnNumber",
    "numberOfReturns",
    "fullwaveIndex",
    "hitObjectId",
    "class"
    "time"
)