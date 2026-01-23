package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * 角色基础信息 DTO
 * @author xqcao2
 *
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class RoleBaseDto {

    /**
     * 角色ID
     */
    private String id;

    /**
     * 角色编码
     */
    private String code;

    /**
     * 角色名称
     */
    private String name;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
