package com.iflytek.rpa.feedback.service;

import com.iflytek.rpa.feedback.entity.dto.RenewalFormSubmitDto;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 续费表单服务接口
 *
 * @author system
 * @since 2024-12-15
 */
public interface RenewalFormService {

    /**
     * 提交续费表单
     *
     * @param dto 续费表单提交DTO
     * @return 提交结果
     */
    AppResponse<?> submitRenewalForm(RenewalFormSubmitDto dto);
}
