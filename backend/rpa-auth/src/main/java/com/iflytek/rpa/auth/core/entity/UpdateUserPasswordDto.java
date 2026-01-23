package com.iflytek.rpa.auth.core.entity;

import com.iflytek.rpa.auth.sp.uap.annotation.Password;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 管理端更新用户密码请求
 */
@Data
public class UpdateUserPasswordDto {

    /**
     * 用户名（登录名）
     */
    @NotBlank(message = "用户名不能为空")
    private String loginName;

    /**
     * 旧密码
     */
    @NotBlank(message = "旧密码不能为空")
    private String oldPassword;

    /**
     * 新密码
     */
    @NotBlank(message = "新密码不能为空")
    @Password
    private String newPassword;
}
