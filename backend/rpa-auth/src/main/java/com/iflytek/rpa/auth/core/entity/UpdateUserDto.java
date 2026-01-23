package com.iflytek.rpa.auth.core.entity;

import java.util.Date;

/**
 * 更新用户DTO
 * @author xqcao2
 *
 */
public class UpdateUserDto {

    /**
     * 主键  更新时必传
     */
    private String id;

    /**
     * 用户姓名
     */
    private String name;

    /**
     * 登陆用户名
     */
    private String loginName;

    /**
     * 用户类型
     *  SUPER_ADMIN("超级管理员", 1),
     *  SYSTEM_ADMIN("平台管理员", 2),
     *  NORMAL_USER("普通用户", -1),
     *  RESOURCE_POOL_USER("资源池用户", 3),
     *  TENANT_SUPER_ADMIN("租户超级管理员", 0);
     */
    private Integer userType;

    /**
     * 用户来源{1系统添加,2域账号}
     */
    private Integer userSource = 1;

    /**
     * 电话
     */
    private String phone;

    /**
     * 地址
     */
    private String address;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 账户状态{0停用 1启用}
     */
    private Integer status = 1;

    /**
     * 机构id  会校验机构是否存在
     */
    private String orgId;

    /**
     * 备注
     */
    private String remark;

    /**
     * 生日
     */
    private Date birthday;

    /**
     * 身份证号
     */
    private String idNumber;

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

    public String getLoginName() {
        return loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }

    public Integer getUserType() {
        return userType;
    }

    public void setUserType(Integer userType) {
        this.userType = userType;
    }

    public Integer getUserSource() {
        return userSource;
    }

    public void setUserSource(Integer userSource) {
        this.userSource = userSource;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getOrgId() {
        return orgId;
    }

    public void setOrgId(String orgId) {
        this.orgId = orgId;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    public Date getBirthday() {
        return birthday;
    }

    public void setBirthday(Date birthday) {
        this.birthday = birthday;
    }

    public String getIdNumber() {
        return idNumber;
    }

    public void setIdNumber(String idNumber) {
        this.idNumber = idNumber;
    }
}
