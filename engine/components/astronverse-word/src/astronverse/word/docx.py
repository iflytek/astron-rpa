import os
import platform
import sys
from typing import Tuple

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH

from astronverse.word import (
    ApplicationType,
    EncodingType,
    SelectRangeType,
    FileExistenceType,
    SaveType,
    CloseRangeType,
    UnderLineStyle,
    SelectTextType,
    CursorPointerType,
    CursorPositionType,
    MoveDirectionType,
    MoveUpDownType,
    MoveLeftRightType,
    InsertionType,
    InsertImgType,
    SearchTableType,
    TableBehavior,
    RowAlignment,
    VerticalAlignment,
    DeleteMode,
    ReplaceType,
    ReplaceMethodType,
    CommentType,
    FileType,
    ConvertPageType,
    SaveFileType,
)
from astronverse.word.core import IDocumentCore
from astronverse.word.docx_obj import DocumentObject
from astronverse.word.error import (
    DOCUMENT_READ_ERROR_FORMAT,
    DOCUMENT_NOT_EXIST_ERROR_FORMAT,
    DOCUMENT_PATH_ERROR_FORMAT,
    CONTENT_FORMAT_ERROR_FORMAT,
    FILENAME_ALREADY_EXISTS_ERROR,
)


if sys.platform == "win32":
    from astronverse.word.core_win import WordDocumentCore
elif platform.system() == "Linux":
    from astronverse.word.core_unix import WordDocumentCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

WordDocumentCore: IDocumentCore = WordDocumentCore()


