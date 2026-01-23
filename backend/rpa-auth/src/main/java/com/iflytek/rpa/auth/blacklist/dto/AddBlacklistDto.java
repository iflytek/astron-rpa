package com.iflytek.rpa.auth.blacklist.dto;

import java.io.Serializable;
import javax.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 添加黑名单 DTO
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AddBlacklistDto implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    @NotBlank(message = "用户ID不能为空")
    private String userId;

    /**
     * 用户名
     */
    @NotBlank(message = "用户名不能为空")
    private String username;

    /**
     * 封禁原因
     */
    @NotBlank(message = "封禁原因不能为空")
    private String reason;
}
