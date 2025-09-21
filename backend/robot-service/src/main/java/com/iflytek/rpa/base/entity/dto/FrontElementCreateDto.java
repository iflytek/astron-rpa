package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

@Data
public class FrontElementCreateDto {

    /**
     * cv，common
     */
    private String type;

    private String robotId;

    private String groupName;

    private FrontElementDto element;
}
