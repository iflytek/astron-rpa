package com.iflytek.rpa.astronAgent.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * 通过手机号获取用户ID请求DTO
 */
@Data
public class GetUserIdDto {
    
    /**
     * 手机号
     */
    @NotBlank(message = "手机号不能为空")
    private String phone;
}
