package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-01 10:14
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class AppApplication {
    private Long id;

    private String robotId;

    private Integer robotVersion;

    private String applicationType;

    private String status;

    private String securityLevel;

    private String allowedDept;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date expireTime;

    private String auditOpinion;

    private String creatorId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    private String updaterId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    private Integer deleted;

    private String tenantId;

    private Integer clientDeleted;

    private Integer cloudDeleted;

    private Integer defaultPass;

    /**
     * 团队市场id，用于第一次发起上架申请，审核通过后自动分享到该市场
     */
    @TableField(exist = false)
    private String marketId;

    /**
     * 市场信息JSON字符串，包含marketIdList、editFlag、category等信息
     */
    private String marketInfo;
    /**
     * 发版信息JSON字符串
     */
    private String publishInfo;
}
