# 18/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#

from src.io.patches.monkey_patch_static_frame import CustomFrame, custom_frame_encode, custom_to_archive, custom_frame_decode, custom_FrameAssignILoc_call
import static_frame as custom_static_frame # noqa: E402


custom_static_frame.core.archive_npy.ArchiveFrameConverter.frame_encode = staticmethod(custom_frame_encode)
custom_static_frame.core.archive_npy.ArchiveFrameConverter.to_archive = classmethod(custom_to_archive)
custom_static_frame.core.archive_npy.ArchiveFrameConverter.frame_decode = classmethod(custom_frame_decode)

custom_static_frame.FrameAssignILoc.__call__ = custom_FrameAssignILoc_call

custom_static_frame.Frame.__iter__ = CustomFrame.__iter__
custom_static_frame.Frame.to_npy = CustomFrame.to_npy
custom_static_frame.Frame.to_npz = CustomFrame.to_npz
custom_static_frame.Frame.metadata = CustomFrame.metadata
custom_static_frame.Frame.from_npy_mmap = CustomFrame.from_npy_mmap