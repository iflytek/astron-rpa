package com.iflytek.rpa.market.service;

import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 团队市场-团队表(AppMarket)表服务接口
 *
 * @author makejava
 * @since 2024-01-19 14:41:34
 */
public interface AppMarketService {

    AppResponse getAppType();

    AppResponse getListForPublish() throws NoLoginException;

    AppResponse getMarketList() throws NoLoginException;

    AppResponse addMarket(AppMarket appMarket) throws NoLoginException;

    AppResponse getMarketInfo(String marketId) throws NoLoginException;

    AppResponse editTeamMarket(AppMarket appMarket) throws NoLoginException;

    AppResponse leaveTeamMarket(AppMarket appMarket) throws NoLoginException;

    AppResponse dissolveTeamMarket(AppMarket appMarket);
}
