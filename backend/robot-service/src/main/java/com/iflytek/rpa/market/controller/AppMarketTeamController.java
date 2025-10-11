package com.iflytek.rpa.market.controller;

import static com.iflytek.rpa.market.constants.RightConstant.*;

import com.iflytek.rpa.market.annotation.RightCheck;
import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.market.entity.AppMarketDict;
import com.iflytek.rpa.market.entity.AppMarketDo;
import com.iflytek.rpa.market.service.AppMarketService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

/**
 * 团队市场-团队
 *
 * @author makejava
 * @since 2024-01-19 14:41:28
 */
@RestController
@RequestMapping("market-team")
public class AppMarketTeamController {
    /**
     * 服务对象
     */
    @Resource
    private AppMarketService appMarketService;

    /**
     * 类型-行业列表
     * @return
     */
    @PostMapping("/type")
    public AppResponse<List<AppMarketDict>> getAppType() {

        return appMarketService.getAppType();
    }

    /**
     * 发布至市场-市场列表、用户是否有市场
     *
     * @param
     * @return
     */
    @PostMapping("/list")
    public AppResponse<AppMarketDo> getListForPublish() throws NoLoginException {

        return appMarketService.getListForPublish();
    }

    /**
     * 团队市场-市场名称列表-左侧树
     *
     * @param
     * @return
     */
    @PostMapping("/get-list")
    public AppResponse<List<AppMarket>> getList() throws NoLoginException {

        return appMarketService.getMarketList();
    }

    /**
     * 创建团队市场
     *
     * @param
     * @return
     */
    @PostMapping("/add")
    public AppResponse<Boolean> addMarket(@RequestBody AppMarket appMarket) throws NoLoginException {

        return appMarketService.addMarket(appMarket);
    }

    /**
     * 获取市场信息
     * @param marketId
     * @return
     */
    @PostMapping("/info")
    AppResponse<AppMarket> getMarketInfo(@RequestParam("marketId") String marketId) throws NoLoginException {
        return appMarketService.getMarketInfo(marketId);
    }

    /**
     * 编辑市场
     *
     * @param
     * @return
     */
    @PostMapping("/edit")
    @RightCheck(dictCode = market_team_edit, clazz = AppMarket.class)
    public AppResponse<Boolean> editTeamMarket(@RequestBody AppMarket appMarket) throws NoLoginException {

        return appMarketService.editTeamMarket(appMarket);
    }

    /**
     * 离开团队市场
     *
     * @param
     * @return
     */
    @PostMapping("/leave")
    @RightCheck(dictCode = market_team_leave, clazz = AppMarket.class)
    public AppResponse<Boolean> leaveTeamMarket(@RequestBody AppMarket appMarket) throws NoLoginException {

        return appMarketService.leaveTeamMarket(appMarket);
    }

    /**
     * 解散团队市场
     *
     * @param
     * @return
     */
    @PostMapping("/dissolve")
    @RightCheck(dictCode = market_team_dissolve, clazz = AppMarket.class)
    public AppResponse<Boolean> dissolveTeamMarket(@RequestBody AppMarket appMarket) throws NoLoginException {

        return appMarketService.dissolveTeamMarket(appMarket);
    }
}
