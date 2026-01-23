package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;
import java.util.Date;

/**
 * @desc: 角色实体类
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/24 16:22
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class Role implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 1L;

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
     * 应用名称
     */
    private String appName;

    /**
     * 上级角色 ID
     */
    private String higherRole;

    /**
     * 上级角色名称
     */
    private String higherName;

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

    /**
     * 首级角色id
     */
    private String firstLevelId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

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

    public String getAppName() {
        return appName;
    }

    public void setAppName(String appName) {
        this.appName = appName;
    }

    public String getHigherRole() {
        return higherRole;
    }

    public void setHigherRole(String higherRole) {
        this.higherRole = higherRole;
    }

    public String getHigherName() {
        return higherName;
    }

    public void setHigherName(String higherName) {
        this.higherName = higherName;
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

    public String getFirstLevelId() {
        return firstLevelId;
    }

    public void setFirstLevelId(String firstLevelId) {
        this.firstLevelId = firstLevelId;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }
}
