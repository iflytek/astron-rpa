package com.iflytek.rpa.common.feign.entity.dto;

public class TenantModeExtendDto {
    private String tenantId;
    private String requestUrl;

    public TenantModeExtendDto() {}

    public String getTenantId() {
        return this.tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public String getRequestUrl() {
        return this.requestUrl;
    }

    public void setRequestUrl(String requestUrl) {
        this.requestUrl = requestUrl;
    }
}
