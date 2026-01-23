package com.iflytek.rpa.auth.sp.uap.entity;

import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/**
 * @Author: wyzhou3
 * @Date: 2022/10/12 14:49
 * @Description:
 */
@Data
public class UserDetail {
    private Long id;

    private String uuid;

    private String redisUUid;

    private String username;

    private String phone;

    private String email;

    private ZonedDateTime registerTime;

    private Integer oauthTypeId;

    private Integer authFlag;

    private String password;

    private ZonedDateTime createTime;

    private ZonedDateTime updateTime;

    private String nickName;

    private Integer gender;

    private String avatorUrl;

    private Integer lastLoginOauthTypeId;

    private ZonedDateTime lastLoginTime;

    private Boolean deleted;

    private Boolean hasPassword = false;

    private Boolean accountNonExpired;

    private Boolean accountNonLocked;

    private Boolean credentialsNonExpired;

    private List<String> userOwnedPath = new ArrayList<>();
}
