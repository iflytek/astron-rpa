package com.iflytek.rpa.notify.entity.dto;

import com.iflytek.rpa.market.entity.AppMarketUser;
import java.util.List;
import lombok.Data;

@Data
public class CreateNotifyDto {

    List<AppMarketUser> marketUserList;
    String tenantId;
    String messageType;
    String marketId;
    String appId;
}
