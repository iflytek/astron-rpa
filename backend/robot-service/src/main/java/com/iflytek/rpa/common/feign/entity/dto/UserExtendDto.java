package com.iflytek.rpa.common.feign.entity.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.iflytek.rpa.common.feign.entity.ExtendRelation;
import com.iflytek.rpa.common.feign.entity.User;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class UserExtendDto extends TenantModeExtendDto {
    private User user;
    private List<ExtendRelation> extands;
    private List<RoleBaseDto> roles;

    public UserExtendDto() {}

    public User getUser() {
        return this.user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public List<ExtendRelation> getExtands() {
        return this.extands;
    }

    public void setExtands(List<ExtendRelation> extands) {
        this.extands = extands;
    }

    public List<RoleBaseDto> getRoles() {
        return this.roles;
    }

    public void setRoles(List<RoleBaseDto> roles) {
        this.roles = roles;
    }
}
