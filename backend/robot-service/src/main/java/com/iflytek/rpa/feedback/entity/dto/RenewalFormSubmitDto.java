package com.iflytek.rpa.feedback.entity.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;
import lombok.Data;

/**
 * 续费表单提交DTO
 *
 * @author system
 * @since 2024-12-15
 */
@Data
public class RenewalFormSubmitDto {

    /**
     * 表单类型 1=专业版 2=企业版
     */
    @NotNull(message = "表单类型不能为空")
    private Integer formType;

    /**
     * 企业名称
     */
    @NotBlank(message = "企业名称不能为空")
    @Size(max = 128, message = "企业名称长度不能超过128字符")
    private String companyName;

    /**
     * 负责人手机号
     */
    @NotBlank(message = "手机号不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    @Size(max = 20, message = "手机号长度不能超过20字符")
    private String mobile;

    /**
     * 续费时长（如：6个月、1年、2年）
     */
    @NotBlank(message = "续费时长不能为空")
    @Size(max = 32, message = "续费时长长度不能超过32字符")
    private String renewalDuration;
}
