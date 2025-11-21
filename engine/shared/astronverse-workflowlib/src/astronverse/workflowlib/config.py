from astronverse.baseline.config.config import load_config


def config(config_path="project.json"):
    return load_config(config_path)
