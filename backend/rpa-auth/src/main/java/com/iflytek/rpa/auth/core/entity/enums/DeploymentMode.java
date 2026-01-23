package com.iflytek.rpa.auth.core.entity.enums;

/**
 * 部署模式枚举
 */
public enum DeploymentMode {
    /**
     * SaaS化部署 - 使用讯飞账号认证
     */
    SAAS("saas", "SaaS化部署"),

    /**
     * 私有化部署 - 企业SSO认证
     */
    PRIVATE_ENTERPRISE("private-enterprise", "私有化部署-企业SSO"),

    /**
     * 私有化部署 - 内部UAP认证
     */
    PRIVATE_UAP("private-uap", "私有化部署-内部UAP"),

    /**
     * Casdoor 部署
     */
    CASDOOR("casdoor", "Casdoor 部署");

    private final String code;
    private final String description;

    DeploymentMode(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    public static DeploymentMode fromCode(String code) {
        for (DeploymentMode mode : values()) {
            if (mode.code.equalsIgnoreCase(code)) {
                return mode;
            }
        }
        throw new IllegalArgumentException("未知的部署模式: " + code);
    }
}
