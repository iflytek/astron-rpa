package com.iflytek.rpa.base.entity.dto;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import com.alibaba.fastjson.JSONObject;
import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;
import lombok.experimental.Accessors;

@Data
public class CSmartComponentDto {

    /**
     * 智能组件Id
     */
    private String smartId;

    /**
     * 组件版本号
     */
    private Integer version;

    /**
     * 组件类型 web_auto | data_process
     */
    private String smartType;

    /**
     * 组件要保存的数据
     */
    private SmartDetail detail;

    /**
     * 机器人Id
     */
    private String robotId;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 当前模式
     */
    @NotBlank(message = "运行位置不能为空")
    private String mode = EDIT_PAGE;

    @Data
    @Accessors(chain = true)
    public static class SmartDetail {
        /**
         * 版本列表
         */
        private List<JSONObject> versionList;
    }
}
