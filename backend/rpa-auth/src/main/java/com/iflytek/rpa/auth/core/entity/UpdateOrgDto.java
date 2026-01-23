package com.iflytek.rpa.auth.core.entity;

/**
 * 创建机构DTO
 * @author xqcao2
 *
 */
public class UpdateOrgDto {

    /**
     * 机构id 更新时必传
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
     * 上级机构id
     */
    private String higherOrg;

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

    public String getHigherOrg() {
        return higherOrg;
    }

    public void setHigherOrg(String higherOrg) {
        this.higherOrg = higherOrg;
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
}
