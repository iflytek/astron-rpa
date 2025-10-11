package com.iflytek.rpa.monitor.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class BaseDto {

    private String tenantId;

    private String deptId;

    /**
     * 部门全路径id
     */
    private String deptIdPath;

    /**
     * 截止时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date countTime;

    /**
     * 用于趋势图的开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date startTime;
    /**
     * 用于趋势图的结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date endTime;

    private List<String> deptIdPathList;
}