class Docx:
    @staticmethod
    @IDocumentCore.validate_path("file_path")
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("encoding", level=AtomicLevel.ADVANCED),
            atomicMg.param("open_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "open_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.open_pwd.show",
                        expression="return $this.open_pwd_flag.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param("write_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "write_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.write_pwd.show",
                        expression="return $this.write_pwd_flag.value == true",
                    )
                ],
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("doc_obj", types="DocumentObject"),
        ],
    )
    def open_document(
        file_path: PATH = "",
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = True,
        encoding: EncodingType = EncodingType.UTF8,
        open_pwd_flag: bool = False,
        open_pwd: str = "",
        write_pwd_flag: bool = False,
        write_pwd: str = "",
    ) -> DocumentObject:
        if not open_pwd_flag:
            open_pwd = ""
        if not write_pwd_flag:
            write_pwd = ""
        try:
            doc_obj = WordDocumentCore.open(
                file_path,
                default_application,
                visible_flag,
                encoding,
                open_pwd,
                write_pwd,
            )
            return DocumentObject(doc_obj)
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(file_path),
                "打开文档失败，请检查文件路径是否正确！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param("doc", types="DocumentObject"),
        ],
        outputList=[
            atomicMg.param("doc_data", types="Str"),
        ],
    )
    def read_document_content(doc: DocumentObject, select_range: SelectRangeType = SelectRangeType.ALL):
        if not doc:
            raise BaseException(DOCUMENT_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            doc_data = WordDocumentCore.read(doc.document_object, select_range)
            return doc_data
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("doc_obj", types="DocumentObject"),
            atomicMg.param("doc_create_path", types="PATH"),
        ],
    )
    def create_docx(
        file_path: str = "",
        file_name: str = "",
        default_application: ApplicationType = ApplicationType.WORD,
        visible_flag: bool = True,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> Tuple[DocumentObject, PATH]:
        if not os.path.exists(file_path):
            raise BaseException(
                DOCUMENT_PATH_ERROR_FORMAT.format(file_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )
        try:
            if file_name:
                file_name += ".docx"
            else:
                file_name = "新建Word文档.docx"
            doc_obj, doc_create_path = WordDocumentCore.create(
                file_path,
                file_name,
                visible_flag,
                default_application,
                exist_handle_type,
            )
            return DocumentObject(doc_obj), doc_create_path
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(file_path),
                "打开文档失败，请检查文件路径是否正确！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression=f"return $this.save_type.value == '{SaveType.SAVE_AS.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression=f"return $this.save_type.value == '{SaveType.SAVE_AS.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression=f"return $this.save_type.value == '{SaveType.SAVE_AS.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("save_file_path", types="PATH"),
        ],
    )
    def save_docx(
        doc: DocumentObject,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        close_flag: bool = False,
    ):
        if not doc:
            raise BaseException(DOCUMENT_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            save_file_path = WordDocumentCore.save(
                doc.document_object,
                file_path,
                file_name,
                save_type,
                exist_handle_type,
                close_flag,
            )
            return save_file_path
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(e),
                "读取文档内容失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression=f"return $this.save_type.value == '{SaveType.SAVE_AS.value}' && $this.close_range_flag.value == '{CloseRangeType.ONE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "pkill_flag",
                dynamics=[
                    DynamicsItem(
                        key="$this.pkill_flag.show",
                        expression=f"return $this.close_range_flag.value == '{CloseRangeType.ALL.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "save_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type.show",
                        expression=f"return $this.close_range_flag.value == '{CloseRangeType.ONE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression=f"return $this.save_type.value == '{SaveType.SAVE_AS.value}' && $this.close_range_flag.value == '{CloseRangeType.ONE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression=f"return $this.close_range_flag.value == '{CloseRangeType.ONE.value}'",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def close_docx(
        doc: DocumentObject,
        close_range_flag: CloseRangeType = CloseRangeType.ONE,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        pkill_flag: bool = False,
    ):
        if not doc:
            raise BaseException(DOCUMENT_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            WordDocumentCore.close(
                doc.document_object,
                file_path,
                file_name,
                save_type,
                exist_handle_type,
                close_range_flag,
                pkill_flag,
            )
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param("font_size", required=False),
            atomicMg.param("font_name", required=False),
            atomicMg.param(
                "font_color",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
                required=False,
            ),
        ],
        outputList=[],
    )
    def insert_docx(
        doc: DocumentObject,
        text: str = "",
        enter_flag: bool = False,
        font_size: int = 12,
        bold_flag: bool = False,
        italic_flag: bool = False,
        underline_flag: UnderLineStyle = UnderLineStyle.DEFAULT,
        font_name: str = "宋体",
        font_color: str = "0,0,0",
    ):
        if not doc:
            raise BaseException(DOCUMENT_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            if not font_color:
                font_color = "0,0,0"
            text_format = {
                "font_size": font_size,
                "bold": bold_flag,
                "italic": italic_flag,
                "underline": underline_flag,
                "font_name": font_name,
                "font_color": font_color,  # 0,0,0
            }
            WordDocumentCore.insert(doc.document_object, text, enter_flag, text_format)
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "p_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_start.show",
                        expression=f"return $this.select_type.value == '{SelectTextType.PARAGRAPH.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "p_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_end.show",
                        expression=f"return $this.select_type.value == '{SelectTextType.PARAGRAPH.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "r_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_start.show",
                        expression=f"return $this.select_type.value == '{SelectTextType.ROW.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "r_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_end.show",
                        expression=f"return $this.select_type.value == '{SelectTextType.ROW.value}'",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def select_text(
        doc: DocumentObject,
        select_type: SelectTextType = SelectTextType.ALL,
        p_start: int = 1,
        p_end: int = 1,
        r_start: int = 1,
        r_end: int = 1,
    ):
        if not doc:
            raise BaseException(DOCUMENT_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        if (
            p_start > p_end
            or r_start > r_end
            or not IDocumentCore.are_positive_integers(p_start, p_end, r_start, r_end)
        ):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请正确输入起始行号或段落号！")
        try:
            WordDocumentCore.select(doc.document_object, select_type, p_start, p_end, r_start, r_end)
        except Exception:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "选中文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "content",
                dynamics=[
                    DynamicsItem(
                        key="$this.content.show",
                        expression=f"return $this.by.value == '{CursorPointerType.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "c_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_idx.show",
                        expression=f"return $this.by.value == '{CursorPointerType.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "p_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_idx.show",
                        expression=f"return $this.by.value == '{CursorPointerType.PARAGRAPH.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "r_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_idx.show",
                        expression=f"return $this.by.value == '{CursorPointerType.ROW.value}'",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def get_cursor_position(
        doc: DocumentObject,
        by: CursorPointerType = CursorPointerType.ALL,
        pos: CursorPositionType = CursorPositionType.HEAD,
        content: str = "",
        c_idx: int = 1,
        p_idx: int = 1,
        r_idx: int = 1,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if not IDocumentCore.are_positive_integers(c_idx, p_idx, r_idx):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请输入正确的数值!")
        try:
            WordDocumentCore.cursor_position(doc.document_object, by, pos, content, c_idx, p_idx, r_idx)
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "定位光标位置失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "unitupdown",
                dynamics=[
                    DynamicsItem(
                        key="$this.unitupdown.show",
                        expression=f"return ['{MoveDirectionType.UP.value}', '{MoveDirectionType.DOWN.value}'].includes($this.direction.value)",
                    )
                ],
            ),
            atomicMg.param(
                "unitleftright",
                dynamics=[
                    DynamicsItem(
                        key="$this.unitleftright.show",
                        expression=f"return ['{MoveDirectionType.LEFT.value}', '{MoveDirectionType.RIGHT.value}'].includes($this.direction.value)",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def move_cursor(
        doc: DocumentObject,
        direction: MoveDirectionType = MoveDirectionType.UP,
        unitupdown: MoveUpDownType = MoveUpDownType.ROW,
        unitleftright: MoveLeftRightType = MoveLeftRightType.CHARACTER,
        distance: int = 0,
        with_shift: bool = False,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if not IDocumentCore.are_positive_integers(distance):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请输入正确的数值!")
        try:
            WordDocumentCore.move_cursor(
                doc.document_object,
                direction,
                unitupdown,
                unitleftright,
                distance,
                with_shift,
            )
        except Exception as e:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "移动光标失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic("Docx", inputList=[], outputList=[])
    def insert_sep(doc: DocumentObject, sep_type: InsertionType = InsertionType.PARAGRAPH):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            WordDocumentCore.insert_sep(doc.document_object, sep_type)
        except Exception as e:
            raise BaseException(DOCUMENT_READ_ERROR_FORMAT.format(doc), "插入失败，请检查文档是否打开！") from e

    @staticmethod
    @atomicMg.atomic("Docx", inputList=[], outputList=[])
    def insert_hyperlink(doc: DocumentObject, url: str = "", display: str = ""):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        WordDocumentCore.insert_hyperlink(doc.document_object, url, display)

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "img_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.img_path.show",
                        expression=f"return $this.img_from.value == '{InsertImgType.FILE.value}'",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_img(
        doc: DocumentObject,
        img_from: InsertImgType = InsertImgType.FILE,
        img_path: str = "",
        scale: int = 100,
        newline: bool = False,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        WordDocumentCore.insert_img(doc.document_object, img_from, img_path, scale, newline)

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "text",
                dynamics=[
                    DynamicsItem(
                        key="$this.text.show",
                        expression=f"return $this.search_type.value == '{SearchTableType.TEXT.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("table_content", types="List"),
        ],
    )
    def read_table(
        doc: DocumentObject,
        search_type: SearchTableType = SearchTableType.IDX,
        idx: int = 1,
        text: str = "",
    ) -> DocumentObject:
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            table_content = WordDocumentCore.read_table(doc.document_object, search_type, idx, text)
            return table_content
        except Exception as e:
            print(e)
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "读取表格失败，请检查文档是否打开！",
            ) from e

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "font_size",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_size.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_color",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.font_color.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_set",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_set.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_bold",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_bold.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_italic",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_italic.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "underline",
                dynamics=[
                    DynamicsItem(
                        key="$this.underline.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_table(
        doc: DocumentObject,
        table_content: list = "",
        table_behavior: TableBehavior = TableBehavior.DEFAULT,
        alignment: RowAlignment = RowAlignment.LEFT,
        v_alignment: VerticalAlignment = VerticalAlignment.TOP,
        border: bool = True,
        if_change_font: bool = False,
        font_size=None,
        font_color=None,
        font_set=None,
        font_bold: bool = False,
        font_italic: bool = False,
        underline: UnderLineStyle = UnderLineStyle.DEFAULT,
        newline: bool = True,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            WordDocumentCore.insert_table(
                doc.document_object,
                table_content,
                table_behavior,
                alignment,
                v_alignment,
                border,
                if_change_font,
                font_size,
                font_color,
                font_set,
                font_bold,
                font_italic,
                underline,
                newline,
            )
        except Exception as exc:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "插入表格失败，请检查文档是否打开！",
            ) from exc

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "delete_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_str.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "str_delete_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.str_delete_all.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "delete_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_idx.show",
                        expression=f"return $this.str_delete_all.value == false && $this.delete_mode.value == '{DeleteMode.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "p_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_start.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.RANGE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "p_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_end.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.RANGE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "c_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_start.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.RANGE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "c_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_end.show",
                        expression=f"return $this.delete_mode.value == '{DeleteMode.RANGE.value}'",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete(
        doc: DocumentObject,
        delete_mode: DeleteMode = DeleteMode.ALL,
        delete_str: str = "",
        delete_idx: int = 0,
        str_delete_all: bool = False,
        p_start: int = 0,
        c_start: int = 0,
        p_end: int = 0,
        c_end: int = 0,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            WordDocumentCore.delete(
                doc.document_object,
                delete_mode,
                delete_str,
                delete_idx,
                str_delete_all,
                p_start,
                c_start,
                p_end,
                c_end,
            )
        except Exception as exc:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "删除内容失败，请检查文档是否打开！",
            ) from exc

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "new_word",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_word.show",
                        expression=f"return $this.replace_type.value == '{ReplaceType.STR.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "img_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.img_path.show",
                        expression=f"return $this.replace_type.value == '{ReplaceType.IMG.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "delete_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_idx.show",
                        expression="return $this.str_delete_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def replace(
        doc: DocumentObject,
        origin_word: str = "",
        replace_type: ReplaceType = ReplaceType.STR,
        new_word: str = "",
        img_path: str = "",
        replace_method: ReplaceMethodType = ReplaceMethodType.ALL,
        ignore_case: bool = True,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            _ = WordDocumentCore.replace(
                doc.document_object,
                replace_type,
                origin_word,
                new_word,
                img_path,
                replace_method,
                ignore_case,
            )
        except Exception as exc:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "查找替换内容失败，请检查文档是否打开！",
            ) from exc

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "paragraph_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.paragraph_idx.show",
                        expression=f"return $this.comment_type.value == '{CommentType.POSITION.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "start",
                dynamics=[
                    DynamicsItem(
                        key="$this.start.show",
                        expression=f"return $this.comment_type.value == '{CommentType.POSITION.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "end",
                dynamics=[
                    DynamicsItem(
                        key="$this.end.show",
                        expression=f"return $this.comment_type.value == '{CommentType.POSITION.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "target_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.target_str.show",
                        expression=f"return $this.comment_type.value == '{CommentType.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "comment_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_all.show",
                        expression=f"return $this.comment_type.value == '{CommentType.CONTENT.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "comment_index",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_index.show",
                        expression="return $this.comment_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def create_comment(
        doc: DocumentObject,
        comment: str = "",
        comment_type: CommentType = CommentType.POSITION,
        paragraph_idx: int = 1,
        start: int = 1,
        end: int = 1,
        target_str: str = "",
        comment_all: bool = True,
        comment_index: int = 1,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            WordDocumentCore.create_comment(
                doc.document_object,
                paragraph_idx,
                start,
                end,
                comment,
                comment_type,
                target_str,
                comment_all,
                comment_index,
            )
        except Exception as exc:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "创建批注失败，请检查文档是否打开！",
            ) from exc

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "comment_index",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_index.show",
                        expression="return $this.delete_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete_comment(doc: DocumentObject, delete_all: bool = False, comment_index: int = 1):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            WordDocumentCore.delete_comment(doc.document_object, comment_index, delete_all)
        except Exception as exc:
            raise BaseException(
                DOCUMENT_READ_ERROR_FORMAT.format(doc),
                "删除批注失败，请检查文档是否打开！",
            ) from exc

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "output_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.output_name.show",
                        expression="return $this.default_name.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "page_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_type.show",
                        expression=f"return $this.output_file_type.value == '{FileType.PDF.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "page_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_start.show",
                        expression=f"return $this.page_type.value == '{ConvertPageType.RANGE.value}' && $this.output_file_type.value == '{FileType.PDF.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "page_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_end.show",
                        expression=f"return $this.page_type.value == '{ConvertPageType.RANGE.value}' && $this.output_file_type.value == '{FileType.PDF.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "output_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
        outputList=[],
    )
    def convert_format(
        doc: DocumentObject,
        output_path: str = "",
        default_name: bool = True,
        output_name: str = None,
        output_file_type: FileType = FileType.PDF,
        page_type: ConvertPageType = ConvertPageType.ALL,
        page_start: int = 1,
        page_end: int = 1,
        save_type: SaveFileType = SaveFileType.WARN,
    ):
        if not doc:
            raise BaseException(
                DOCUMENT_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if default_name:
            document_name = doc.document_object.Name
            output_name, extension = os.path.splitext(document_name)

        try:
            if output_file_type == FileType.PDF:
                WordDocumentCore.convert_to_pdf(
                    doc.document_object,
                    output_path,
                    output_name,
                    page_type,
                    page_start,
                    page_end,
                    save_type,
                )
            elif output_file_type == FileType.TXT:
                WordDocumentCore.convert_to_txt(doc.document_object, output_path, output_name, save_type)
        except Exception as exc:
            raise BaseException(
                FILENAME_ALREADY_EXISTS_ERROR.format(output_name),
                "导出失败，文件名已存在！",
            ) from exc
