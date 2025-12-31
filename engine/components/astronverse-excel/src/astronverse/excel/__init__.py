from enum import Enum


class ApplicationType(Enum):
    """默认创建程序类型"""

    EXCEL = "Excel"  # Excel
    WPS = "WPS"  # WPS
    DEFAULT = "Default"  # 系统自动选择


class FileExistenceType(Enum):
    """文件名存在处理方式"""

    OVERWRITE = "overwrite"  # 覆盖原有文件
    RENAME = "rename"  # 创建文件副本
    CANCEL = "cancel"  # 跳过保存操作


class SaveType(Enum):
    """保存类型"""

    SAVE = "save"  # 保存
    SAVE_AS = "save_as"  # 另存为
    ABORT = "abort"  # 不保存


class SaveType_ALL(Enum):
    """保存类型（关闭所有文档时）"""

    SAVE = "save"  # 保存
    ABORT = "abort"  # 不保存


class CloseType(Enum):
    """关闭类型"""

    NOTSAVE = "not_save"  # 不保存
    SAVE = "save"  # 保存
    SAVE_AS = "save_as"  # 另存为


class ReadRangeType(Enum):
    """读取范围类型"""

    CELL = "cell"  # 单元格
    ROW = "row"  # 行
    COLUMN = "column"  # 列
    AREA = "area"  # 区域
    ALL = "all"  # 已编辑区域


class EditRangeType(Enum):
    """编辑范围类型"""

    ROW = "row"  # 行
    COLUMN = "column"  # 列
    AREA = "area"  # 区域
    CELL = "cell"  # 单元格


class FontType(Enum):
    """字体类型"""

    NO_CHANGE = "no_change"  # 维持原状
    BOLD = "bold"  # 粗体
    ITALIC = "italic"  # 斜体
    BOLD_ITALIC = "bold_italic"  # 粗斜体
    NORMAL = "normal"  # 常规


class PasteType(Enum):
    """粘贴类型"""

    ALL = "all"  # 默认全部粘贴
    VALUE_AND_FORMAT = "value_and_format"  # 值和数字格式
    FORMAT = "format"  # 仅格式
    EXCLUDE_FRAME = "exclude_frame"  # 边框除外
    COL_WIDTH_ONLY = "col_width_only"  # 仅列宽
    FORMULA_ONLY = "formula_only"  # 仅公式
    FORMULA_AND_FORMAT = "formula_and_format"  # 公式和数字格式
    PASTE_VALUE = "paste_value"  # 粘贴值


class NumberFormatType(Enum):
    """数字格式类型"""

    NO_CHANGE = "no_change"  # 维持原状
    GENERAL = "G/通用格式"  # 常规
    NUMBER = "0.00"  # 数字
    CURRENCY = "¥#,##0.00"  # 货币
    ACCOUNTING = "_(¥* #,##0.00_);_(¥* (#,##0.00);_(¥* -_0_0_);_(@_)"  # 会计专用
    SHORT_DATE = "yyyy/m/d"  # 短日期
    LONG_DATE = "yyyy年mm月dd日"  # 长日期
    TIME = "h:mm:ss AM/PM"  # 时间
    PERCENT = "0.00%"  # 百分比
    FRACTION = "# ?/?"  # 分数
    SCIENTIFIC = "0.00E+00"  # 科学记数
    TEXT = "@"  # 文本
    CUSTOM = "other"  # 自定义


class FontNameType(Enum):
    """字体名称类型"""

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
    """水平对齐方式"""

    NO_CHANGE = "no_change"  # 维持原状
    DEFAULT = "default"  # 默认常规
    LEFT = "left-aligned"  # 左对齐
    RIGHT = "right-aligned"  # 右对齐
    CENTER = "center"  # 居中对齐
    PADDING = "padding"  # 填充
    BOTH = "aligned_both_sides"  # 两端对齐
    CROSS = "center_cross_column"  # 跨列居中
    DISTRIBUTED = "distributed_align"  # 分散对齐


class VerticalAlign(Enum):
    """垂直对齐方式"""

    NO_CHANGE = "no_change"  # 维持原状
    UP = "up"  # 靠上
    MIDDLE = "middle"  # 居中
    DOWN = "down"  # 靠下
    BOTH = "aligned_both_sides"  # 两端对齐
    DISTRIBUTED = "distributed_align"  # 分散对齐


class ClearType(Enum):
    """清除类型"""

    CONTENT = "content"  # 清除内容
    STYLE = "style"  # 清除格式
    ALL = "all"  # 清除内容和格式


class SheetRangeType(Enum):
    """工作表范围类型"""

    ACTIVATED = "activated"  # 当前激活工作表
    ALL = "all"  # 所有工作表


