package com.iflytek.rpa.market.entity;

import lombok.Data;

import java.util.List;

/**
 * @author mjren
 * @date 2024-01-24 17:07
 * @copyright Copyright (c) 2024 mjren
 */
@Data
public class AppMarketDo {

    private Boolean noMarket;

    private List<AppMarket> joinedMarketList ;

    private List<AppMarket> createdMarketList;

}
