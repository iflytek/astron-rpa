"""Agent related atomic operations and workflow integration for AI interactions."""

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem, AtomicLevel
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.ai import DifyFileTypes
from astronverse.ai.api.dify import Dify
from astronverse.ai.api.xcagent import xcAgent


class Agent:
    """High-level wrapper for interacting with Dify and xcAgent flows via atomic tasks."""

    @staticmethod
    @atomicMg.atomic(
        "Agent",
        inputList=[
            atomicMg.param("user", types="Str"),
            atomicMg.param("app_url", types="Str", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param("app_token", types="Str"),
            atomicMg.param("variable_name", types="Str", required=False),
            atomicMg.param(
                "variable_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.variable_value.show",
                        expression="return $this.file_flag.value != true",
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "file_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_type.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("dify_result", types="Str")],
    )
    def call_dify(
        user: str,
        app_token: str,
        app_url: str = "https://api.dify.ai/v1",
        file_flag: bool = False,
        variable_name: str = "",
        variable_value: str = "",
        file_path: PATH = "",
        file_type: DifyFileTypes = DifyFileTypes.DOCUMENT,
    ):
        # 使用示例

        # file_path = r"C:\Users\zyzhou23.IFLYTEK\Downloads\写出好的代码 -经验篇.md"
        # user = "drbruce"
        # dify = Dify("app-MgbOPD6ZYA6mSyip1w4h74wU")

        dify = Dify(app_token, app_url)
        file_id = None
        # 上传文件
        if file_flag:
            file_id = dify.upload_file(file_path, user)
        # file_id = "a17f9f77-4eb9-461b-a62c-1f302c806187"
        if file_id:
            # 文件上传成功，继续运行工作流
            # result = dify.run_workflow(user, "input_files", True, file_id, "document")
            result = dify.run_workflow(user, variable_name, file_flag, file_id, file_type.value)
            logger.info(result)
        else:
            result = dify.run_workflow(user, variable_name, file_flag, variable_value, file_type.value)
            logger.info(result)
        return result

    @staticmethod
    @atomicMg.atomic(
        "Agent",
        inputList=[
            atomicMg.param("user", types="Str"),
            atomicMg.param("app_url", types="Str", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param("app_token", types="Str"),
            atomicMg.param("variable_name", types="Str", required=False),
            atomicMg.param("variable_value", types="Str", required=False),
            atomicMg.param(
                "variable_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.variable_value.show",
                        expression="return $this.file_flag.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "file_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_type.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("dify_result", types="Str")],
    )
    def call_dify_chatflow(
        user: str,
        app_token: str,
        app_url: str = "https://api.dify.ai/v1",
        query: str = "",
        file_flag: bool = False,
        variable_name: str = "",
        variable_value: str = "",
        file_path: PATH = "",
        file_type: DifyFileTypes = DifyFileTypes.DOCUMENT,
    ):
        # 使用示例

        # file_path = r"C:\Users\zyzhou23.IFLYTEK\Downloads\写出好的代码 -经验篇.md"
        # user = "drbruce"
        # dify = Dify("app-MgbOPD6ZYA6mSyip1w4h74wU")

        dify = Dify(app_token, app_url)
        file_id = None
        # 上传文件
        if file_flag:
            file_id = dify.upload_file(file_path, user)
        # file_id = "a17f9f77-4eb9-461b-a62c-1f302c806187"
        if file_id:
            # 文件上传成功，继续运行工作流
            # result = dify.run_workflow(user, "input_files", True, file_id, "document")
            result = dify.run_chatflow(user, query, variable_name, file_flag, file_id, file_type.value)
            logger.info(result)
        else:
            result = dify.run_chatflow(user, query, variable_name, file_flag, variable_value, file_type.value)
            logger.info(result)
        return result

    @staticmethod
    @atomicMg.atomic(
        "Agent",
        inputList=[
            atomicMg.param("app_key", types="Str"),
            atomicMg.param("app_secret", types="Str"),
            atomicMg.param("flow_id", types="Str"),
            atomicMg.param(
                "input_value",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
            ),
            atomicMg.param("variable_name", types="Str", required=False),
            atomicMg.param("variable_value", types="Str", required=False),
            atomicMg.param(
                "variable_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.variable_value.show",
                        expression="return $this.file_flag.value != true",
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("xcagent_result", types="Str")],
    )
    def call_xcagent(
        api_key: str,
        api_secret: str,
        flow_id: str,
        input_value: str = "",
        file_flag: bool = False,
        variable_name: str = "",
        variable_value: str = "",
        file_path: PATH = "",
    ):
        xc_agent = xcAgent(api_key, api_secret)
        xc_agent_result = xc_agent.run_flow(
            flow_id, input_value, False, file_flag, variable_name, variable_value, file_path
        )
        return xc_agent_result
