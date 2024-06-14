# 14/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#

from src.io.formats.format_patches import custom_point_formats
from src.io.formats.monkey_patch_laspy import CustomPointFormat, patch_laspy_types
patch_laspy_types(custom_point_formats)
import laspy as claspy  # noqa: E402
claspy.PointFormat = CustomPointFormat
