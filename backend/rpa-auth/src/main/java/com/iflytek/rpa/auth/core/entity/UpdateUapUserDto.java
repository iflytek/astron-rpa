package com.iflytek.rpa.auth.core.entity;

import java.util.List;

/**
 * 更新用户
 * @author xqcao2
 *
 */
public class UpdateUapUserDto {

    /**
     * 用户基础信息
     */
    private UpdateUserDto user;

    /**
     * 用户扩展信息
     */
    private List<UapExtendPropertyDto> extands;

    public UpdateUserDto getUser() {
        return user;
    }

    public void setUser(UpdateUserDto user) {
        this.user = user;
    }

    public List<UapExtendPropertyDto> getExtands() {
        return extands;
    }

    public void setExtands(List<UapExtendPropertyDto> extands) {
        this.extands = extands;
    }
}
