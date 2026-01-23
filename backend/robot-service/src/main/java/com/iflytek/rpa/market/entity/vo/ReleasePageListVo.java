package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

/**
 * 发布页面列表VO
 */
@Data
public class ReleasePageListVo {
    /**
     * 上架审核ID
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
     * 所有者id
     */
    private String creatorId;
    /**
     * 所有者名称
     */
    private String creatorName;

    /**
     * 所有者手机号
     */
    private String creatorPhone;

    /**
     * 提交审核时间
     */
    private String submitAuditTime;

    /**
     * 审核状态
     */
    private String status;

    /**
     * 密级标识
     */
    private String securityLevel;
    /**
     * 允许使用的部门ID列表
     */
    private String allowedDept;
}

