from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.baseline.config.config import load_config
from astronverse.report.report import Report


def get_version():
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Report, version=get_version())
    atomicMg.meta()
