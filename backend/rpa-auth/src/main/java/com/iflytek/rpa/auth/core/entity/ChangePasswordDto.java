package com.iflytek.rpa.auth.core.entity;

import com.iflytek.rpa.auth.sp.uap.annotation.Password;
import javax.validation.constraints.AssertTrue;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 修改密码请求 DTO
 */
@Data
public class ChangePasswordDto {

    /**
     * 账号（登录名）
     */
    //    @NotBlank(message = "账号不能为空")
    private String loginName;

    /**
     * 登录手机号
     */
    //    @NotBlank(message = "手机号不能为空")
    private String phone;

    /**
     * 原密码
     */
    @NotBlank(message = "原密码不能为空")
    private String oldPassword;

    /**
     * 新密码
     */
    @NotBlank(message = "新密码不能为空")
    @Password
    private String newPassword;

    /**
     * 确认密码
     */
    @NotBlank(message = "确认密码不能为空")
    private String confirmPassword;

    /**
     * 验证两次密码是否一致
     */
    @AssertTrue(message = "两次输入的密码不一致")
    public boolean isPasswordMatch() {
        if (newPassword == null || confirmPassword == null) {
            return true; // 由 @NotBlank 处理空值校验
        }
        return newPassword.equals(confirmPassword);
    }
}
