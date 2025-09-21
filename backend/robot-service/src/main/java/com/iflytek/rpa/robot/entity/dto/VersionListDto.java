package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class VersionListDto {
    String robotId; // 机器人id

    Integer sortType = 1; // 默认根据版本号逆序排序 0:asc 1:desc

    Long pageNo; // 页数

    Long pageSize; // 页面大小
}
