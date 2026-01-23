package com.iflytek.rpa.auth.core.entity;

import java.util.List;

/**
 * 创建用户 DTO  基本信息以及扩展信息
 * @author xqcao2
 *
 */
public class CreateUapUserDto {

    /**
     * 用户基础信息
     */
    private CreateUserDto user;

    /**
     * 用户扩展信息  没有扩展属性，此字段可以不理会
     */
    private List<UapExtendPropertyDto> extands;

    public CreateUserDto getUser() {
        return user;
    }

    public void setUser(CreateUserDto user) {
        this.user = user;
    }

    public List<UapExtendPropertyDto> getExtands() {
        return extands;
    }

    public void setExtands(List<UapExtendPropertyDto> extands) {
        this.extands = extands;
    }
}
