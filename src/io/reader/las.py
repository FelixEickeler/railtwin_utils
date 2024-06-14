from pathlib import Path
import numpy as np
from pandas import DataFrame
import laspy

from src.io.formats import BasePCSFormat

def create_las_reader(pcs_format: BasePCSFormat, row_skip=0, delimiter=r"\s+"):

    def read_las(input_path: Path):
        # logger.info("Reading points from {}".format(input_path))
        las_file = laspy.read(input_path.as_posix())


        # reconstruct points from las format scale(f8) * val(i4) + offset(f8)



        #TODO just get everything which is define in the point format, if a thing is not defined return a default value, and a log

        if las_file.point_format.id < 6:
            intensity = las_file.intensity
            return_number = las_file.return_number
            number_of_returns = las_file.number_of_returns
            scan_direction_flag = las_file.scan_direction_flag
            edge_of_flight_line = las_file.edge_of_flight_line
            classification = las_file.classification
            synthetic = las_file.synthetic
            key_point = las_file.key_point
            user_data = las_file.user_data
            point_source_id = las_file.point_source_id

            records += [intensity, return_number, number_of_returns, scan_direction_flag, edge_of_flight_line,
                       classification, synthetic, key_point, user_data, point_source_id]

            if las_file.point_format.id in {1, 3, 4, 5}:
                gps_time = las_file.gps_time
                records += [gps_time]

            if las_file.point_format.id in {2, 3, 5}:
                red = las_file.red
                green = las_file.green
                blue = las_file.blue
                records += [red, green, blue]

            if las_file.point_format.id in {4, 5}:
                wavepacket_index = las_file.wavepacket_index
                wavepacket_offset = las_file.wavepacket_offset
                wavepacket_size = las_file.wavepacket_size
                return_point_wave_location = las_file.return_point_wave_location
                x_t = las_file.x_t
                y_t = las_file.y_t
                z_t = las_file.z_t
                records += [wavepacket_index, wavepacket_offset, wavepacket_size, return_point_wave_location, x_t, y_t, z_t]

        elif 5 < las_file.point_format.id < 10:
            # based on point format 6






    if las.point_format.id < 6:
        # reconstruct points from las format scale(f8) * val(i4) + offset(f8)
        point_cloud = DataFrame.from_records(xyz, columns=header.header.keys())

        # preset offset
        # offset = records.fromarrays(las.header.offset, dtype=HeaderGenerator.offset())
        offset = las.header.offset.view(HeaderGenerator.offset())
        point_cloud.attrs["offset"] = offset

        # This will also update the offset and center the point  cloud so that min_n == -max_n
        base_options = IOOptions.only_localization()
        base_options.xyz_accuracy = np.float32
        data_augmentations(point_cloud, base_options)

        # Fill in scalar fields
        if np.unique(las.intensity).size > 1:
            point_cloud["intensity"] = _allowed_headers["intensity"].augment(las.intensity)

        # BitField 1
        tmp = TA(np.uint8, UnpackBinary(las.return_number.bit_mask)).augment(las.return_number.array)
        if np.unique(tmp).size > 1 or tmp[0] != 1 or ignore_default:
            point_cloud["return_number"] = tmp
        tmp = TA(np.uint8, UnpackBinary(las.number_of_returns.bit_mask)).augment(las.number_of_returns.array)
        if np.unique(tmp).size > 1 or tmp[0] != 1 or ignore_default:
            point_cloud["number_of_returns"] = tmp
        tmp = TA(bool, UnpackBinary(las.scan_direction_flag.bit_mask)).augment(las.scan_direction_flag.array)
        if np.unique(tmp).size > 1 or tmp[0] != 0 or ignore_default:
            point_cloud["scan_direction_flag"] = tmp
        tmp = TA(bool, UnpackBinary(las.edge_of_flight_line.bit_mask)).augment(las.edge_of_flight_line.array)
        if np.unique(tmp).size > 1 or tmp[0] != 0 or ignore_default:
            point_cloud["edge_of_flight_line"] = tmp

        # BitField 2
        tmp = TA(np.uint8, UnpackBinary(las.classification.bit_mask)).augment(las.classification.array)
        if np.unique(tmp).size > 1 or tmp[0] != 0 or ignore_default:
            point_cloud["classification"] = tmp
        tmp = TA(np.uint8, UnpackBinary(las.synthetic.bit_mask)).augment(las.synthetic.array)
        if np.unique(tmp).size > 1 or tmp[0] != 0 or ignore_default:
            point_cloud["synthetic"] = tmp
        tmp = TA(np.uint8, UnpackBinary(las.key_point.bit_mask)).augment(las.key_point.array)
        if np.unique(tmp).size > 1 or tmp[0] != 0 or ignore_default:
            point_cloud["key_point"] = tmp

        # additional f6
        if np.unique(las.user_data).size > 1:
            point_cloud["user_data"] = TA(np.float16, TrueValue()).augment(las.user_data)
        if np.unique(las.point_source_id).size > 1:
            point_cloud["point_source_id"] = TA(np.float16, TrueValue()).augment(las.point_source_id)

        if las.point_format.id >= 1:
            raise NotImplementedError("This format is present in laspy, but not implemented in this tool !")

        elif las.point_format.id > 0:
            logger.warn(f"Las format {las.point_format.id} is only supported by base attributes.")

    else:
        raise NotImplementedError("Only 0-Based las formats are supported")
    logger.info("{} points where added.".format(point_cloud.shape[0]))
    return point_cloud