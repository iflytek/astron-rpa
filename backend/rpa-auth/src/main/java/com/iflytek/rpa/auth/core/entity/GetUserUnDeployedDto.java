package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 获取未部署用户列表查询DTO
 *
 * @author system
 */
@Data
public class GetUserUnDeployedDto implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 市场ID
     */
    private String marketId;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 应用ID
     */
    private String appId;

    /**
     * 手机号（用于模糊查询）
     */
    private String phone;
}
