def param(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if not k.startswith("__")}