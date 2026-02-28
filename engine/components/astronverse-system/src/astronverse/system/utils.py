import os


def linux_open_folder(folder_path: str = ""):
    import subprocess

    subprocess.Popen(
        ["xdg-open", folder_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # Linux 脱离终端会话
        close_fds=True,  # 关闭无用 fd
    )


def windows_open_folder(folder_path: str = ""):
    return os.startfile(folder_path)


def get_file_name_only(file_path: str = "") -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def folder_is_exists(folder_path: str = "") -> bool:
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def generate_copy(target_path: str = "", target_name: str = ""):
    base, extension = os.path.splitext(target_name)
    counter = 1
    new_name = f"{base}({counter}){extension}"
    new_path = os.path.join(target_path, new_name)
    while os.path.exists(new_path):
        counter += 1
        new_name = f"{base}({counter}){extension}"
        new_path = os.path.join(target_path, new_name)
    return new_path


def get_file_encoding_type(file_path: str = "") -> str:
    """
    获取文件编码类型，获取失败时使用默认编码 utf-8
    """
    with open(file_path, "rb") as f:
        try:
            raw_data = f.read()
            from charset_normalizer import from_bytes

            encoding = from_bytes(raw_data).best().encoding
            if encoding is None:
                encoding = "utf-8"
        except Exception as e:
            encoding = "utf-8"
    return encoding


def convert_time_format(input_time: float = 0) -> str:
    from datetime import datetime

    convert_time = datetime.fromtimestamp(input_time)
    return convert_time.strftime("%Y-%m-%d %H:%M:%S")


def list_to_excel(path_list: list = None, excel_path: str = ""):
    import pandas as pd

    data = {
        "序号": range(1, len(path_list) + 1),
        "名称": [os.path.basename(path) for path in path_list],
        "路径": path_list,
    }
    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)


def get_exe_path():
    atoms_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    driver_path = os.path.join(
        atoms_dir, "astronverse.input", "src", "astronverse.input", "VK", "bin", "debug", "VK.exe"
    )
    return driver_path


def get_files_in_folder(folder_path: str = "", general=False) -> list:
    """
    获取文件夹下所有文件列表
    Args:
        folder_path: 文件夹路径
        general: 是否包含隐藏文件 False 包含 True 不包含 默认False
    """
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if general:
            files = [f for f in files if not f.startswith(".") and not f.startswith("~$")]
        return files
    except Exception:
        from astronverse.system.error import BizException, FILE_LIST_ERROR
        raise BizException(FILE_LIST_ERROR, f"获取文件夹下文件列表失败，文件夹路径：{folder_path}")


def file_is_exists(file_path: str = "") -> bool:
    return os.path.exists(file_path) and os.path.isfile(file_path)


def path_join(*paths: str) -> str:
    return os.path.join(*paths)
