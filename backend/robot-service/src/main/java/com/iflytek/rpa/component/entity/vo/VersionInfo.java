package com.iflytek.rpa.component.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.util.Date;

@Data
public class VersionInfo {
    Integer version; // 版本号

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date createTime; // 创建时间
    String updateLog; // 更新日志
}
