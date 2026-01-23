package com.iflytek.rpa.market.entity.dto;

import com.iflytek.rpa.market.entity.AppMarketResource;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class MarketResourceDto extends AppMarketResource {

//    @NotNull(message = "编辑标识不能为空")
    private Integer editFlag;

    @NotBlank(message = "行业分类不能为空")
    private String category;

    @NotBlank(message = "机器人id不能为空")
    private String robotId;

//    @NotNull(message = "版本号不能为空")
    private Integer version;

    private List<String> obtainDirection;

    private List<String> marketIdList;

    private List<AppMarketResource> appInsertInfoList;

    private List<AppMarketResource> appUpdateInfoList;

}
