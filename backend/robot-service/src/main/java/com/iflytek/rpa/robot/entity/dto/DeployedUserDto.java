package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-15 10:42
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class DeployedUserDto {

    private Long id;

    private String creatorId;

    private String time;

    private String name;

    private Integer version;

    private Boolean isCreator;
}
