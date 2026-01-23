package com.iflytek.rpa.common.feign.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;
import java.util.Date;

/**
 * @desc: 组织实体类
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/24 17:39
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class Org implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 1L;

    /**
     * 机构id
     */
    private String id;

    /**
     * 机构名称
     */
    private String name;

    /**
     * 机构编码
     */
    private String code;

    /**
     * 省份名称
     */
    private String province;

    /**
     * 省份编码
     */
    private String provinceCode;

    /**
     * 市名称
     */
    private String city;

    /**
     * 市编码
     */
    private String cityCode;

    /**
     * 区县名称
     */
    private String district;

    /**
     * 区县编码
     */
    private String districtCode;

    /**
     * 机构简称
     */
    private String shortName;

    /**
     * 机构类型
     */
    private String orgType;

    /**
     * 机构类型名称
     */
    private String orgTypeName;

    /**
     * 机构类型编码
     */
    private String orgTypeCode;

    /**
     * 上级机构id
     */
    private String higherOrg;

    /**
     * 上级机构名称
     */
    private String higherName;

    /**
     * 机构状态
     */
    private Integer status = 1;

    /**
     * 排序
     */
    private Integer sort = 1;

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

    /**
     * 机构层级
     */
    private Integer level;

    /**
     * 层级码
     */
    private String levelCode;

    /**
     * 是否逻辑删除
     */
    private Integer isDelete;

    /**
     * 对应首级机构id
     */
    private String firstLevelId;

    /**
     * 扩展字段
     */
    private String extInfo;

    /**
     * 三方扩展字段
     */
    private String thirdExtInfo;

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

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getProvinceCode() {
        return provinceCode;
    }

    public void setProvinceCode(String provinceCode) {
        this.provinceCode = provinceCode;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getCityCode() {
        return cityCode;
    }

    public void setCityCode(String cityCode) {
        this.cityCode = cityCode;
    }

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public String getDistrictCode() {
        return districtCode;
    }

    public void setDistrictCode(String districtCode) {
        this.districtCode = districtCode;
    }

    public String getShortName() {
        return shortName;
    }

    public void setShortName(String shortName) {
        this.shortName = shortName;
    }

    public String getOrgType() {
        return orgType;
    }

    public void setOrgType(String orgType) {
        this.orgType = orgType;
    }

    public String getOrgTypeName() {
        return orgTypeName;
    }

    public void setOrgTypeName(String orgTypeName) {
        this.orgTypeName = orgTypeName;
    }

    public String getOrgTypeCode() {
        return orgTypeCode;
    }

    public void setOrgTypeCode(String orgTypeCode) {
        this.orgTypeCode = orgTypeCode;
    }

    public String getHigherOrg() {
        return higherOrg;
    }

    public void setHigherOrg(String higherOrg) {
        this.higherOrg = higherOrg;
    }

    public String getHigherName() {
        return higherName;
    }

    public void setHigherName(String higherName) {
        this.higherName = higherName;
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

    public Integer getLevel() {
        return level;
    }

    public void setLevel(Integer level) {
        this.level = level;
    }

    public String getLevelCode() {
        return levelCode;
    }

    public void setLevelCode(String levelCode) {
        this.levelCode = levelCode;
    }

    public Integer getIsDelete() {
        return isDelete;
    }

    public void setIsDelete(Integer isDelete) {
        this.isDelete = isDelete;
    }

    public String getFirstLevelId() {
        return firstLevelId;
    }

    public void setFirstLevelId(String firstLevelId) {
        this.firstLevelId = firstLevelId;
    }

    public String getExtInfo() {
        return extInfo;
    }

    public void setExtInfo(String extInfo) {
        this.extInfo = extInfo;
    }

    public String getThirdExtInfo() {
        return thirdExtInfo;
    }

    public void setThirdExtInfo(String thirdExtInfo) {
        this.thirdExtInfo = thirdExtInfo;
    }
}
