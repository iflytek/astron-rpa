package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * 用户权益响应DTO
 *
 * @author system
 */
@Data
public class UserEntitlementDto implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 设计器权限
     */
    private Boolean moduleDesigner;

    /**
     * 执行器权限
     */
    private Boolean moduleExecutor;

    /**
     * 控制台权限
     */
    private Boolean moduleConsole;

    /**
     * 团队市场权限
     */
    private Boolean moduleMarket;
}
