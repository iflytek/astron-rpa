package com.iflytek.rpa.example.constants;

import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.base.entity.CParam;
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
            put("c_element", CElement.class);
            put("c_group", CGroup.class);
            put("c_param", CParam.class);
        }
    };

    public static final String EXAMPLE_USER_NAME = "example-user";

    public static final String WORKFLOWS_UPSERT_URL = "http://rpa-openapi:6699/workflows/upsert";
}