class DeleteCellDirection(Enum):
    """删除单元格后剩余数据填充方向"""

    LOWER_MOVE_UP = "lower_move_up"  # 下方单元格上移
    RIGHT_MOVE_LEFT = "right_move_left"  # 右侧单元格左移


class InsertType(Enum):
    """插入类型"""

    ROW = "row"  # 行
    COLUMN = "column"  # 列


class EnhancedInsertType(Enum):
    """增强插入类型"""

    ROW = "row"  # 指定行号插入
    COLUMN = "column"  # 指定列号插入
    ADD_ROWS = "add_rows"  # 在最后一行后插入
    ADD_COLUMNS = "add_columns"  # 在最后一列后插入


class RowDirectionType(Enum):
    """插入行方向"""

    UPPER = "upper"  # 向上插入
    LOWER = "lower"  # 向下插入


class ColumnDirectionType(Enum):
    """插入列方向"""

    LEFT = "left"  # 向左插入
    RIGHT = "right"  # 向右插入


class MergeOrSplitType(Enum):
    """合并或拆分类型"""

    MERGE = "merge"  # 合并
    SPLIT = "split"  # 拆分


class CopySheetType(Enum):
    """复制工作表类型"""

    CURRENT_WORKBOOK = "current_workbook"  # 当前工作簿
    OTHER_WORKBOOK = "other_workbook"  # 其他工作簿


class CopySheetLocationType(Enum):
    """复制工作表位置类型"""

    BEFORE = "before"  # 复制到当前工作表之前
    AFTER = "after"  # 复制到当前工作表之后
    FIRST = "first"  # 复制到第一个工作表
    LAST = "last"  # 复制到最后一个工作表


class MoveSheetType(Enum):
    """移动工作表类型"""

    MOVE_AFTER = "move_after"  # 移动到目标工作表之后
    MOVE_BEFORE = "move_before"  # 移动到目标工作表之前
    MOVE_TO_FIRST = "move_to_first"  # 移动到第一个工作表
    MOVE_TO_LAST = "move_to_last"  # 移动到最后一个工作表


class SearchRangeType(Enum):
    """查找范围类型"""

    ALL = "all"  # 已编辑区域
    ROW = "row"  # 行
    COLUMN = "column"  # 列
    AREA = "area"  # 区域


class SearchSheetType(Enum):
    """查找工作表类型"""

    ALL = "all"  # 全部工作表
    ONE = "one"  # 单个工作表


class MatchCountType(Enum):
    """匹配数量类型"""

    ALL = "all"  # 所有结果
    FIRST = "first"  # 第一个结果


class SearchResultType(Enum):
    """查找结果输出类型"""

    CELL = "cell"  # 返回单元格位置
    COL_AND_ROW = "col_and_row"  # 返回列号和行号


class ImageSizeType(Enum):
    """图片大小控制类型"""

    SCALE = "scale"  # 调整缩放比例
    NUMBER = "number"  # 调整高度和宽度数值
    AUTO = "auto"  # 自动调整大小匹配范围


class InsertFormulaDirectionType(Enum):
    """公式插入方向"""

    DOWN = "down"  # 向下插入
    RIGHT = "right"  # 向右插入


class CreateCommentType(Enum):
    """批注插入方式"""

    POSITION = "position"  # 按照单元格位置插入
    CONTENT = "content"  # 按照内容搜索插入


class ColumnOutputType(Enum):
    """列输出格式"""

    LETTER = "letter"  # 字母列号
    NUMBER = "number"  # 数字列号


class RowType(Enum):
    """行类型"""

    ALL = "all"  # 所有行
    ONE_ROW = "one_row"  # 单行


class ColumnType(Enum):
    """列类型"""

    ALL = "all"  # 所有列
    ONE_COLUMN = "one_column"  # 单列


class SetType(Enum):
    """设置类型"""

    VALUE = "value"  # 设置值
    AUTO = "auto"  # 自动行高/列宽


class CloseRangeType(Enum):
    """关闭文档范围"""

    ONE = "one"  # 当前文档
    ALL = "all"  # 所有文档


class SheetInsertType(Enum):
    """工作表插入位置类型"""

    FIRST = "first"  # 新表成为第一个工作表
    LAST = "last"  # 新表成为最后一个工作表
    BEFORE = "before"  # 新表插入到...表之前
    AFTER = "after"  # 新表插入到...表之后


class EditType(Enum):
    """写入类型，包括追加和覆盖两种"""

    OVERWRITE = "overwrite"  # 覆盖
    APPEND = "append"  # 追加
