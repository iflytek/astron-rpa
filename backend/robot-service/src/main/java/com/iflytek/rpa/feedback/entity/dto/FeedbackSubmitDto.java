package com.iflytek.rpa.feedback.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import lombok.Data;

/**
 * 反馈提交DTO
 *
 * @author system
 * @since 2024-12-15
 */
@Data
public class FeedbackSubmitDto {

    /**
     * 用户登录名
     */
    @NotBlank(message = "用户登录名不能为空")
    private String username;

    /**
     * 问题分类列表（JSON格式字符串）
     * 格式：{"内容安全类":["生成违法/违规信息","核心内容"],"功能缺陷类":["生成流程代码错误，无法执行"]}
     */
    @NotBlank(message = "问题分类不能为空")
    private String categories;

    /**
     * 问题描述
     */
    @NotBlank(message = "问题描述不能为空")
    @Size(max = 5000, message = "问题描述长度不能超过5000字符")
    private String description;

    /**
     * 图片文件ID列表（最多3个）
     * 前端需要先调用Python服务上传图片，获取fileId后再传递
     */
    @Size(max = 3, message = "最多只能上传3张图片")
    private List<@NotBlank(message = "图片文件ID不能为空") String> imageIds;
}
