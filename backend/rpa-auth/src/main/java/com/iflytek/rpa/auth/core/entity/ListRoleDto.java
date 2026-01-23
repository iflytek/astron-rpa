package com.iflytek.rpa.auth.core.entity;

/**
 * 分页查询用户列表信息DTO
 * @author xqcao2
 *
 */
public class ListRoleDto extends PageQueryDto {

    /**
     * 角色ID
     */
    private String roleId;

    /**
     * 上级角色ID
     */
    private String parentRoleId;

    /**
     * 角色名称
     */
    private String roleName;

    /**
     * 应用ID
     */
    private String appId;

    /**
     * 应用编码
     */
    private String appCode;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 租户ID
     * 是为了兼容低版本 才加入此字段 请勿主动使用此字段
     */
    private String tenantId;

    public String getRoleId() {
        return roleId;
    }

    public void setRoleId(String roleId) {
        this.roleId = roleId;
    }

    public String getParentRoleId() {
        return parentRoleId;
    }

    public void setParentRoleId(String parentRoleId) {
        this.parentRoleId = parentRoleId;
    }

    public String getRoleName() {
        return roleName;
    }

    public void setRoleName(String roleName) {
        this.roleName = roleName;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getAppCode() {
        return appCode;
    }

    public void setAppCode(String appCode) {
        this.appCode = appCode;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }
}
