package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.util.Date;

@Data
public class VersionInfo {
    Integer versionNum; // 版本号

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date createTime; // 发版时间
    Integer online; // 是否启用
}
