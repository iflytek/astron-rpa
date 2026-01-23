package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

@Data
public class MyApplicationPageListDto {
    /**
     * 机器人名称
     */
    private String robotName;

    /**
     * 申请类型: release(上架申请)/use(使用申请)
     */
    private String applicationType;

    /**
     * 申请状态: pending(待审核)/approved(已通过)/rejected(未通过)/canceled(已撤销)
     */
    private String status;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 用户id
     */
    private String userId;

    /**
     * 页码
     */
    private Integer pageNo;

    /**
     * 每页大小
     */
    private Integer pageSize;
}
