package com.iflytek.rpa.market.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 客户端发版后提交上架申请DTO
 */
@Data
public class SubmitAfterPublishDto extends ReleaseApplicationDto {
    /**
     * 机器人名，不能为空
     */
    @NotBlank(message = "机器人名不能为空")
    private String name;

    private String creatorId;

    private String tenantId;
}
