package com.iflytek.rpa.auth.core.entity;

/**
 * 实体类添加扩展属性 DTO
 * @author xqcao2
 *
 */
public class UapExtendPropertyDto {

    /**
     * 扩展属性ID
     */
    private String id;

    /**
     * 扩展属性 对应的值
     */
    private String value;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }
}
