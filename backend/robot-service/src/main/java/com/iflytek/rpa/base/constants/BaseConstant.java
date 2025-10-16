package com.iflytek.rpa.base.constants;

public class BaseConstant {

    public static final String TYPE_CV = "cv";

    public static final String TYPE_COMMON = "common";

    public static final String DEFAULT_GROUP = "默认分组";

    public static final String PROCESS_TYPE_PROCESS = "process";

    public static final String PROCESS_TYPE_MODULE = "module";

    public static final Integer ATOM_LIST_MAX_SIZE = 500;

    public static final Integer INIT_VERSION_NUM = 1000000;

    public static final Integer MAJOR_SIZE = 1000000;

    public static final Integer MINOR_SIZE = 1000;

    public static final Integer BATCH_SIZE = 50;

    // 实际数据库中medium text 支持的最大长度是 16777215
    public static final Integer CONTENT_MAX_LENGTH = 10000000;

    public static final Integer MAX_PROCESS_SIZE = 14;

    public static final String MODULE_INIT_CONTENT =
            "from typing import Any\n" + "from astronverse.workflowlib.helper import Helper, print, logger\n"
                    + "\n"
                    + "\n"
                    + "def main(*args, **kwargs) -> Any:\n"
                    + "    h = Helper(**kwargs)\n"
                    + "    params = h.params()\n"
                    + "\n"
                    + "    # 打印所有的变量key\n"
                    + "    logger.info(params.keys())\n"
                    + "\n"
                    + "    return True";
}
