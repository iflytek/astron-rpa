package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class ExecuteListDto {
    String name; // 机器人名称

    String sortType = "desc"; // asc desc

    Long pageNo; // 页数

    Long pageSize; // 页面大小
}
