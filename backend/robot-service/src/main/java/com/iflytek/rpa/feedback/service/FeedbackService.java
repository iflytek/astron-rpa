package com.iflytek.rpa.feedback.service;

import com.iflytek.rpa.feedback.entity.dto.FeedbackSubmitDto;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 反馈服务接口
 *
 * @author system
 * @since 2024-12-15
 */
public interface FeedbackService {

    /**
     * 提交反馈
     *
     * @param dto 反馈提交DTO
     * @return 提交结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<?> submitFeedback(FeedbackSubmitDto dto) throws NoLoginException;
}
