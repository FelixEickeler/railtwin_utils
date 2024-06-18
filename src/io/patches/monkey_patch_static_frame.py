# 18/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import typing_extensions as tp
from static_frame import Frame, Series
from static_frame.core.archive_npy import Archive, ArchiveIndexConverter, NPYFrameConverter, NPZFrameConverter
from static_frame.core.container_util import ContainerMap, key_to_ascending_key
from static_frame.core.exception import ErrorNPYEncode
from static_frame.core.frame import TFrameAny
from static_frame.core.index import Index
from static_frame.core.index_base import IndexBase
from static_frame.core.metadata import NPYLabel
from static_frame.core.util import JSONTranslator, TPathSpecifierOrIO, KEY_MULTIPLE_TYPES, TILocSelector
from static_frame.core.util import TPathSpecifier

if tp.TYPE_CHECKING:
    TNDArrayAny = np.ndarray[tp.Any, tp.Any]  #pragma: no cover
    TDtypeAny = np.dtype[tp.Any]  #pragma: no cover
    TOptionalArrayList = tp.Optional[tp.List[TNDArrayAny]]  #pragma: no cover
    TIndexAny = Index[tp.Any]  #pragma: no cover


def custom_frame_encode(*, archive: Archive, frame: TFrameAny, include_index: bool = True, include_columns: bool = True, consolidate_blocks: bool = False,
                        metadata: tp.Dict[str, tp.Any] = None, ) -> None:
    """
    Mostly taken from static_frame.core.archive_npy.ArchiveFrameConverter.frame_encode only added metadata switch

    :param archive:
    :param frame:
    :param include_index:
    :param include_columns:
    :param consolidate_blocks:
    :param metadata:
    """
    if metadata is None:
        metadata: tp.Dict[str, tp.Any] = {}

    # NOTE: isolate custom pre-json encoding only where needed: on `name` attributes; the name might be nested tuples, so we cannot assume that name
    # is just a string
    metadata[NPYLabel.KEY_NAMES] = [
        JSONTranslator.encode_element(frame._name),
        JSONTranslator.encode_element(frame._index._name),
        JSONTranslator.encode_element(frame._columns._name),
    ]
    # do not store Frame class as caller will determine
    metadata[NPYLabel.KEY_TYPES] = [
        frame._index.__class__.__name__,
        frame._columns.__class__.__name__,
    ]

    # store shape, index depths
    depth_index = frame._index.depth
    depth_columns = frame._columns.depth

    if consolidate_blocks:
        # NOTE: by taking iter, can avoid 2x memory in some circumstances
        block_iter = frame._blocks._reblock()
    else:
        block_iter = iter(frame._blocks._blocks)

    ArchiveIndexConverter.index_encode(
        metadata=metadata,
        archive=archive,
        index=frame._index,
        key_template_values=NPYLabel.FILE_TEMPLATE_VALUES_INDEX,
        key_types=NPYLabel.KEY_TYPES_INDEX,
        depth=depth_index,
        include=include_index,
    )
    ArchiveIndexConverter.index_encode(
        metadata=metadata,
        archive=archive,
        index=frame._columns,
        key_template_values=NPYLabel.FILE_TEMPLATE_VALUES_COLUMNS,
        key_types=NPYLabel.KEY_TYPES_COLUMNS,
        depth=depth_columns,
        include=include_columns,
    )
    i = 0
    for i, array in enumerate(block_iter, 1):
        archive.write_array(NPYLabel.FILE_TEMPLATE_BLOCKS.format(i - 1), array)

    metadata[NPYLabel.KEY_DEPTHS] = [
        i,  # block count
        depth_index,
        depth_columns]

    archive.write_metadata(metadata)


def custom_to_archive(cls, *, frame: TFrameAny, fp: TPathSpecifierOrIO, include_index: bool = True,
                      include_columns: bool = True, consolidate_blocks: bool = False, metadata=None) -> None:
    archive = cls._ARCHIVE_CLS(fp,
                               writeable=True,
                               memory_map=False,
                               )
    try:
        cls.frame_encode(
            archive=archive,
            frame=frame,
            include_index=include_index,
            include_columns=include_columns,
            consolidate_blocks=consolidate_blocks,
            metadata=metadata,
        )
    except ErrorNPYEncode:
        archive.close()
        archive.__del__()  # force cleanup
        # fp can be BytesIO in a to_npz/to_zip_npz scenario
        if not isinstance(fp, io.IOBase) and os.path.exists(fp):  # type: ignore[arg-type]
            cls._ARCHIVE_CLS.FUNC_REMOVE_FP(fp)  # type: ignore[arg-type]
        raise


