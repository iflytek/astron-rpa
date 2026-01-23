package com.iflytek.rpa.market.controller;

import com.iflytek.rpa.market.entity.dto.InviteKeyDto;
import com.iflytek.rpa.market.entity.dto.InviteLinkDto;
import com.iflytek.rpa.market.entity.vo.AcceptResultVo;
import com.iflytek.rpa.market.entity.vo.InviteInfoVo;
import com.iflytek.rpa.market.entity.vo.InviteLinkVo;
import com.iflytek.rpa.market.service.AppMarketInviteService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 团队市场-链接邀请
 */
@RestController
@RequestMapping("market-invite")
public class AppMarketInviteController {

    @Resource
    private AppMarketInviteService appMarketInviteService;

    /**
     * 生成/获取邀请链接
     * 有效期内不会生成新链接
     * @param inviteLinkDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/generate-invite-link")
    public AppResponse<InviteLinkVo> generateInviteLink(@RequestBody InviteLinkDto inviteLinkDto)
            throws NoLoginException {
        return appMarketInviteService.generateInviteLink(inviteLinkDto);
    }

    /**
     * 重置邀请链接
     *
     * @param inviteLinkDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/reset-invite-link")
    public AppResponse<InviteLinkVo> resetInviteLink(@RequestBody InviteLinkDto inviteLinkDto) throws NoLoginException {
        return appMarketInviteService.resetInviteLink(inviteLinkDto);
    }

    /**
     * 根据邀请key获取邀请信息
     *
     * @param inviteKeyDto
     * @return
     */
    @PostMapping("/get-invite-info-by-invite-key")
    public AppResponse<InviteInfoVo> getInviteInfoByInviteKey(@RequestBody InviteKeyDto inviteKeyDto) {
        return appMarketInviteService.getInviteInfoByInviteKey(inviteKeyDto.getInviteKey());
    }

    /**
     * 接受邀请
     *
     * @param inviteKeyDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/accept-invite")
    public AppResponse<AcceptResultVo> acceptInvite(@RequestBody InviteKeyDto inviteKeyDto) throws NoLoginException {
        return appMarketInviteService.acceptInvite(inviteKeyDto.getInviteKey());
    }
}
