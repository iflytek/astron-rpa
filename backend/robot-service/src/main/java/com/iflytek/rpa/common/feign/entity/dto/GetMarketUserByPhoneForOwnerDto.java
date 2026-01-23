package com.iflytek.rpa.common.feign.entity.dto;

import java.io.Serializable;
import lombok.Data;

/**
 * 根据手机号查询市场中的用户DTO（用于市场所有者）
 *
 * @author system
 */
@Data
public class GetMarketUserByPhoneForOwnerDto implements Serializable {
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
     * 手机号（用于模糊查询）
     */
    private String phone;

    /**
     * 当前用户ID（用于排除自己）
     */
    private String userId;
}
