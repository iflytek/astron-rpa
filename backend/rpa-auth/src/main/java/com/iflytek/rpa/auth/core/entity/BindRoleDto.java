package com.iflytek.rpa.auth.core.entity;

import java.util.List;

/**
 * 绑定角色DTO
 * @author xqcao2
 *
 */
public class BindRoleDto {

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 角色列表
     */
    private List<String> roleIdList;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public List<String> getRoleIdList() {
        return roleIdList;
    }

    public void setRoleIdList(List<String> roleIdList) {
        this.roleIdList = roleIdList;
    }
}
