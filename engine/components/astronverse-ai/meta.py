from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.ai.agent import Agent
from astronverse.ai.chat import ChatAI
from astronverse.ai.contract import ContractAI
from astronverse.ai.document import DocumentAI
from astronverse.ai.recruit import RecruitAI
from astronverse.baseline.config.config import load_config


def get_version():
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(ChatAI, version=get_version())
    atomicMg.register(DocumentAI, version=get_version())
    atomicMg.register(Agent, version=get_version())
    atomicMg.register(RecruitAI, version=get_version())
    atomicMg.register(ContractAI, version=get_version())
    atomicMg.meta()
