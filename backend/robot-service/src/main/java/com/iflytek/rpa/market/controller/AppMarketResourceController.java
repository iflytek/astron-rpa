package com.iflytek.rpa.market.controller;

import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.AllAppListDto;
import com.iflytek.rpa.market.entity.dto.AppUpdateCheckDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.market.entity.dto.ShareRobotDto;
import com.iflytek.rpa.market.service.AppMarketResourceService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.List;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.apache.commons.lang3.StringUtils;
import org.springframework.util.CollectionUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 团队市场-资源映射表(AppMarketResource)表控制层
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
@RestController
@RequestMapping("/market-resource")
public class AppMarketResourceController {
    /**
     * 服务对象
     */
    @Resource
    private AppMarketResourceService appMarketResourceService;

    /**
     * 机器人分享到团队市场
     * @paramMarketResourceDto
     * @return
     * @throws Exception
     */
    @PostMapping("/share")
    public AppResponse<?> shareRobot(@Valid @RequestBody ShareRobotDto marketResourceDto) throws Exception {
        return appMarketResourceService.shareRobot(marketResourceDto);
    }

    /**
     * 获取
     * @paramMarketResourceDto
     * @return
     * @throws Exception
     */
    @PostMapping("/obtain")
    public AppResponse<?> obtainRobot(@RequestBody MarketResourceDto marketResourceDto) throws Exception {
        String marketId = marketResourceDto.getMarketId();
        String robotName = marketResourceDto.getAppName();
        if (StringUtils.isBlank(robotName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人名称不能为空");
        }
        //        Integer editFlag = marketResourceDto.getEditFlag();
        List<String> obtainDirectory = marketResourceDto.getObtainDirection();
        if (CollectionUtils.isEmpty(obtainDirectory)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "缺少获取去向");
        }
        if (null == marketId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "缺少市场id");
        }
        if (null == marketResourceDto.getAppId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "缺少应用Id");
        }
        return appMarketResourceService.obtainRobot(marketResourceDto);
    }

    /**
     * 已部署账号列表查询
     * @param marketDto
     * @return
     * @throws Exception
     */
    @PostMapping("/deployed-user")
    public AppResponse<?> getDeployedUserList(@RequestBody MarketDto marketDto) throws Exception {
        return appMarketResourceService.getDeployedUserList(marketDto);
    }

    /**
     * 部署(客户端团队市场)
     * MarketDto
     * @return
     * @throws Exception
     */
    @PostMapping("/deploy")
    public AppResponse<?> deployRobot(@RequestBody MarketDto marketDto) throws Exception {
        return appMarketResourceService.deployRobot(marketDto);
    }

    /**
     * 更新-管理员推送更新(客户端团队市场)
     * @paramMarketResourceDto
     * @return
     * @throws Exception
     */
    @PostMapping("/update/push")
    public AppResponse<?> updateRobotByPush(@RequestBody MarketDto marketDto) throws Exception {
        return appMarketResourceService.updateRobotByPush(marketDto);
    }

    /**
     * 推送版本-历史版本列表查询
     * @paramMarketResourceDto
     * @return
     * @throws Exception
     */
    @PostMapping("/update/version-list")
    public AppResponse<?> getVersionListForApp(@RequestBody MarketDto marketDto) throws Exception {
        return appMarketResourceService.getVersionListForApp(marketDto);
    }

    /**
     * 删除app
     * @param appId
     * @param marketId
     * @return
     * @throws Exception
     */
    @GetMapping("/delete-app")
    public AppResponse<?> deleteApp(@RequestParam String appId, @RequestParam String marketId) throws Exception {
        return appMarketResourceService.deleteApp(appId, marketId);
    }

    /**
     * 应用列表接口
     * @param allAppListDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/get-all-app-list")
    public AppResponse<?> getALlAppList(@RequestBody AllAppListDto allAppListDto) throws NoLoginException {
        return appMarketResourceService.getALlAppList(allAppListDto);
    }

    /**
     * 应用列表更新状态轮训
     * @param queryDto
     * @return
     * @throws Exception
     */
    @PostMapping("/app-update-check")
    public AppResponse<?> appUpdateCheck(@RequestBody AppUpdateCheckDto queryDto) throws Exception {
        return appMarketResourceService.appUpdateCheck(queryDto);
    }

    @GetMapping("/app-detail")
    public AppResponse<?> appDetail(@RequestParam String appId, @RequestParam String marketId) throws Exception {
        return appMarketResourceService.appDetail(appId, marketId);
    }
}
