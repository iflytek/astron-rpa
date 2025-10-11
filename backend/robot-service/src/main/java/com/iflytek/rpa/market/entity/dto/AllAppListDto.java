package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

@Data
public class AllAppListDto {
    String marketId;
    Long pageNo;
    Long pageSize;
    String appName;
    String creatorId;
    String sortKey;
}
