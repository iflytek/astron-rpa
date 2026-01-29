package com.iflytek.rpa.auth.core.entity;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AddUserDto {
    /**
     * 手机号(必填)
     */
    @NotBlank
    private String phone;
    /**
     * 姓名(必填)
     */
    @NotBlank
    private String name;
    /**
     * 部门Id(必填)
     */
    @NotBlank
    private String orgId;
    /**
     * 角色Id 默认为 【未指定】
     */
    private String roleId = "1";

    private String loginName;

    private String tenantId;

    private String password;

    private String confirmPassword;
}
