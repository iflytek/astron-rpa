package com.iflytek.rpa.auth.core.entity;

import com.iflytek.rpa.auth.core.entity.enums.LoginTypeEnum;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginDto {

    /**
     * 手机号
     */
    private String phone;

    /**
     * 登录名
     */
    private String loginName;

    /**
     * 密码
     */
    private String password;

    /**
     * 验证码
     */
    private String captcha;

    /**
     * 登录类型
     */
    private LoginTypeEnum loginType;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 登录平台（client: 客户端, admin: 运营后台, invite: 邀请链接）
     */
    private String platform;

    /**
     * 验证码场景（login/register/set_password），用于校验防交叉使用
     */
    private String scene;
}
