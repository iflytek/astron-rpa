package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 根据手机号查询市场用户DTO
 *
 * @author system
 */
@Data
public class GetMarketUserByPhoneDto implements Serializable {
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

    private String keyword;
}
