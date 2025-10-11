package com.iflytek.rpa.market.entity.vo;

import com.iflytek.rpa.market.entity.AppMarketUser;
import lombok.Data;

@Data
public class AppMarketUserVo extends AppMarketUser {

    private String marketId;

    private String appId;
}
