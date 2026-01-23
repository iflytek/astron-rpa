package com.iflytek.rpa.auth.core.entity;

/**
 * 根据角色ID 分页查询用户列表信息DTO
 *
 * 注意：仅仅当前角色  不涉及子角色
 * @author xqcao2
 *
 */
public class ListUserByRoleDto extends PageQueryDto {

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 角色ID 仅仅查询当前角色 不包含子角色
     */
    private String roleId;

    /**
     * 机构ID 根据机构ID过滤 仅当前机构  不包含子机构
     */
    private String orgId;

    /**
     * 检索内容  登录名 姓名
     */
    private String keyWord;

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public String getRoleId() {
        return roleId;
    }

    public void setRoleId(String roleId) {
        this.roleId = roleId;
    }

    public String getOrgId() {
        return orgId;
    }

    public void setOrgId(String orgId) {
        this.orgId = orgId;
    }

    public String getKeyWord() {
        return keyWord;
    }

    public void setKeyWord(String keyWord) {
        this.keyWord = keyWord;
    }
}
