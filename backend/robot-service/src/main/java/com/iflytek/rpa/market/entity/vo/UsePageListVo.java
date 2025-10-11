package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

/**
 * 使用申请页面列表VO
 */
@Data
public class UsePageListVo {
    /**
     * 使用审核ID
     */
    private String id;
    /**
     * 机器人id
     */
    private String robotId;
    /**
     * 机器人名称
     */
    private String robotName;
    /**
     * 版本号
     */
    private String robotVersion;

    /**
     * 密级标识
     */
    private String securityLevel;

    /**
     * 申请人id
     */
    private String creatorId;

    /**
     * 申请人姓名
     */
    private String creatorName;
    /**
     * 申请人手机号
     */
    private String creatorPhone;
    /**
     * 申请人部门名
     */
    private String creatorDeptName;
    /**
     * 申请人部门id
     */
    private String creatorDeptId;

    /**
     * 提交审核时间
     */
    private String submitAuditTime;

    /**
     * 审核状态
     */
    private String status;
}
