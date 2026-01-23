package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 获取市场用户列表查询DTO
 *
 * @author system
 */
@Data
public class GetMarketUserListDto implements Serializable {
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
     * 登录名（用于模糊查询）
     */
    private String userName;

    /**
     * 真实姓名（用于模糊查询）
     */
    private String realName;

    /**
     * 排序字段（如update_time）
     */
    private String sortBy;

    /**
     * 排序类型（descend或ascend）
     */
    private String sortType;

    /**
     * 页码
     */
    private Integer pageNo;

    /**
     * 每页大小
     */
    private Integer pageSize;
}
