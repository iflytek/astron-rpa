package com.iflytek.rpa.feedback.entity.dto;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;
import lombok.Data;

/**
 * 咨询表单提交DTO
 *
 * @author system
 * @since 2024-12-15
 */
@Data
public class ConsultFormSubmitDto {

    /**
     * 表单类型 1=专业版 2=企业版
     */
    //    @NotNull(message = "表单类型不能为空")
    private Integer formType;

    /**
     * 公司名称
     */
    @NotBlank(message = "公司名称不能为空")
    @Size(max = 128, message = "公司名称长度不能超过128字符")
    private String companyName;

    /**
     * 联系人姓名
     */
    @NotBlank(message = "联系人姓名不能为空")
    @Size(max = 64, message = "联系人姓名长度不能超过64字符")
    private String contactName;

    /**
     * 手机号
     */
    @NotBlank(message = "手机号不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    @Size(max = 20, message = "手机号长度不能超过20字符")
    private String mobile;

    /**
     * 邮箱（非必填）
     */
    @Email(message = "邮箱格式不正确")
    @Size(max = 128, message = "邮箱长度不能超过128字符")
    private String email;

    /**
     * 团队人数区间（字典值）
     */
    @Size(max = 32, message = "团队人数区间长度不能超过32字符")
    private String teamSize;
}
