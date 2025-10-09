import json
import os


def generate_local_name(exist_list: list, rename: str):
    base, extension = os.path.splitext(rename)
    counter = 1
    new_name = f"{base}({counter}){extension}"
    while new_name in exist_list:
        counter += 1
        new_name = f"{base}({counter}){extension}"
    return new_name


def get_file_list(paths_string: str):
    """
    处理上传的多个文件/文件夹
    """
    file_list = [path.strip() for path in paths_string.split(",")]
    return file_list


def is_json(data: str):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def file_is_exist(file_path: str):
    """
    判断文件是否存在
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)


def folder_is_exist(folder_path: str):
    """
    判断文件夹是否存在
    """
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def get_exist_files(folder_path: str):
    return os.listdir(os.path.abspath(folder_path))
