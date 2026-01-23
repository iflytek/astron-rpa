package com.iflytek.rpa.common.feign.entity.dto;

public class GetUserDto {
    private String userId;
    private String loginName;

    public GetUserDto() {}

    public String getUserId() {
        return this.userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getLoginName() {
        return this.loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }
}
