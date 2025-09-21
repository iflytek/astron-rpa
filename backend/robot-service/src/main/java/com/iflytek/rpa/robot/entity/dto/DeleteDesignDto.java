package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class DeleteDesignDto {

    // 设计器机器人删除情况分类：1： 设计器 ，2：设计器 执行器，3：设计器 执行期 被计划任务引用
    // 执行器机器人删除情况分类：1： 执行器，3：执行期 被计划任务引用
    Integer situation;

    // 机器人id
    String robotId;

    // 多个引用该机器人的计划任务id，用逗号隔开，只有第三种情况需要。
    String taskIds;
}
