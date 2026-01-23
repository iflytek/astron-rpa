package com.iflytek.rpa.feedback.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.feedback.dao.ConsultFormDao;
import com.iflytek.rpa.feedback.entity.ConsultForm;
import com.iflytek.rpa.feedback.entity.dto.ConsultFormSubmitDto;
import com.iflytek.rpa.feedback.entity.enums.FormStatus;
import com.iflytek.rpa.feedback.entity.enums.FormType;
import com.iflytek.rpa.feedback.service.ConsultFormService;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Date;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 咨询表单服务实现类
 *
 * @author system
 * @since 2024-12-15
 */
@Slf4j
@Service
public class ConsultFormServiceImpl extends ServiceImpl<ConsultFormDao, ConsultForm> implements ConsultFormService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> submitConsultForm(ConsultFormSubmitDto dto) {
        try {
            // 1. 参数校验
            //            validateDto(dto);

            // 2. 保存咨询表单记录
            ConsultForm consultForm = new ConsultForm();
            consultForm.setFormType(dto.getFormType());
            consultForm.setCompanyName(dto.getCompanyName());
            consultForm.setContactName(dto.getContactName());
            consultForm.setMobile(dto.getMobile());
            consultForm.setEmail(dto.getEmail());
            consultForm.setTeamSize(dto.getTeamSize());
            consultForm.setStatus(FormStatus.PENDING.getCode()); // 默认待处理
            consultForm.setCreatedAt(new Date());
            consultForm.setUpdatedAt(new Date());

            this.save(consultForm);

            // 3. 返回结果
            return AppResponse.success("咨询表单提交成功");
        } catch (ServiceException e) {
            log.error("提交咨询表单失败: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_PARAM, e.getMessage());
        } catch (Exception e) {
            log.error("提交咨询表单异常: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_COMMON, "提交咨询表单失败，请稍后重试");
        }
    }

    /**
     * 参数校验
     * 注意：基础校验已通过@Valid注解在Controller层完成
     * 这里只做业务相关的校验
     */
    private void validateDto(ConsultFormSubmitDto dto) {
        // 验证表单类型是否有效
        FormType formType = FormType.getByCode(dto.getFormType());
        if (formType == null) {
            throw new ServiceException("表单类型无效，仅支持专业版(1)和企业版(2)");
        }
    }
}
