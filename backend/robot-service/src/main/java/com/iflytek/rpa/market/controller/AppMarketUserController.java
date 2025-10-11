package com.iflytek.rpa.market.controller;

import static com.iflytek.rpa.market.constants.RightConstant.*;

import com.iflytek.rpa.market.annotation.RightCheck;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.service.AppMarketUserService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 团队市场-人员
 *
 * @author makejava
 * @since 2024-01-19 14:41:35
 */
@RestController
@RequestMapping("market-user")
public class AppMarketUserController {
    /**
     * 服务对象
     */
    @Resource
    private AppMarketUserService appMarketUserService;

    /**
     * 未部署账号列表查询
     * @param marketDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/undeploy-user")
    //    @RightCheck(dictCode = market_user_get_user)
    public AppResponse<?> getUserUnDeployed(@RequestBody MarketDto marketDto) throws NoLoginException {

        return appMarketUserService.getUserUnDeployed(marketDto);
    }

    /**
     * 成员管理-成员列表
     *
     * @param
     * @return
     */
    @PostMapping("/list")
    public AppResponse<List<MarketDto>> getUserList(@RequestBody MarketDto marketUserDto) {
        return appMarketUserService.getUserList(marketUserDto);
    }

    /**
     * 成员管理-移出
     *
     * @param
     * @return
     */
    @PostMapping("/delete")
    @RightCheck(dictCode = market_user_delete)
    public AppResponse<Boolean> deleteUser(@RequestBody MarketDto marketUserDto) throws NoLoginException {

        return appMarketUserService.deleteUser(marketUserDto);
    }

    /**
     * 成员管理-设置角色
     *
     * @param
     * @return
     */
    @PostMapping("/role")
    @RightCheck(dictCode = market_user_role)
    public AppResponse<Boolean> roleSet(@RequestBody MarketDto marketUserDto) throws NoLoginException {

        return appMarketUserService.roleSet(marketUserDto);
    }

    /**
     * 成员管理-邀请-模糊查询员工
     *
     * @param
     * @return
     */
    @PostMapping("/get/user")
    @RightCheck(dictCode = market_user_get_user)
    public AppResponse<List<MarketDto>> getUserByPhone(@RequestBody MarketDto marketDto) throws NoLoginException {

        return appMarketUserService.getUserByPhone(marketDto);
    }

    /**
     * 团队管理-拥有者离开团队-模糊查询员工
     *
     * @param
     * @return
     */
    @PostMapping("/leave/user")
    @RightCheck(dictCode = market_user_get_user)
    public AppResponse<List<MarketDto>> getUserByPhoneForOwner(@RequestBody MarketDto marketDto)
            throws NoLoginException {
        return appMarketUserService.getUserByPhoneForOwner(marketDto);
    }

    /**
     * 成员管理-邀请
     *
     * @param
     * @return
     */
    @PostMapping("/invite")
    @RightCheck(dictCode = market_user_invite)
    public AppResponse<Boolean> inviteUser(@RequestBody MarketDto marketDto) throws NoLoginException {

        return appMarketUserService.inviteUser(marketDto);
    }

    //
    //    /**
    //     * 成员管理-邀请-查询部门和员工
    //     *
    //     * @param
    //     * @return
    //     */
    //    @PostMapping("/dept/user")
    //    public AppResponse<?> getDeptAndUser(@RequestBody MarketDto marketDto) throws NoLoginException {
    //        if(null == marketDto.getMarketId()){
    //            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
    //        }
    //        String tenantId = TenantUtils.getTenantId();
    //
    //        AppResponse response = uacFeign.getDeptUserForInvite(tenantId, marketDto.getMarketId());
    //        if(! response.ok()){
    //            return AppResponse.error(ErrorCodeEnum.E_SERVICE);
    //        }
    //        return response;
    //    }

}
