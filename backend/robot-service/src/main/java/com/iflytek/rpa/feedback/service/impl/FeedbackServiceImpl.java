package com.iflytek.rpa.feedback.service.impl;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.feedback.dao.FeedbackReportDao;
import com.iflytek.rpa.feedback.entity.FeedbackReport;
import com.iflytek.rpa.feedback.entity.dto.FeedbackSubmitDto;
import com.iflytek.rpa.feedback.entity.dto.FeedbackSubmitResponse;
import com.iflytek.rpa.feedback.service.FeedbackService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.text.SimpleDateFormat;
import java.util.Date;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 反馈服务实现类
 *
 * @author system
 * @since 2024-12-15
 */
@Slf4j
@Service
public class FeedbackServiceImpl extends ServiceImpl<FeedbackReportDao, FeedbackReport> implements FeedbackService {

    @Autowired
    private IdWorker idWorker;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> submitFeedback(FeedbackSubmitDto dto) throws NoLoginException {
        try {
            // 1. 参数校验
            validateDto(dto);

            // 2. 处理图片ID列表
            String imageIdsStr = "";
            if (dto.getImageIds() != null && !dto.getImageIds().isEmpty()) {
                imageIdsStr = String.join(",", dto.getImageIds());
            }

            // 3. 生成唯一编号
            String reportNo = generateReportNo();

            // 4. 保存反馈记录
            FeedbackReport feedbackReport = new FeedbackReport();
            feedbackReport.setId(idWorker.nextId());
            feedbackReport.setReportNo(reportNo);
            feedbackReport.setUsername(dto.getUsername());
            feedbackReport.setCategories(dto.getCategories());
            feedbackReport.setDescription(dto.getDescription());
            feedbackReport.setImageIds(imageIdsStr);
            feedbackReport.setCreateTime(new Date());
            feedbackReport.setDeleted(0);
            feedbackReport.setProcessed(0); // 默认未处理

            this.save(feedbackReport);

            // 5. 返回结果
            FeedbackSubmitResponse response = new FeedbackSubmitResponse();
            response.setReportNo(reportNo);

            return AppResponse.success(response);
        } catch (ServiceException e) {
            log.error("提交反馈失败: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_PARAM, e.getMessage());
        } catch (Exception e) {
            log.error("提交反馈异常: {}", e.getMessage(), e);
            return AppResponse.error(ErrorCodeEnum.E_COMMON, "提交反馈失败，请稍后重试");
        }
    }

    /**
     * 参数校验
     * 注意：基础校验已通过@Valid注解在Controller层完成
     * 这里只做业务相关的校验（如JSON格式验证）
     */
    private void validateDto(FeedbackSubmitDto dto) {
        // 验证categories是否为有效的JSON格式
        try {
            JSON.parseObject(dto.getCategories());
        } catch (Exception e) {
            throw new ServiceException("问题分类格式不正确，应为JSON格式");
        }
    }

    /**
     * 生成唯一编号
     * 格式：FB + 时间戳（yyyyMMddHHmmss） + 雪花算法ID的后6位
     */
    private String generateReportNo() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMddHHmmss");
        String timestamp = sdf.format(new Date());
        long snowflakeId = idWorker.nextId();
        String lastSixDigits = String.valueOf(snowflakeId)
                .substring(Math.max(0, String.valueOf(snowflakeId).length() - 6));
        return "FB" + timestamp + lastSixDigits;
    }
}
