package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import java.util.List;
import lombok.Data;

/**
 * 根据用户ID列表查询租户用户DTO
 *
 * @author system
 */
@Data
public class GetMarketTenantUserListDto implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 用户ID列表（从AppMarketUser的creatorId中提取）
     */
    private List<String> userIdList;
}
