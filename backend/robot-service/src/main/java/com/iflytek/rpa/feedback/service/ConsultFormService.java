package com.iflytek.rpa.feedback.service;

import com.iflytek.rpa.feedback.entity.dto.ConsultFormSubmitDto;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 咨询表单服务接口
 *
 * @author system
 * @since 2024-12-15
 */
public interface ConsultFormService {

    /**
     * 提交咨询表单
     *
     * @param dto 咨询表单提交DTO
     * @return 提交结果
     */
    AppResponse<?> submitConsultForm(ConsultFormSubmitDto dto);
}
