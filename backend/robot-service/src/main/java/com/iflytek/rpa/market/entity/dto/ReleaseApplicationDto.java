package com.iflytek.rpa.market.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * 客户端上架申请DTO
 */
@Data
public class ReleaseApplicationDto {

    /**
     * robotId，不能为空
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * robotVersion，不能为空
     */
    @NotNull(message = "机器人版本不能为空")
    private Integer robotVersion;

    /**
     * 目标市场ID列表，不能为空
     */
    @NotNull(message = "市场id不能为空")
    private List<String> marketIdList;

    /**
     * 编辑权限标识
     */
    private Integer editFlag;

    /**
     * 分类
     */
    private String category;
}
