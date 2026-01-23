"""
打印核心服务模块

提供多种文件类型（Word、Excel、PDF、图片）的打印功能，支持自定义打印参数。
包含打印机管理、打印任务队列、打印状态查询等辅助方法。

主要类：
    PrinterCore: 打印服务主类，包含各类打印方法和工具方法。
"""

import os
import queue
import subprocess
import sys
import time

import win32com
import win32com.client as wc
import win32print
import win32ui
from astronverse.baseline.logger.logger import logger
from astronverse.system import BatchType, DocAppType, FileType, XlsAppType
from PIL import Image, ImageWin


class PrinterCore:
    """
    打印核心服务主类。

    提供 Word、Excel、PDF、图片等文件的打印功能，支持自定义参数。
    包含打印机管理、打印任务队列、打印状态查询等辅助方法。

    """

    IMAGE_TYPES = {
        ".bmp",
        ".bufr",
        ".cur",
        ".dcx",
        ".eps",
        ".fits",
        ".fli",
        ".flc",
        ".fpx",
        ".gbr",
        ".gd",
        ".gif",
        ".grib",
        ".ico",
        ".im",
        ".imt",
        ".jpeg",
        ".mcidas",
        ".mic",
        ".mpeg",
        ".msp",
        ".palm",
        ".pcd",
        ".pcx",
        ".pixar",
        ".png",
        ".ppm",
        ".psd",
        ".sgi",
        ".spider",
        ".tga",
        ".tiff",
        ".wal",
        ".wmf",
        ".xbm",
        ".xpm",
        ".jpg",
    }
    GHOSTSCRIPT_PATH = "gswin32c"
    _GHOSTSCRIPT_PATH = os.path.join(os.path.dirname(__file__), "lib", GHOSTSCRIPT_PATH)

    def __init__(self):
        self.word_obj = None
        self.excel_obj = None

    @staticmethod
    def _create_app(params: str):
        try:
            app_obj = win32com.client.gencache.EnsureDispatch(params)  # type: ignore
            return app_obj
        except Exception:
            try:
                app_obj = win32com.client.Dispatch(params)
                return app_obj
            except Exception:
                logger.info(f"创建app对象失败：{params}")

    def init_word_app(self, default_application: DocAppType = DocAppType.WORD):
        """初始化 word app"""
        keys = [
            "Word.Application",
            "Kwps.Application",
            "wps.Application",
        ]
        if default_application == DocAppType.WORD.value:
            keys = ["Word.Application"]
        elif default_application == DocAppType.WPS.value:
            keys = ["Kwps.Application", "wps.Application"]

        for key in keys:
            self.word_obj = self._create_app(key)
            if self.word_obj:
                return self.word_obj

        # 尝试重建缓存兜底
        try:
            wc.gencache.Rebuild()
            wc.gencache.EnsureModule("{00020813-0000-0000-C000-000000000046}", 0, 8, 7)
            for key in keys:
                self.word_obj = self._create_app(key)
                if self.word_obj:
                    return self.word_obj
        except:
            raise Exception(r"兜底失败，请尝试手动删除 %LOCALAPPDATA%\Temp\gen_py 目录再运行！")

        raise Exception("未检测到wps和office注册表信息！")

    def init_excel_app(self, default_application: XlsAppType = XlsAppType.EXCEL):
        """初始化 excel app"""
        keys = [
            "Excel.Application",
            "Ket.Application",
            "et.Application",
            "Kwps.Application",
            "wps.Application",
        ]
        if default_application == XlsAppType.EXCEL.value:
            keys = ["Excel.Application"]
        elif default_application == XlsAppType.WPS.value:
            keys = ["Ket.Application", "et.Application", "Kwps.Application", "wps.Application"]

        for key in keys:
            self.excel_obj = self._create_app(key)
            if self.excel_obj:
                return self.excel_obj

        # 尝试重建缓存兜底
        try:
            wc.gencache.Rebuild()
            wc.gencache.EnsureModule("{00020813-0000-0000-C000-000000000046}", 0, 8, 7)
            for key in keys:
                self.excel_obj = self._create_app(key)
                if self.excel_obj:
                    return self.excel_obj
        except:
            raise Exception(r"兜底失败，请尝试手动删除 %LOCALAPPDATA%\Temp\gen_py 目录再运行！")

        raise Exception("未检测到wps和office注册表信息！")

    def run(self, printer_name="", print_file=None, printer_type="", file_type="", batch_print="", **kwargs):
        """
        执行打印任务。
        根据打印机名称和文件类型，自动分派到对应的打印方法。
        支持批量打印和自定义参数。

        Args:
            printer_name (str): 打印机名称。
            print_file (str|list): 待打印文件路径或文件列表。
            printer_type (str): 打印类型（default/custom）。
            **kwargs: 其他自定义参数。

        Returns:
            list: 每个打印任务的执行结果。
        """
        logger.info(f"选择的打印机: {printer_name}")
        # 批量打印时过滤文件类型
        if batch_print == BatchType.BATCH.value and print_file:
            print_file = self.file_type_batch(file_type=file_type, print_file=print_file)

        logger.info(f"选择的文件类型：{file_type}，打印的文件: {print_file}")

        if printer_name in ["默认打印机", ""]:
            _default_printer_name = win32print.GetDefaultPrinter()
            logger.info(f"获取到的默认打印机名称为：{_default_printer_name}")
        else:
            all_printers = PrinterCore.view_printer()
            logger.info(f"获取到的打印机列表为：{all_printers}")
            if all_printers and printer_name not in all_printers:
                raise ValueError("未发现 {} 打印机，请检查打印机名称.".format(printer_name))
            _default_printer_name = printer_name

        if not print_file:
            raise ValueError("待打印文件为空，请检查文件路径信息")

        print_queue = PrinterCore.generate_printer_task(
            _default_printer_name, print_file, printer_type, file_type, **kwargs
        )

        if print_queue is None:
            raise ValueError("{} 打印机暂不支持打印，请检查打印机信息".format(printer_name))

        flags = []
        while not print_queue.empty():
            task = print_queue.get()
            flag = task["print_function"](
                self,
                printer_name=task["printer_name"],
                file_path=task["file_path"],
                printer_type=task["printer_type"],
                **task["attributes"],
            )
            time.sleep(2)
            flags.append(flag)
        return flags

    @staticmethod
    def _add_task(printer_name: str = "", file_path: str = "", print_function=None, printer_type=None, **kwargs):
        """
        构造打印任务字典。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): 文件路径。
            print_function (callable): 打印方法。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            dict: 打印任务信息。
        """
        task = {
            "printer_name": printer_name,
            "file_path": file_path,
            "print_function": print_function,
            "printer_type": printer_type,
            "attributes": kwargs,
        }
        return task

    @staticmethod
    def _process_file(printer_name: str, file_path: str, printer_type: str, file_type: str, **kwargs):
        """
        根据文件类型分派到对应的打印方法。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): 文件路径。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            dict: 打印任务信息。
        """
        lower_suffix = file_path.lower()
        logger.info(f"处理打印文件类型：{file_type}，后缀名：{lower_suffix}")
        if lower_suffix.endswith((".doc", ".docx", ".wps")) and file_type == FileType.WORD.value:
            task = PrinterCore._add_task(printer_name, file_path, PrinterCore.print_word, printer_type, **kwargs)
        elif lower_suffix.endswith((".xls", ".xlsx", ".et")) and file_type == FileType.EXCEL.value:
            task = PrinterCore._add_task(printer_name, file_path, PrinterCore.print_excel, printer_type, **kwargs)
        elif lower_suffix.endswith(".pdf") and file_type == FileType.PDF.value:
            task = PrinterCore._add_task(printer_name, file_path, PrinterCore.print_pdf, printer_type, **kwargs)
        elif any(file_path.endswith(img) for img in PrinterCore.IMAGE_TYPES) and file_type == FileType.PICTURE.value:
            task = PrinterCore._add_task(printer_name, file_path, PrinterCore.print_img, printer_type, **kwargs)
        else:
            raise ValueError("不支持打印的文件类型，请检查文件信息")
        return task

    def print_word(self, printer_name: str, file_path: str, printer_type: str, **kwargs):
        """
        打印 Word 文档。
        支持默认和自定义打印参数。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): Word 文件路径。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            bool: 打印是否成功。
        """
        defaults = {
            "paper_size": "A4",
            "print_num": 1,
            "scale": None,
            "margin_type": None,
            "margin": [-1, -1, -1, -1],
            "orientation_type": None,
            "page_weight": "",
            "page_height": "",
            "pages": None,
        }

        params = {**defaults, **kwargs}
        printer_app = params.get("printer_app", DocAppType.WORD.value)
        logger.info(
            f"printer_app: {printer_app}, file_path: {file_path}, printer_type: {printer_type}, params: {params}"
        )
        if self.word_obj is None:
            self.init_word_app(printer_app)

        doc_app = self.word_obj
        if doc_app is None:
            raise ValueError("未检测到所选程序的注册表信息，请检查是否安装！")
        doc_app.Visible = 0
        doc_app.DisplayAlerts = 0
        doc_ = doc_app.Documents.Open(file_path)
        if printer_type == "default":
            try:
                doc_.PrintOut()
                doc_.Close(SaveChanges=0)
                # if hasattr(doc_app, "Quit"):
                #     doc_app.Quit()
            except AttributeError as e:
                raise e

        elif printer_type == "custom":
            try:
                paper_size_params = {
                    "A3": 6,
                    "A4": 7,
                    "小A4": 8,
                    "A5": 9,
                    "B4": 10,
                    "B5": 11,
                    "C_Sheet": 12,
                    "D_Sheet": 13,
                    "自定义": 41,
                }

                if params["orientation_type"] == "horizontal":
                    doc_.PageSetup.Orientation = 1
                elif params["orientation_type"] == "vertical":
                    doc_.PageSetup.Orientation = 0

                if params["paper_size"] == "custom":
                    doc_.PageSetup.PageWidth = float(params["page_width"]) * 2.83
                    doc_.PageSetup.PageHeight = float(params["page_height"]) * 2.83
                else:
                    doc_.PageSetup.PaperSize = paper_size_params.get(params["paper_size"], 7)

                if str(params["margin_type"]) == "custom":
                    doc_.PageSetup.LeftMargin = float(params["margin"][0]) * 2.83
                    doc_.PageSetup.RightMargin = float(params["margin"][2]) * 2.83
                    doc_.PageSetup.TopMargin = float(params["margin"][1]) * 2.83
                    doc_.PageSetup.BottomMargin = float(params["margin"][3]) * 2.83

                print_params = {}
                if 10 <= params["scale"] <= 200 and params["scale"] != 100:
                    scale = params["scale"] / 100
                    print_params["PrintZoomPaperWidth"] = round(doc_.PageSetup.PageWidth * scale * 20, 2)
                    print_params["PrintZoomPaperHeight"] = round(doc_.PageSetup.PageHeight * scale * 20, 2)

                if params["pages"]:
                    print_params["Range"] = 4
                    print_params["Pages"] = params["pages"]

                if params["print_num"]:
                    print_params["Copies"] = int(params["print_num"])

                doc_.PrintOut(**print_params)
                doc_.Close(SaveChanges=0)
                doc_app.Quit()

            except AttributeError as e:
                raise e
        return True

    def print_excel(self, printer_name: str, file_path: str, printer_type: str, **kwargs):
        """
        打印 Excel 文件。
        支持默认和自定义打印参数。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): Excel 文件路径。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            bool: 打印是否成功。
        """
        defaults = {
            "paper_size": "A4",
            "print_num": 1,
            "scale": None,
            "margin_type": None,
            "margin": [-1, -1, -1, -1],
            "orientation_type": None,
            "page_weight": "",
            "page_height": "",
            "pages": None,
        }

        params = {**defaults, **kwargs}
        printer_app = params.get("printer_app", XlsAppType.EXCEL.value)
        logger.info(
            f"printer_app: {printer_app}, file_path: {file_path}, printer_type: {printer_type}, params: {params}"
        )

        if self.excel_obj is None:
            self.init_excel_app(printer_app)

        try:
            xl_app = self.excel_obj
            if xl_app is None:
                raise ValueError("未检测到所选程序的注册表信息，请检查是否安装！")
            xl_app.Visible = 0  # 不显示EXEL的界面，True时为显示。 不在后台运行
            xl_app.DisplayAlerts = 0  # 不显示弹窗
            if hasattr(xl_app, "EnableEvents") and xl_app:
                xl_app.EnableEvents = False

            xl_workbook = xl_app.Workbooks.Open(file_path)
            if xl_workbook is None:
                raise ValueError("无法打开该软件")
            if hasattr(xl_workbook, "Checkcompatibility"):
                xl_workbook.Checkcompatibility = False  # 屏蔽弹窗
            if hasattr(xl_workbook, "RunAutoMacros"):
                xl_workbook.RunAutoMacros(2)  # 1:打开宏，2:禁用宏
            if printer_type == "default":
                sheets = xl_workbook.Sheets.Count
                for sheet in range(sheets):
                    wsheet = xl_workbook.Worksheets(sheet + 1)
                    value = str(wsheet.Cells(4, 6))
                    if value != "None":
                        wsheet.PageSetup.Zoom = 50

                    wsheet.PageSetup.PaperSize = 9  # 设置纸张大小，A3=8，A4=9(与Word不同)
                    wsheet.PageSetup.Orientation = 2  # 设置页面方向，纵向=1，横向=2(与Word不同)
                    wsheet.PrintOut()  # 打印# xl_workbook.Close(SaveChanges=0)  # 关闭文件，不保存
                xl_workbook.Close(SaveChanges=0)
                xl_app.Quit()
            elif printer_type == "custom":
                sheets = xl_workbook.Sheets.Count
                sheets_pages = PrinterCore.parse_pages(self, page_string=params["pages"])
                if max(sheets_pages) > sheets:
                    raise ValueError("请检查页码范围！")
                for sheet in sheets_pages:
                    wsheet = xl_workbook.Worksheets(sheet)
                    if 10 <= params["scale"] <= 200 and params["scale"] != 100:
                        wsheet.PageSetup.Zoom = params["scale"]

                    paper_size_parms = {
                        "A3": 8,
                        "A4": 9,
                        "小A4": 10,
                        "A5": 11,
                        "B4": 12,
                        "B5": 13,
                        "C_Sheet": 24,
                        "D_Sheet": 25,
                        "自定义": 256,
                    }
                    wsheet.PageSetup.PaperSize = 9  # 设置纸张大小，A3=8，A4=9(与Word不同)
                    if params["orientation_type"] == "horizontal":
                        wsheet.PageSetup.Orientation = 2  # 设置页面方向，纵向=1，横向=2(与Word不同)
                    elif params["orientation_type"] == "vertical":
                        wsheet.PageSetup.Orientation = 1  # 设置页面方向，纵向=1，横向=2(与Word不同)
                    if params["paper_size"] == "自定义":
                        wsheet.PageSetup.PageWidth = float(params["page_width"]) * 2.83
                        wsheet.PageSetup.PageHeight = float(params["page_width"]) * 2.83
                    else:
                        paper_size = paper_size_parms.get(params["paper_size"])
                        wsheet.PageSetup.PaperSize = paper_size

                    # wsheet.PageSetup.AlignMarginsHeaderFooter =True #边距对齐页眉和页脚
                    if str(params["margin_type"]) == "custom":
                        wsheet.PageSetup.LeftMargin = xl_app.CentimetersToPoints(float(params["margin"][0]) / 10)
                        wsheet.PageSetup.RightMargin = xl_app.CentimetersToPoints(float(params["margin"][1]) / 10)
                        wsheet.PageSetup.TopMargin = xl_app.CentimetersToPoints(float(params["margin"][2]) / 10)
                        wsheet.PageSetup.BottomMargin = xl_app.CentimetersToPoints(float(params["margin"][3]) / 10)

                    params_printer = {}
                    if params["print_num"]:
                        params_printer["Copies"] = int(params["print_num"])
                    if printer_name:
                        params_printer["ActivePrinter"] = printer_name
                    try:
                        wsheet.PrintOut(**params_printer)
                    except AttributeError as e:
                        xl_workbook.Close(SaveChanges=False)
                        xl_app.Quit()
                        raise e
        except Exception as e:
            raise e
        return True

    def print_pdf(self, printer_name: str, file_path: str, printer_type: str, **kwargs):
        """
        打印 PDF 文件。
        支持默认和自定义打印参数。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): PDF 文件路径。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            bool: 打印是否成功。
        """
        defaults = {
            "paper_size": "A4",
            "print_num": 1,
            "scale": None,
            "margin_type": None,
            "margin": [-1, -1, -1, -1],
            "orientation_type": None,
            "page_weight": "",
            "page_height": "",
            "pages": None,
        }

        params = {**defaults, **kwargs}

        _A4_width = 2479
        _A4_height = 3508
        paper_size_parms = {
            "A3": [3508, 4961],
            "A4": [2479, 3508],
            "小A4": [2480, 3508],
            "A5": [1748, 2480],
            "B4": [2953, 4170],
            "B5": [2079, 2953],
        }

        if params["paper_size"] is not None:
            size_list = paper_size_parms.get(params["paper_size"])
            if size_list:
                _A4_width = size_list[0]
                _A4_height = size_list[1]
            if params["paper_size"] == "custom":
                _A4_width = float(params["page_width"]) * 300 / 25.4
                _A4_height = float(params["page_height"]) * 300 / 25.4

        if printer_type == "default":
            try:
                if sys.platform == "win32":
                    outputFile = f'-sOutputFile="%printer%{printer_name}"'
                    file_path = file_path.replace("\\", "\\\\")
                    gs_path = PrinterCore._GHOSTSCRIPT_PATH.replace("\\", "\\\\")
                    cmd = [
                        gs_path,
                        "-dPrinted",
                        "-dBATCH",
                        "-dNOPAUSE",
                        "-dNOSAFER",
                        "-sDEVICE=mswinpr2",
                        outputFile,
                        file_path,
                    ]

                    subprocess.call(cmd, shell=True)
            except Exception as e:
                raise e
        elif printer_type == "custom":
            try:
                if sys.platform == "win32":
                    # 构建 Ghostscript 命令参数
                    args = "-sDEVICE=mswinpr2 -dBATCH -dNOPAUSE -dFitPage -dQUIET -r300 "
                    # 横向打印时交换宽高
                    if params["orientation_type"] == "horizontal":
                        _A4_width, _A4_height = _A4_height, _A4_width

                    # 按比例缩放
                    scale = params["scale"]
                    if 10 < scale <= 200 and scale != 100:
                        _A4_width = _A4_width * scale / 100
                        _A4_height = _A4_height * scale / 100

                    orientation = f"-g{int(_A4_width)}x{int(_A4_height)} "
                    output_file = f'-sOutputFile="%printer%{printer_name}" '
                    copies = f"-dNumCopies={int(params['print_num'])} " if params["print_num"] else ""
                    abs_file_path = os.path.join(os.getcwd(), file_path).replace("\\", "\\\\")
                    file_arg = f'-f "{abs_file_path}"'

                    gs_path_replaced = PrinterCore._GHOSTSCRIPT_PATH.replace("\\", "\\\\")
                    ghostscript_cmd = f'"{gs_path_replaced}" {args}{orientation}{output_file}{copies}{file_arg}'
                    subprocess.call(ghostscript_cmd, shell=True)

            except Exception as e:
                raise e
        return True

    def print_img(self, printer_name: str, file_path: str, printer_type: str, **kwargs):
        """
        打印图片文件。
        支持默认和自定义打印参数。

        Args:
            printer_name (str): 打印机名称。
            file_path (str): 图片文件路径。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            bool: 打印是否成功。
        """
        defaults = {
            "paper_size": "A4",
            "print_num": 1,
            "scale": None,
            "margin_type": None,
            "margin": [-1, -1, -1, -1],
            "orientation_type": None,
            "page_weight": "",
            "page_height": "",
            "pages": None,
        }

        params = {**defaults, **kwargs}
        HORZRES = 8
        VERTRES = 10
        PHYSICALWIDTH = 110
        PHYSICALHEIGHT = 111

        try:
            hDC = win32ui.CreateDC()
            if hDC is None:
                raise ValueError("无法创建打印设备上下文")
            hDC.CreatePrinterDC(printer_name)
            printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
            printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
            image = Image.open(file_path)

            if printer_type == "default":
                if image.size[0] > image.size[1]:
                    image = image.rotate(90, expand=True)
                ratios = [1.0 * printable_area[0] / image.size[1], 1.0 * printable_area[0] / image.size[0]]
                scale = min(ratios)

                hDC.StartDoc(file_path)
                hDC.StartPage()

                dib = ImageWin.Dib(image)
                scaled_width, scaled_height = [int(scale * i) for i in image.size]
                x1 = int((printer_size[0] - scaled_width) / 2)
                y1 = int((printer_size[1] - scaled_height) / 2)
                x2 = x1 + scaled_width
                y2 = y1 + scaled_height
                dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))

                hDC.EndPage()
                hDC.EndDoc()

            elif printer_type == "custom":
                if params["orientation_type"] == "horizontal":
                    if image.size[1] > image.size[0]:
                        image = image.rotate(90, expand=True)
                elif params["orientation_type"] == "vertical":
                    if image.size[0] > image.size[1]:
                        image = image.rotate(90, expand=True)

                ratios = [1.0 * printable_area[0] / image.size[1], 1.0 * printable_area[0] / image.size[0]]
                printable_scale = min(ratios)

                hDC.StartDoc(file_path)
                hDC.StartPage()
                dib = ImageWin.Dib(image)

                scale = params["scale"]

                if not scale:
                    scale = 100

                scaled_width, scaled_height = [int((printable_scale * i) * (scale / 100)) for i in image.size]
                x1 = int((printer_size[0] * (scale / 100) - scaled_width) / 2)
                y1 = int((printer_size[1] * (scale / 100) - scaled_height) / 2)

                x2 = x1 + scaled_width
                y2 = y1 + scaled_height
                dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))

                hDC.EndPage()
                hDC.EndDoc()

            hDC.DeleteDC()
        except Exception as e:
            raise e
        return True

    @staticmethod
    def view_printer():
        """
        获取系统所有本地和网络连接的打印机名称列表。

        Returns:
            list: 打印机名称列表。
        """
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        printer_names = [printers[2] for printers in printers if printers[2]]
        return printer_names

    @staticmethod
    def get_printer_status():
        """
        获取默认打印机的状态码。

        Returns:
            int: 打印机状态码。
        """
        printer_name = win32print.GetDefaultPrinter()
        printer_handle = win32print.OpenPrinter(printer_name)
        status = win32print.GetPrinter(printer_handle, 2)
        print_status = status["Status"]
        return print_status

    @staticmethod
    def jobs_printer():
        """
        检查默认打印机是否有打印任务。

        Returns:
            bool|None: True-无任务，False-有任务，None-异常。
        """
        try:
            # 获取默认打印机的名称
            printer_name = win32print.GetDefaultPrinter()
            # 打开打印机句柄
            printer_handle = win32print.OpenPrinter(printer_name)
            # 枚举打印任务
            jobs = win32print.EnumJobs(printer_handle, 0, -1, 1)
            # 关闭打印机句柄
            win32print.ClosePrinter(printer_handle)
            # 检查是否有打印任务
            if not jobs:
                return True  # 没有任务
            else:
                return False  # 有任务

        except Exception as e:
            # 处理异常并打印错误信息
            print(f"发生错误: {e}")
            return None

    @staticmethod
    def generate_printer_task(printer_name="", print_file=None, printer_type="", file_type="", **kwargs):
        """
        生成打印任务队列。
        支持单文件或多文件批量打印。

        Args:
            printer_name (str): 打印机名称。
            print_file (str|list): 文件路径或文件列表。
            printer_type (str): 打印类型。
            **kwargs: 其他参数。

        Returns:
            queue.Queue: 打印任务队列。
        """
        task_queue = queue.Queue()
        if isinstance(print_file, str):
            task = PrinterCore._process_file(printer_name, print_file, printer_type, file_type, **kwargs)
            task_queue.put(task)
        elif isinstance(print_file, list):
            for file in print_file:
                task = PrinterCore._process_file(printer_name, file, printer_type, file_type, **kwargs)
                task_queue.put(task)
        return task_queue

    def parse_pages(self, page_string):
        """
        2, 6-10"表示打印第 2 页以及第 6 至第 10 页
        """
        pages = []
        page_ranges = page_string.split(",")  # 按逗号分割字符串，得到页码范围
        for page_range in page_ranges:
            if "-" in page_range:
                start, end = map(int, page_range.split("-"))  # 按照连字符分割页码范围的起始页和结束页
                pages.extend(range(start, end + 1))  # 将起始页到结束页的页码添加到列表中
            else:
                pages.append(int(page_range))  # 如果没有连字符，则将单个页码添加到列表中
        return pages

    def file_type_batch(self, file_type: str, print_file: list):
        """
        根据文件类型过滤批量打印的文件列表。

        Args:
            file_type (str): 文件类型。
            print_file (list): 文件路径列表。
        Returns:
            list: 过滤后的文件路径列表。
        """
        filtered_files = []
        for file in print_file:
            lower_suffix = file.lower()
            if (
                (file_type == FileType.WORD.value and lower_suffix.endswith((".doc", ".docx", ".wps")))
                or (file_type == FileType.EXCEL.value and lower_suffix.endswith((".xls", ".xlsx", ".et")))
                or (file_type == FileType.PDF.value and lower_suffix.endswith(".pdf"))
                or (
                    file_type == FileType.PICTURE.value
                    and any(lower_suffix.endswith(img) for img in PrinterCore.IMAGE_TYPES)
                )
            ):
                filtered_files.append(file)
        return filtered_files
