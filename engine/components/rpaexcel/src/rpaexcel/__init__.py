from enum import Enum


class ApplicationType(Enum):
    EXCEL = "Excel"
    WPS = "WPS"
    DEFAULT = "Default"


class FileExistenceType(Enum):
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CANCEL = "cancel"


class SaveType(Enum):
    SAVE = "save"
    SAVE_AS = "save_as"
    ABORT = "abort"


class SaveType_ALL(Enum):
    SAVE = "save"
    ABORT = "abort"


class CloseType(Enum):
    NOTSAVE = "not_save"
    SAVE = "save"
    SAVE_AS = "save_as"


class ReadRangeType(Enum):
    CELL = "cell"
    ROW = "row"
    COLUMN = "column"
    AREA = "area"
    ALL = "all"


class EditRangeType(Enum):
    ROW = "row"
    COLUMN = "column"
    AREA = "area"
    CELL = "cell"


class FontType(Enum):
    NO_CHANGE = "no_change"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    NORMAL = "normal"


class PasteType(Enum):
    ALL = "all"
    VALUE_AND_FORMAT = "value_and_format"
    FORMAT = "format"
    EXCLUDE_FRAME = "exclude_frame"
    COL_WIDTH_ONLY = "col_width_only"
    FORMULA_ONLY = "formula_only"
    FORMULA_AND_FORMAT = "formula_and_format"
    PASTE_VALUE = "paste_value"


class NumberFormatType(Enum):
    NO_CHANGE = "no_change"
    GENERAL = "G/通用格式"
    NUMBER = "0.00"
    CURRENCY = "¥#,##0.00"
    ACCOUNTING = "_(¥* #,##0.00_);_(¥* (#,##0.00);_(¥* -_0_0_);_(@_)"
    SHORT_DATE = "yyyy/m/d"
    LONG_DATE = "yyyy年mm月dd日"
    TIME = "h:mm:ss AM/PM"
    PERCENT = "0.00%"
    FRACTION = "# ?/?"
    SCIENTIFIC = "0.00E+00"
    TEXT = "@"
    CUSTOM = "other"


class FontNameType(Enum):
    NO_CHANGE = "维持原状"
    HEITI = "黑体"
    FANGSONG = "仿宋"
    SONGTI = "宋体"
    WEIRUANYAHEI = "微软雅黑"
    WEIRUANYAHEI_LIGHT = "微软雅黑 Light"
    HUAWENZHONGSONG = "华文中宋"
    HUAWENFANGSONG = "华文仿宋"
    HUAWENSONGTI = "华文宋体"
    HUAWENCAIYUN = "华文彩云"
    HUAWENXINWEI = "华文新魏"
    HUAWENKAITI = "华文楷体"
    HUAWENHUPO = "华文琥珀"
    HUAWEIXIHEI = "华文细黑"
    HUAWENXINGKAI = "华文行楷"
    HUAWENLISHU = "华文隶书"
    YOUYUAN = "幼圆"
    LISHU = "隶书"
    FANGZHENGYAOTI = "方正姚体"
    FANGZHENGSHUTI = "方正舒体"
    XINSONGTI = "新宋体"
    WEIRUANZHENGHEITI_LIGHT = "微軟正黑體 Light"
    WEIRUANZHENGHEITI = "微軟正黑體"
    XIMINGTI = "細明體_HKSCS-ExtB"
    DENGXIAN = "等线"
    DENGXIAN_LIGHT = "等线 Light"
    KAITI = "楷体"
    XIMINGZHI = "細明置-ExtB"
    XINXIMINGZHI = "新細明置-ExtB"
    ONYX = "Onyx"
    MYANMAR_TEXT = "Myanmar Text"
    NIAGARA_ENGRAVED = "Niagara Engraved"
    NIAGARA_SOLID = "Niagara Solid"
    NIRMALA_UL = "Nirmala Ul"
    NIRMALA_UL_SEMILIGHT = "Nirmala Ul Semilight"
    OCR_A_EXTENDED = "OCR A Extended"
    OLD_ENGLISH_TEXT = "Old English Text MT"
    PALACE_SCRIPT_MT = "Palace Script MT"
    POOR_RICHARD = "Poor Richard"
    PAPYRUS = "Papyrus"
    PARCHMENT = "Parchment"
    PERPETUA = "Perpetua"
    PERPETUA_TILTING_MT = "Perpetua Tilting MT"
    PLAYBILL = "Playbill"
    MV_BOLI = "MV Boli"
    PRISTINA = "Pristina"
    RAGE_ITALIC = "Rage Italic"
    RAVIE = "Ravie"
    PALATO_LINOTYPE = "Palatino Linotype"
    MT_EXTRA = "MT Extra"
    MS_GOTHIC = "MS Gothic"
    MS_REFERENCE_SPECIALTY = "MS Reference Specialty"
    MARLETT = "Marlett"
    MATURA_MT_SCRIPT_CAPITALS = "Matura MT Script Capitals"
    MICROSOFT_HIMALAYA = "Microsoft Himalaya"
    MICROSOFT_JHENGHEI_UI = "Microsoft JhengHei UI"
    MICROSOFT_JHENGHEI_UI_LIGHT = "Microsoft JhengHei UI Light"
    MICROSOFT_NEW_TAI_LUE = "Microsoft New Tai Lue"
    MICROSOFT_PHAGSPA = "Microsoft PhagsPa"
    MICROSOFT_SANS_SERIF = "Microsoft Sans Serif"
    MICROSOFT_TAILE = "Microsoft Tai Le"
    MICROSOFT_UIGHUR = "Microsoft Uighur"
    MICROSOFT_YAHEI_Ul = "Microsoft Yahei Ul"
    MICROSOFT_yahei_Ul_LIGHT = "Microsoft YaHei Ul Light"
    MICROSOFT_YI_BAITI = "Microsoft Yi Baiti"
    MISTRAL = "Mistral"
    MODERN_NO20 = "Modern No.20"
    MOGOLIAN_BAITI = "Mogolian Baiti"


