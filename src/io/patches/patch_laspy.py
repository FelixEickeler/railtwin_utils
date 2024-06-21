# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#

from src.io.formats.registry import custom_point_formats
from src.io.patches.monkey_patch_laspy import CustomPointFormat, patch_laspy_types
patch_laspy_types(custom_point_formats)
import laspy as claspy  # noqa: E402
claspy.PointFormat = CustomPointFormat
# claspy.PointFormat.FMT_TRACKER = CustomPointFormat.FMT_TRACKER
# claspy.PointFormat.__init__ = CustomPointFormat.__init__
# claspy.PointFormat.register_fmt = CustomPointFormat.register_fmt
# claspy.PointFormat.as_dataframe = CustomPointFormat.as_dataframe
# claspy.PointFormat.from_dataframe = CustomPointFormat.from_dataframe
# claspy.PointFormat.select_point_format= CustomPointFormat.select_point_format
# claspy.PointFormat.get_format_mapping = CustomPointFormat.get_format_mapping

