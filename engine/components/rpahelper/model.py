from typing import Any

from rpahelper.helper import Helper


def main(*args, **kwargs) -> Any:
    h = Helper(**kwargs)
    logger = h.logger()
    params = h.params()

    return True
