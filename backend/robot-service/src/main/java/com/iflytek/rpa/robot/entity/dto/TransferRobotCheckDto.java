package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

import java.util.List;

/**
 * @author mjren
 * @date 2025-07-01 15:17
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class TransferRobotCheckDto {
    private List<String> robotIdList;
}
