package com.iflytek.rpa.auth.core.entity;

/**
 * @author: boqiu3
 * @date: 2023/4/21 9:41
 * @description: 用作多租户模式下，接口参数拓展使用
 */
public class TenantModeExtendDto {

    /**
     * 租户id
     */
    private String tenantId;

    /**
     *
     */
    private String requestUrl;

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public String getRequestUrl() {
        return requestUrl;
    }

    public void setRequestUrl(String requestUrl) {
        this.requestUrl = requestUrl;
    }
}
