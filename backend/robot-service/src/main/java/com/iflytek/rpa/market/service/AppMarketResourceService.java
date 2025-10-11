package com.iflytek.rpa.market.service;

import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.AllAppListDto;
import com.iflytek.rpa.market.entity.dto.AppUpdateCheckDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.market.entity.dto.ShareRobotDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 团队市场-资源映射表(AppMarketResource)表服务接口
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
public interface AppMarketResourceService {

    /**
     * 机器人分享到团队市场
     */
    AppResponse<?> shareRobot(ShareRobotDto marketResourceDto) throws Exception;

    /**
     * 获取机器人
     */
    AppResponse<?> obtainRobot(MarketResourceDto marketResourceDto) throws Exception;

    /**
     * 已部署账号列表查询
     */
    AppResponse<?> getDeployedUserList(MarketDto marketDto) throws Exception;

    /**
     * 部署
     */
    AppResponse<?> deployRobot(MarketDto marketDto) throws Exception;

    /**
     * 更新-管理员推送更新
     */
    AppResponse<?> updateRobotByPush(MarketDto marketDto) throws Exception;

    /**
     * 推送版本-历史版本列表查询
     */
    AppResponse<?> getVersionListForApp(MarketDto marketDto) throws Exception;

    /**
     * 删除app
     */
    AppResponse<?> deleteApp(String appId, String marketId) throws Exception;

    /**
     * 应用列表接口
     */
    AppResponse<?> getALlAppList(AllAppListDto allAppListDto) throws NoLoginException;

    /**
     * 应用列表更新状态轮训
     */
    AppResponse<?> appUpdateCheck(AppUpdateCheckDto queryDto) throws Exception;

    /**
     * 应用详情
     */
    AppResponse<?> appDetail(String appId, String marketId) throws Exception;

    /**
     * 执行分享逻辑（供审核通过后自动调用）
     */
    AppResponse<?> executeShareRobotLogic(ShareRobotDto marketResourceDto, String userId, String tenantId);
}