def custom_frame_decode(cls, *, archive: Archive, constructor: tp.Type[TFrameAny], ) -> TFrameAny:
    from static_frame.core.type_blocks import TypeBlocks
    metadata = archive.read_metadata()
    names = metadata[NPYLabel.KEY_NAMES]

    name = JSONTranslator.decode_element(names[0])
    name_index = JSONTranslator.decode_element(names[1])
    name_columns = JSONTranslator.decode_element(names[2])

    block_count, depth_index, depth_columns = metadata[NPYLabel.KEY_DEPTHS]

    cls_index: tp.Type[IndexBase]
    cls_columns: tp.Type[IndexBase]
    cls_index, cls_columns = (ContainerMap.str_to_cls(name)
                              for name in metadata[NPYLabel.KEY_TYPES])

    index = ArchiveIndexConverter.index_decode(
        archive=archive,
        metadata=metadata,
        key_template_values=NPYLabel.FILE_TEMPLATE_VALUES_INDEX,
        key_types=NPYLabel.KEY_TYPES_INDEX,
        depth=depth_index,
        cls_index=cls_index,
        name=name_index,
    )

    # we need to align the mutability of the constructor with the Index type on the columns
    if constructor.STATIC != cls_columns.STATIC:
        if constructor.STATIC:
            cls_columns = cls_columns._IMMUTABLE_CONSTRUCTOR  #type: ignore
        else:
            cls_columns = cls_columns._MUTABLE_CONSTRUCTOR  #type: ignore

    columns = ArchiveIndexConverter.index_decode(
        archive=archive,
        metadata=metadata,
        key_template_values=NPYLabel.FILE_TEMPLATE_VALUES_COLUMNS,
        key_types=NPYLabel.KEY_TYPES_COLUMNS,
        depth=depth_columns,
        cls_index=cls_columns,
        name=name_columns,
    )

    if block_count:
        tb = TypeBlocks.from_blocks(
            archive.read_array(NPYLabel.FILE_TEMPLATE_BLOCKS.format(i))
            for i in range(block_count)
        )
    else:
        tb = TypeBlocks.from_zero_size_shape()

    f = constructor(tb,
                    own_data=True,
                    index=index,
                    own_index=False if index is None else True,
                    columns=columns,
                    own_columns=False if columns is None else True,
                    name=name,
                    )
    reserved = {v for k, v in NPYLabel.__dict__.items() if k[0] != "_"}
    f.metadata.update({k, v} for k, v in metadata.items() if k not in reserved)
    return f


def custom_FrameAssignILoc_call(self, value: tp.Any, *, fill_value: tp.Any = np.nan, ) -> TFrameAny:
    is_frame = isinstance(value, Frame)
    is_series = isinstance(value, Series)

    key: tp.Tuple[TILocSelector, TILocSelector]
    if isinstance(self.key, tuple):
        # NOTE: the iloc key's order is not relevant in assignment, and block assignment requires that column keys are ascending
        key = (self.key[0],  # type: ignore
               key_to_ascending_key(
                   self.key[1],  # type: ignore
                   self.container.shape[1]
               ))
    else:
        key = (self.key, None)

    column_only = key[0] is None
    column_is_multiple = key[1] is None or isinstance(key[1], KEY_MULTIPLE_TYPES)

    assigned: TNDArrayAny | tp.Iterable[TNDArrayAny]
    if is_series:
        assigned = self.container._reindex_other_like_iloc(value, key, is_series=is_series, is_frame=is_frame, fill_value=fill_value).values
        blocks = self.container._blocks.extract_iloc_assign_by_unit(
            key,
            assigned,
        )
    elif is_frame:
        assigned = self.container._reindex_other_like_iloc(value, key, is_series=is_series, is_frame=is_frame,
                                                           fill_value=fill_value)._blocks._blocks  # pyright: ignore
        blocks = self.container._blocks.extract_iloc_assign_by_blocks(  # pyright: ignore
            key,
            assigned,
        )
    elif (column_is_multiple
          and not column_only
          and not value.__class__ is np.ndarray
          and hasattr(value, '__len__')
          and not isinstance(value, str)
    ):
        # if column_only, we are expecting a "vertical" assignment, and use the by_unit interface
        blocks = self.container._blocks.extract_iloc_assign_by_sequence(
            key,
            value,
        )
    else:  # could be array or single element, or an NP array, or an iterable to be used for a column
        blocks = self.container._blocks.extract_iloc_assign_by_unit(
            key,
            value,
        )

    container = self.container.__class__(
        data=blocks,
        columns=self.container._columns,
        index=self.container._index,
        name=self.container._name,
        own_data=True
    )

    if hasattr(self.container, "_metadata"):
        container._metadata = self.container._metadata

    return container


class CustomFrame(Frame):
    def __init__(self, *args, **kwargs):
        self._metadata = kwargs.pop('metadata', {})
        super().__init__(*args, **kwargs)

    @property
    def metadata(self):
        return self._metadata

    def to_npz(self, fp: TPathSpecifier, *, include_index: bool = True, include_columns: bool = True, consolidate_blocks: bool = False, metadata=None) -> None:
        if metadata is None:
            metadata = {}
        self._metadata.update(metadata)

        NPZFrameConverter.to_archive(
            frame=self,
            fp=fp,
            include_index=include_index,
            include_columns=include_columns,
            consolidate_blocks=consolidate_blocks,
            metadata=self._metadata,
        )

    def to_npy(self, fp: TPathSpecifier, *, include_index: bool = True, include_columns: bool = True, consolidate_blocks: bool = False, metadata=None) -> None:
        if metadata is None:
            metadata = {}
        self._metadata.update(metadata)

        # noinspection PyArgumentList
        NPYFrameConverter.to_archive(
            frame=self,
            fp=fp,
            include_index=include_index,
            include_columns=include_columns,
            consolidate_blocks=consolidate_blocks,
            metadata=self._metadata,
        )

    @classmethod
    def from_npy_mmap(cls, fp: TPathSpecifier, ) -> tp.Tuple[TFrameAny, tp.Callable[[], None]]:
        raise NotImplementedError