class HorizontalAlign(Enum):
    NO_CHANGE = "no_change"
    DEFAULT = "default"
    LEFT = "left-aligned"
    RIGHT = "right-aligned"
    CENTER = "center"
    PADDING = "padding"
    BOTH = "aligned_both_sides"
    CROSS = "center_cross_column"
    DISTRIBUTED = "distributed_align"


class VerticalAlign(Enum):
    NO_CHANGE = "no_change"
    UP = "up"
    MIDDLE = "middle"
    DOWN = "down"
    BOTH = "aligned_both_sides"
    DISTRIBUTED = "distributed_align"


class ClearType(Enum):
    CONTENT = "content"
    STYLE = "style"
    ALL = "all"


class SheetRangeType(Enum):
    ACTIVATED = "activated"
    ALL = "all"


class DeleteCellDirection(Enum):
    LOWER_MOVE_UP = "lower_move_up"
    RIGHT_MOVE_LEFT = "right_move_left"


class InsertType(Enum):
    ROW = "row"
    COLUMN = "column"


class EnhancedInsertType(Enum):
    ROW = "row"  # 指定行号插入
    COLUMN = "column"  # 指定列号插入
    ADD_ROWS = "add_rows"  # 末尾追加插入
    ADD_COLUMNS = "add_columns"  # 右边追加插入


class RowDirectionType(Enum):
    UPPER = "upper"
    LOWER = "lower"


class ColumnDirectionType(Enum):
    LEFT = "left"
    RIGHT = "right"


class MergeOrSplitType(Enum):
    MERGE = "merge"
    SPLIT = "split"


class CopySheetType(Enum):
    CURRENT_WORKBOOK = "current_workbook"
    OTHER_WORKBOOK = "other_workbook"


class CopySheetLocationType(Enum):
    BEFORE = "before"
    AFTER = "after"
    FIRST = "first"
    LAST = "last"


class MoveSheetType(Enum):
    MOVE_AFTER = "move_after"
    MOVE_BEFORE = "move_before"
    MOVE_TO_FIRST = "move_to_first"
    MOVE_TO_LAST = "move_to_last"


class SearchRangeType(Enum):
    ALL = "all"  # 已编辑区域
    ROW = "row"
    COLUMN = "column"
    AREA = "area"


class SearchSheetType(Enum):
    ALL = "all"  # 所有工作表
    ONE = "one"  # 指定工作表


class MatchCountType(Enum):
    ALL = "all"  # 所有匹配项
    FIRST = "first"  # 第一个匹配项


class SearchResultType(Enum):
    CELL = "cell"
    COL_AND_ROW = "col_and_row"


class ImageSizeType(Enum):
    SCALE = "scale"
    NUMBER = "number"
    AUTO = "auto"


class InsertFormulaDirectionType(Enum):
    DOWN = "down"
    RIGHT = "right"


class CreateCommentType(Enum):
    POSITION = "position"
    CONTENT = "content"


class ColumnOutputType(Enum):
    LETTER = "letter"
    NUMBER = "number"


class RowType(Enum):
    ALL = "all"
    ONE_ROW = "one_row"


class ColumnType(Enum):
    ALL = "all"
    ONE_COLUMN = "one_column"


class SetType(Enum):
    VALUE = "value"  # 设置值
    AUTO = "auto"  # 自动行高/列宽


class CloseRangeType(Enum):
    ONE = "one"
    ALL = "all"


class SheetInsertType(Enum):
    FIRST = "first"
    LAST = "last"
    BEFORE = "before"
    AFTER = "after"
