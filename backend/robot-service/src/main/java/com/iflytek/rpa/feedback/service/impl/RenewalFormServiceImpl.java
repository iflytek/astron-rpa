package com.iflytek.rpa.feedback.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.feedback.dao.RenewalFormDao;
import com.iflytek.rpa.feedback.entity.RenewalForm;
import com.iflytek.rpa.feedback.entity.dto.RenewalFormSubmitDto;
import com.iflytek.rpa.feedback.entity.enums.FormStatus;
import com.iflytek.rpa.feedback.entity.enums.FormType;
import com.iflytek.rpa.feedback.service.RenewalFormService;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Date;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 续费表单服务实现类
 *
 * @author system
 * @since 2024-12-15
 */
@Slf4j
@Service
public class RenewalFormServiceImpl extends ServiceImpl<RenewalFormDao, RenewalForm> implements RenewalFormService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> submitRenewalForm(RenewalFormSubmitDto dto) {
        try {
            // 1. 参数校验
            validateDto(dto);

            // 2. 保存续费表单记录
            RenewalForm renewalForm = new RenewalForm();
            renewalForm.setFormType(dto.getFormType());
            renewalForm.setCompanyName(dto.getCompanyName());
            renewalForm.setMobile(dto.getMobile());
            renewalForm.setRenewalDuration(dto.getRenewalDuration());
            renewalForm.setStatus(FormStatus.PENDING.getCode()); // 默认待处理
            renewalForm.setCreatedAt(new Date());
            renewalForm.setUpdatedAt(new Date());

            this.save(renewalForm);

            // 3. 返回结果
            return AppResponse.success("续费表单提交成功");
        } catch (ServiceException e) {
            log.error("提交续费表单失败: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_PARAM, e.getMessage());
        } catch (Exception e) {
            log.error("提交续费表单异常: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_COMMON, "提交续费表单失败，请稍后重试");
        }
    }

    /**
     * 参数校验
     * 注意：基础校验已通过@Valid注解在Controller层完成
     * 这里只做业务相关的校验
     */
    private void validateDto(RenewalFormSubmitDto dto) {
        // 验证表单类型是否有效
        FormType formType = FormType.getByCode(dto.getFormType());
        if (formType == null) {
            throw new ServiceException("表单类型无效，仅支持专业版(1)和企业版(2)");
        }
    }
}
