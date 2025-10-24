from astronverse.actionlib.report import IReport, report

logger: IReport = report


def print(*args, sep=" ", end=""):
    output = sep.join(str(arg) for arg in args)
    output += end
    logger.info(output)
