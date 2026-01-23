package com.iflytek.rpa.notify.entity.dto;

import com.iflytek.rpa.market.entity.AppMarketUser;
import lombok.Data;

import java.util.List;

@Data
public class CreateNotifyDto {

    List<AppMarketUser> marketUserList;
    String tenantId;
    String messageType;
    String marketId;
    String appId;
    Integer operateResult;
}
