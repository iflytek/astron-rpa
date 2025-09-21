package com.iflytek.rpa.base.entity.dto;

import com.iflytek.rpa.base.entity.CProcess;
import lombok.Data;

@Data
public class CProcessDto extends CProcess {

    private String robotId;

    private String processId;

    private String processJson;

    /**
     * 指定工程在哪个阶段运行
     */
    private String mode;
}
