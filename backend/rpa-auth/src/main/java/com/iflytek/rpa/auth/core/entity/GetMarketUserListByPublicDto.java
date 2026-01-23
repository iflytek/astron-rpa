package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 获取公共市场用户列表查询DTO
 *
 * @author system
 */
@Data
public class GetMarketUserListByPublicDto implements Serializable {
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
     * 当前用户ID（用于排除自己）
     */
    private String nowUserid;

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
