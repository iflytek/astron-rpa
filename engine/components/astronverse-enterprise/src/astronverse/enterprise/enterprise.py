"""Enterprise module"""

import json
import os
import urllib.parse
from pathlib import Path

import requests
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH, Ciphertext
from astronverse.baseline.logger.logger import logger
from astronverse.enterprise.error import *


class Enterprise:
    """Enterprise class"""

    @staticmethod
    @atomicMg.atomic(
        "Enterprise",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("upload_result", types="Str")],
    )
    def upload_to_sharefolder(file_path: PATH = ""):
        """Upload file to shared folder"""
        upload_url = "http://127.0.0.1:{}/api/resource/file/shared-file-upload".format(
            atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
        )
        update_info_url = "http://127.0.0.1:{}/api/robot/robot-shared-file/addSharedFileInfo".format(
            atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
        )
        # 检查文件是否存在
        if not (os.path.exists(file_path) and os.path.isfile(file_path)):
            return BaseException(PATH_INVALID_FORMAT.format(file_path), "请重新输入正确的文件路径")

        try:
            # 准备文件上传
            with open(file_path, "rb") as file:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        file,
                        "application/octet-stream",
                    )
                }
                data = {"fileId": "", "tags": ""}
                # 发送POST请求
                response = requests.post(upload_url, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    logger.info(f"请求返回值：{response.text}")
                    inner_data = json.loads(response.text)
                    if inner_data.get("code") in ["999999", "500000"]:
                        raise BaseException(
                            FILE_UPLOAD_FAILED_FORMAT.format(response.text),
                            "可能用了不支持的扩展名！",
                        )
                    info_data = {
                        "fileId": inner_data.get("data").get("fileid"),
                        "fileType": inner_data.get("data").get("type"),
                        "fileName": inner_data.get("data").get("fileName"),
                        "tags": [],
                    }
                    info_response = requests.post(update_info_url, json=info_data, timeout=30)
                    if info_response.status_code == 200:
                        logger.info(info_response.text)
                        if info_response.json().get("code") != "000000":
                            raise BaseException(
                                FILE_UPLOAD_FAILED_FORMAT.format(info_response.json().get("message")),
                                "文件已存在或更新文件信息失败！",
                            )
                        return "上传成功"
                    else:
                        logger.info(
                            f"上传成功，但更新文件信息失败，状态码：{info_response.status_code}，响应：{info_response.text}"
                        )
                        raise BaseException(
                            FILE_UPLOAD_FAILED_FORMAT.format(info_response.text),
                            "请检查更新文件信息接口！",
                        )
                else:
                    logger.info(f"上传失败，状态码：{response.status_code}，响应：{response.text}")
                    raise BaseException(
                        FILE_UPLOAD_FAILED_FORMAT.format(response.text),
                        "请检查上传接口！",
                    )
        except Exception as e:
            logger.error(f"上传过程中发生错误：{str(e)}")
            raise BaseException(FILE_UPLOAD_FAILED_FORMAT.format(e), "")

    @staticmethod
    @atomicMg.atomic(
        "Enterprise",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(type=AtomicFormType.REMOTEFOLDERS.value),
            ),
            atomicMg.param(
                "save_folder",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
        outputList=[atomicMg.param("download_result", types="Str")],
    )
    def download_from_sharefolder(file_path: int, save_folder: PATH = ""):
        """Download file from shared folder"""
        download_url = "http://127.0.0.1:{}/api/resource/file/download".format(
            atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
        )
        # 检查 save_folder 路径是否是绝对路径
        if not Path(save_folder).is_absolute():
            raise Exception(f"文件夹路径错误：{save_folder} 不是绝对路径")
        # 检查保存文件夹是否存在，如果不存在则创建
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 检查保存路径是否为目录
        if not os.path.isdir(save_folder):
            raise Exception(f"文件夹路径错误：{save_folder} 不是文件夹路径")

        try:
            params = {"fileId": file_path}
            response = requests.get(download_url, params=params, timeout=30, stream=True)

            # 检查响应状态
            if response.status_code == 200:
                # 从响应头中获取文件名，如果没有则使用默认名称
                content_disposition = response.headers.get("content-disposition", "")
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[1].strip('"')
                    # 对文件名进行URL解码，解决中文文件名问题
                    try:
                        filename = urllib.parse.unquote(filename)
                    except Exception as e:
                        logger.info(f"解码失败：{e}")
                        pass  # 如果解码失败，使用原始文件名
                else:
                    filename = f"downloaded_file_{file_path}"

                # 构建完整的保存路径
                save_path = os.path.join(save_folder, filename)
                # 文件已存在，重命名文件
                if os.path.exists(save_path):
                    base, ext = os.path.splitext(filename)
                    count = 1
                    while os.path.exists(save_path):
                        new_filename = f"{base}({count}){ext}"
                        save_path = os.path.join(save_folder, new_filename)
                        count += 1
                # 保存文件
                with open(save_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

                logger.info(f"下载成功：文件已保存到 {save_path}")
                return save_path
            else:
                logger.error(f"下载失败，状态码：{response.status_code}，响应：{response.text}")
                raise BaseException(
                    FILE_DOWNLOAD_FAILED_FORMAT.format(response.text),
                    "请检查下载接口！",
                )
        except Exception as e:
            logger.error(f"下载过程中发生错误：{str(e)}")
            raise BaseException(FILE_UPLOAD_FAILED_FORMAT.format(e), "")

    # 获取远程变量
    @staticmethod
    @atomicMg.atomic(
        "Enterprise",
        inputList=[
            atomicMg.param(
                "shared_variable",
                types="Dict",
                formType=AtomicFormTypeMeta(type=AtomicFormType.REMOTEPARAMS.value),
            ),
        ],
        outputList=[
            atomicMg.param("variable_data", types="Dict"),
        ],
    )
    def get_shared_variable(shared_variable: dict):
        """
        Get shared variable from remote
        """
        sub_var_list = shared_variable.get("subVarList", [])
        if not sub_var_list:
            return None
        res = {}
        for sub_var in sub_var_list:
            if sub_var["encrypt"]:
                c = Ciphertext(sub_var.get("varValue"))
                c.set_key(sub_var.get("key"))
                res[sub_var.get("varName")] = c
            else:
                res[sub_var.get("varName")] = sub_var.get("varValue")
        return res
