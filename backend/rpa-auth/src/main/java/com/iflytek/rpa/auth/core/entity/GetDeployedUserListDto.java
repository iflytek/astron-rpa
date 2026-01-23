package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 获取已部署用户列表查询DTO
 *
 * @author system
 */
@Data
public class GetDeployedUserListDto implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 应用ID
     */
    private String appId;

    /**
     * 市场ID
     */
    private String marketId;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 真实姓名（用于模糊查询）
     */
    private String realName;

    /**
     * 页码
     */
    private Integer pageNo;

    /**
     * 每页大小
     */
    private Integer pageSize;
}
