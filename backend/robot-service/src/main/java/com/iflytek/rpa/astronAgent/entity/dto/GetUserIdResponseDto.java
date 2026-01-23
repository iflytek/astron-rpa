package com.iflytek.rpa.astronAgent.entity.dto;

import lombok.Data;

/**
 * 通过手机号获取用户ID响应DTO
 */
@Data
public class GetUserIdResponseDto {

    /**
     * 用户ID
     */
    private String userId;
}
