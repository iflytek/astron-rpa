package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

/**
 * 使用申请页面列表VO
 */
@Data
public class MyApplicationPageListVo {
    /**
     * 使用审核ID
     */
    private String id;

    /**
     * 机器人id
     */
    private String robotId;
    /**
     * 机器人版本
     */
    private String robotVersion;
    /**
     * 机器人名称
     */
    private String robotName;

    /**
     * 密级标识
     */
    private String securityLevel;

    /**
     * 提交审核时间
     */
    private String submitAuditTime;

    /**
     * 审核意见
     */
    private String auditOpinion;
    /**
     * 申请类型: release(上架申请)/use(使用申请)
     */
    private String applicationType;
    /**
     * 申请状态: pending(待审核)/approved(已通过)/rejected(未通过)/canceled(已撤销)
     */
    private String status;
}
