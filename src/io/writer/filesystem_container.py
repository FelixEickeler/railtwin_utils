# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import os.path
from pathlib import Path, PurePath

from src.io.writer.data_container_interface import DataContainerInterface


class FilesystemContainer(DataContainerInterface):

    def __init__(self, root: Path):
        root = Path(root)
        assert root.parent.exists(), f"Parent directory {root.parent} does not exist."
        assert root.suffix == "", f"Root path {root} must not have a suffix."
        root.mkdir(exist_ok=True)
        self.root = root

    def write(self, relative_path, codec, data):
        path = self.root / PurePath("./") / relative_path.lstrip("/")
        path.parent.mkdir(exist_ok=True, parents=True)
        serializer = codec(handle=path).encode(data)

        path = next(serializer)
        try:
            while path:
                with open(path, "wb") as f:
                    path = serializer.send(f)
        except StopIteration:
            f.close()


    def read(self):
        raise NotImplementedError
        # TODO this is not implement, its the code from the test implementation
        try:
            resp = next(deserializer)
            while True:
                with open(resp, "rb") as f:
                    resp = deserializer.send(f)
        except (TypeError, StopIteration):
            return resp
        return resp

    def exist(self, relative_path):
        return os.path.exists(self.root / relative_path)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
