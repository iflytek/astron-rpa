package com.iflytek.rpa.example.constants;

import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import java.util.HashMap;
import java.util.Map;

public class ExampleConstants {

    // 类型与业务表的映射常量
    public static final Map<String, Class<?>> TYPE_BUSINESS_CLASS_MAP = new HashMap<String, Class<?>>() {
        {
            put("robot_design", RobotDesign.class);
            put("robot_execute", RobotExecute.class);
            put("robot_version", RobotVersion.class);
            put("c_process", CProcess.class);
        }
    };

    public static final String EXAMPLE_USER_NAME = "example-user";

    public static final String WORKFLOWS_UPSERT_URL = "http://openapi-service:8020/workflows/upsert";
}
