from astronverse.actionlib.report import IReport, report

logger: IReport = report


def print(*args, sep=" ", end="\n"):
    output = sep.join(str(arg) for arg in args)
    output += end
    logger.info(output)
