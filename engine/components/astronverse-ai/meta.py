import toml
from astronverse.ai.agent import Agent
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.ai.chat import ChatAI
from astronverse.ai.contract import ContractAI
from astronverse.ai.document import DocumentAI
from astronverse.ai.recruit import RecruitAI


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.default_value["atomic"] = {
        "icon": "icon-list-math-operation",
    }
    config.set_config_file("config.yaml")
    atomicMg.register(ChatAI, version=get_version())
    atomicMg.register(DocumentAI, version=get_version())
    atomicMg.register(Agent, version=get_version())
    atomicMg.register(RecruitAI, version=get_version())
    atomicMg.register(ContractAI, version=get_version())
    atomicMg.meta()
