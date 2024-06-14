from ..header import HeaderGenerator
from plyfile import PlyData
from pathlib import Path
import numpy as np
import numpy.lib.recfunctions as np_rf
import json
import pandas
from ...logger import RailTwinLogger

# connect to logging system
logger = RailTwinLogger.create()


def read_ply(input_path: Path):
    point_header = HeaderGenerator()
    point_cloud_ply = PlyData.read(input_path)
    scale = np.ones(3)
    offset = np.zeros(3)
    metadata = {}
    class_mapping = {}

    for i, ele in enumerate(point_cloud_ply.elements):
        if ele.name in ["vertex", "points", "point", "vertices"]:
            indexer = []
            point_header.index = i
            for col_name in ele.data.dtype.names:
                if col_name.lower() in point_header.possible_properties():
                    point_header.add(col_name)
                    indexer.append(True)
                else:
                    indexer.append(False)

        if ele.name in ["shift", "offset"]:
            metadata["offset"] = ele.data
            metadata["original_offset_name"] = ele.name
        # else:
        #     metadata["offset"] = np.array([(4209.16699219, 8317.51757812, 160.86159516)], dtype=[('x', '<f8'), ('y', '<f8'), ('z', '<f8')])

    if any([c.find("dialect=tum_ply") > -1 for c in point_cloud_ply.comments]):
        for comment in point_cloud_ply.comments:
            if comment.startswith("metadata:"):
                metadata_update = json.loads(comment[9:])
                if "offset" in metadata_update:
                    if type(metadata_update["offset"]) is list:
                        try:
                            _f = np.array(metadata_update["offset"]).flatten()[:3]
                            metadata_update["offset"] = np.array(tuple(_f), dtype=np.dtype([('x', '<f8'), ('y', '<f8'), ('z', '<f8')]))
                        except Exception as e:
                            raise e
                            raise ValueError("Offset format is not readable")

                    if "offset" in metadata:
                        if type(metadata_update["offset"]) is np.ndarray:
                            if np.linalg.norm(metadata["offset"].view((float, (3,))) - metadata_update['offset'].view((float, (3,)))) < 0.01:
                                logger.info("Metadata was defined twice. Discarding json offset")
                            else:
                                logger.warn(f"Two definitions of were defined. The datatype take priority over json: {metadata_update['offset']}")
                                metadata_update["I0"] = metadata_update["offset"]
                            del metadata_update["offset"]

                metadata.update(metadata_update)
            elif comment.startswith("categories:"):
                class_mapping = json.loads(comment[11:])

    # Points are needed we create df first
    series = {}
    for ply_name, internal_name, in point_header.mapping.items():
        internal_type = point_header.header[internal_name].type
        series[internal_name] = pandas.Series(point_cloud_ply.elements[point_header.index].data[ply_name], dtype=internal_type)
    point_cloud = pandas.DataFrame(series)
    del series

    # Exceptions
    if metadata:
        point_cloud.attrs["metadata"] = metadata

    if class_mapping:
        point_cloud.attrs["categories"] = class_mapping
        point_cloud["class"].cat.rename_categories(class_mapping)
    return point_cloud