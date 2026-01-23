package com.iflytek.rpa.auth.core.entity;

import com.iflytek.rpa.auth.sp.uap.annotation.Password;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 设置密码请求 DTO（用于注册后首次设置密码）
 */
@Data
public class SetPasswordDto {

    /**
     * 临时凭证（注册后返回的）
     */
    @NotBlank(message = "临时凭证不能为空")
    private String tempToken;

    /**
     * 新密码
     */
    @NotBlank(message = "密码不能为空")
    @Password
    private String password;

    /**
     * 确认密码
     */
    @NotBlank(message = "确认密码不能为空")
    private String confirmPassword;

    /**
     * 选择的租户ID（可选，如果用户只有一个租户可以自动选择）
     */
    private String tenantId;
}
