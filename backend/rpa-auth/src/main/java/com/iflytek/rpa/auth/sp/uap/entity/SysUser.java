package com.iflytek.rpa.auth.sp.uap.entity;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import lombok.Getter;
import lombok.Setter;

/**
 * 用户基础信息
 * @author keler
 */
@Setter
@Getter
public class SysUser implements Serializable {
    private Long id;
    /** 用户名 */
    private String name;

    private String username;
    private String password;

    private String phone;
    private String telephone;
    private String email;

    /** 账户是否可用 */
    private Boolean enabled;
    /** 账户是否未过期 */
    private Boolean accountNonExpired;
    /** 账户是否未锁定 */
    private Boolean accountNonLocked;
    /** 账户凭证是否未 */
    private Boolean credentialsNonExpired;

    private List<String> userOwnedPath = new ArrayList<>();

    public SysUser() {}

    @Override
    public String toString() {
        return "User{" + "id="
                + id + ", username='"
                + name + '\'' + ", password='"
                + password + '\'' + ", enabled="
                + enabled + ", accountNonExpired="
                + accountNonExpired + ", accountNonLocked="
                + accountNonLocked + ", credentialsNonExpired="
                + credentialsNonExpired + ", roles="
                + userOwnedPath + '}';
    }
}
