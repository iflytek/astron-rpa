package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * 用户详细信息DTO
 * @author xqcao2
 *
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserExtendDto extends TenantModeExtendDto {

    /**
     * 用户基础信息
     */
    private User user;

    /**
     * 用户扩展信息
     */
    private List<UapExtendRelation> extands;

    /**
     * 角色信息
     */
    private List<RoleBaseDto> roles;

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public List<UapExtendRelation> getExtands() {
        return extands;
    }

    public void setExtands(List<UapExtendRelation> extands) {
        this.extands = extands;
    }

    public List<RoleBaseDto> getRoles() {
        return roles;
    }

    public void setRoles(List<RoleBaseDto> roles) {
        this.roles = roles;
    }
}
