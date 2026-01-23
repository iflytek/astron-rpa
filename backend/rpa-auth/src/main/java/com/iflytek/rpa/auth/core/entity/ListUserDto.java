package com.iflytek.rpa.auth.core.entity;

import java.util.List;

/**
 * 分页查询用户列表信息DTO
 * @author xqcao2
 *
 */
public class ListUserDto extends PageQueryDto {

    /**
     * 用户ID 集合  用于查询指定用户ID的用户
     */
    private List<String> userIds;

    /**
     * 角色ID 集合  用于查询角色下的用户
     */
    private List<String> roleIdList;

    /**
     * 机构ID 用于过滤某个机构下的用户
     */
    private String orgId;

    /**
     * 登录名
     */
    private String loginName;

    /**
     * 姓名
     */
    private String name;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 电话
     */
    private String phone;

    /**
     * 状态 账户状态{0停用 1启用}
     */
    private Integer status = 1;

    /**
     * 是否查询总数(低版本时 使用)
     */
    private boolean queryPageCount = false;

    public List<String> getUserIds() {
        return userIds;
    }

    public void setUserIds(List<String> userIds) {
        this.userIds = userIds;
    }

    public List<String> getRoleIdList() {
        return roleIdList;
    }

    public void setRoleIdList(List<String> roleIdList) {
        this.roleIdList = roleIdList;
    }

    public String getOrgId() {
        return orgId;
    }

    public void setOrgId(String orgId) {
        this.orgId = orgId;
    }

    public String getLoginName() {
        return loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public boolean isQueryPageCount() {
        return queryPageCount;
    }

    public void setQueryPageCount(boolean queryPageCount) {
        this.queryPageCount = queryPageCount;
    }
}
