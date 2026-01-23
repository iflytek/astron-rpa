package com.iflytek.rpa.feedback.controller;

import com.iflytek.rpa.feedback.entity.dto.ConsultFormSubmitDto;
import com.iflytek.rpa.feedback.entity.dto.FeedbackSubmitDto;
import com.iflytek.rpa.feedback.entity.dto.RenewalFormSubmitDto;
import com.iflytek.rpa.feedback.service.ConsultFormService;
import com.iflytek.rpa.feedback.service.FeedbackService;
import com.iflytek.rpa.feedback.service.RenewalFormService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 反馈举报控制器
 *
 * @author system
 * @since 2024-12-15
 */
@RestController
@RequestMapping("/feedback")
public class FeedbackController {

    @Autowired
    private FeedbackService feedbackService;

    @Autowired
    private ConsultFormService consultFormService;

    @Autowired
    private RenewalFormService renewalFormService;

    /**
     * 提交反馈
     * 注意：前端需要先调用Python服务（/api/resource/file/upload）上传图片获取fileId，
     * 然后再调用此接口传递fileId列表
     *
     * @param dto 反馈提交DTO
     * @return 提交结果
     * @throws NoLoginException 未登录异常
     */
    @PostMapping("/submit")
    public AppResponse<?> submitFeedback(@RequestBody @Valid FeedbackSubmitDto dto) throws NoLoginException {
        return feedbackService.submitFeedback(dto);
    }

    /**
     * 提交咨询表单（专业版/企业版）
     *
     * @param dto 咨询表单提交DTO
     * @return 提交结果
     */
    @PostMapping("/consult/submit")
    public AppResponse<?> submitConsultForm(@RequestBody @Valid ConsultFormSubmitDto dto) {
        return consultFormService.submitConsultForm(dto);
    }

    /**
     * 提交续费表单（专业版/企业版）
     *
     * @param dto 续费表单提交DTO
     * @return 提交结果
     */
    @PostMapping("/renewal/submit")
    public AppResponse<?> submitRenewalForm(@RequestBody @Valid RenewalFormSubmitDto dto) {
        return renewalFormService.submitRenewalForm(dto);
    }
}
