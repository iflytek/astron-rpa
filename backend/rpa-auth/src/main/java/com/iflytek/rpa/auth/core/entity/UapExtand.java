package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;
import java.util.Date;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/4 10:17
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class UapExtand extends TenantModeExtendDto implements Serializable {

    private static final long serialVersionUID = -542509006960020555L;

    /**
     * 扩展属性ID
     */
    private String id;

    /**
     * 属性名称
     */
    private String name;

    /**
     * 属性代码
     */
    private String nameCode;

    /**
     * 属性编码
     */
    private String code;

    /**
     * 数据类型0表示String,1表示int,2表示datetime
     */
    private Integer type;

    /**
     * 属性类型0表示用户 1表示机构
     */
    private Integer catalog;

    /**
     * 是否必填{0否 1是}
     */
    private Integer mandatory;

    /**
     * 组件类型
     */
    private String componentType;

    /**
     * 数据源
     */
    private String componentData;

    /**
     * 唯一性（0否 1是）
     */
    private Integer isUnique = 0;

    /**属性状态{0无效 1有效}
     *
     */
    private Integer status = 1;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 备注
     */
    private String remark;

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

    public String getNameCode() {
        return nameCode;
    }

    public void setNameCode(String nameCode) {
        this.nameCode = nameCode;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public Integer getType() {
        return type;
    }

    public void setType(Integer type) {
        this.type = type;
    }

    public Integer getCatalog() {
        return catalog;
    }

    public void setCatalog(Integer catalog) {
        this.catalog = catalog;
    }

    public Integer getMandatory() {
        return mandatory;
    }

    public void setMandatory(Integer mandatory) {
        this.mandatory = mandatory;
    }

    public String getComponentType() {
        return componentType;
    }

    public void setComponentType(String componentType) {
        this.componentType = componentType;
    }

    public String getComponentData() {
        return componentData;
    }

    public void setComponentData(String componentData) {
        this.componentData = componentData;
    }

    public Integer getIsUnique() {
        return isUnique;
    }

    public void setIsUnique(Integer isUnique) {
        this.isUnique = isUnique;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
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
