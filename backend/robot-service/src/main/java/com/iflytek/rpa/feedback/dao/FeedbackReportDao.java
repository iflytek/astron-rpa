package com.iflytek.rpa.feedback.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.feedback.entity.FeedbackReport;
import org.apache.ibatis.annotations.Mapper;

/**
 * 反馈举报DAO
 *
 * @author system
 * @since 2024-12-15
 */
@Mapper
public interface FeedbackReportDao extends BaseMapper<FeedbackReport> {}
