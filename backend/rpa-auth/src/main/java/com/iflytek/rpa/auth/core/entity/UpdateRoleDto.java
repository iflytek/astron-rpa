package com.iflytek.rpa.auth.core.entity;

/**
 * 更新角色DTO
 * @author xqcao2
 *
 */
public class UpdateRoleDto {

    /**
     * 主键id
     */
    private String id;

    /**
     * 角色名称
     */
    private String name;

    /**
     * 角色编码
     */
    private String code;

    /**
     * 角色状态 角色状态{0停用 1启用}
     */
    private Integer status = 1;

    /**
     * 应用id
     */
    private String appId;

    /**
     * 上级角色 ID
     */
    private String higherRole;

    /**
     * 排序字段
     */
    private Integer sort = 1;

    /**
     * 备注
     */
    private String remark;

    /**
     * 该角色下菜单与功能的绑定策略,1:强绑定，0：非强绑定
     */
    private Integer isMustBind = 1;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getHigherRole() {
        return higherRole;
    }

    public void setHigherRole(String higherRole) {
        this.higherRole = higherRole;
    }

    public Integer getSort() {
        return sort;
    }

    public void setSort(Integer sort) {
        this.sort = sort;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    public Integer getIsMustBind() {
        return isMustBind;
    }

    public void setIsMustBind(Integer isMustBind) {
        this.isMustBind = isMustBind;
    }
}
