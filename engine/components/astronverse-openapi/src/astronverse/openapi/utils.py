import os
from pathlib import Path

from astronverse.openapi.error import BizException, EXCEL_WORKSHEET_ERROR
from openpyxl import Workbook


def write_to_excel(dst_file, dst_file_name, header_dict, json_data):
    """
    将从ai接口获取到的数据写入到本地excel中
    :param dst_file: 本地excel路径（文件夹）
    :param dst_file_name: 本地excel名称
    :param header_dict: excel的第一行标题，格式{"payer_name": "发票抬头", ...}
    :param json_data: 要写入到excel中的json数据，必须满足不含嵌套，格式固定为[{“发票抬头”: "科大讯飞", ...}, {“发票抬头”: "科大讯飞", ...}, ...]
    :return: 本地excel路径
    """
    if not os.path.splitext(dst_file_name)[1]:
        dst_file_name += ".xlsx"

    if not os.path.exists(dst_file):
        os.makedirs(dst_file)

    full_file_path = os.path.join(dst_file, dst_file_name)
    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise BizException(EXCEL_WORKSHEET_ERROR, "无法获取活动工作表")
    cols = []

    for title in header_dict.values():
        if title not in cols:
            cols.append(title)
    ws.append(cols)
    for line in json_data:
        row_data = []
        for title in cols:
            value = line.get(title)
            if isinstance(value, list):
                value = ",".join(value)
            row_data.append(value)
        ws.append(row_data)

    wb.save(full_file_path)
    return full_file_path


def generate_src_files(src_file, file_type="image"):
    """
    生成目标文件列表
    """
    files = []
    if os.path.exists(src_file):
        if os.path.isdir(src_file):
            for file in os.listdir(src_file):
                if file_type == "image":
                    if os.path.splitext(file)[1].lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                        files.append(os.path.join(src_file, file))
                else:
                    if file.startswith("~$"):
                        continue
                    file_path = os.path.join(src_file, file)
                    if os.path.isfile(file_path):
                        files.append(file_path)
        else:
            if file_type == "image":
                if os.path.splitext(src_file)[1].lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                    files.append(src_file)
            else:
                files.append(src_file)
    return files


def ensure_parent_dir(dst_file: str):
    Path(dst_file).mkdir(parents=True, exist_ok=True)


def write_text_file(dst_dir: str, dst_name: str, content: str, suffix: str = ".txt") -> str:
    ensure_parent_dir(dst_dir)
    if not os.path.splitext(dst_name)[1]:
        dst_name = f"{dst_name}{suffix}"
    full_path = os.path.join(dst_dir, dst_name)
    Path(full_path).write_text(content, encoding="utf-8")
    return full_path


def write_binary_file(dst_dir: str, dst_name: str, content: bytes, suffix: str) -> str:
    ensure_parent_dir(dst_dir)
    if not os.path.splitext(dst_name)[1]:
        dst_name = f"{dst_name}{suffix}"
    full_path = os.path.join(dst_dir, dst_name)
    Path(full_path).write_bytes(content)
    return full_path
