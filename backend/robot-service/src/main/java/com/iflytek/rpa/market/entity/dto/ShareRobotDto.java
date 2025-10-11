package com.iflytek.rpa.market.entity.dto;

import com.iflytek.rpa.market.entity.AppMarketResource;
import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-09 10:03
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class ShareRobotDto {

    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    // @NotNull(message = "版本号不能为空")
    private Integer version;

    private Integer editFlag;

    @NotBlank(message = "行业分类不能为空")
    private String category;

    private List<String> marketIdList;

    private List<AppMarketResource> appInsertInfoList;

    private List<AppMarketResource> appUpdateInfoList;

    /**
     * 应用id，模板id，组件id
     */
    private String appId;
    /**
     * 发布人
     */
    private String creatorId;
    /**
     * 更新者id
     */
    private String updaterId;

    private String tenantId;
    /**
     * 资源名称
     */
    private String appName;
}
