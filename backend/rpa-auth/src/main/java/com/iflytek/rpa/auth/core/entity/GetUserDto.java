package com.iflytek.rpa.auth.core.entity;

/**
 * 查看用户详细信息 DTO
 * @author xqcao2
 *
 */
public class GetUserDto {

    /***
     * 请传一个即可 两个同时传 是& 关系
     */

    /**
     * 用户ID (remark: 请传一个即可 两个同时传 请确保是对应的, 否则查询不到)
     */
    private String userId;

    /**
     * 登录名 (remark: 请传一个即可 两个同时传 请确保是对应的, 否则查询不到)
     */
    private String loginName;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getLoginName() {
        return loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }
}
