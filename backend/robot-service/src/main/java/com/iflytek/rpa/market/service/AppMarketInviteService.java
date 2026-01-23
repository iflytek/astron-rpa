package com.iflytek.rpa.market.service;

import com.iflytek.rpa.market.entity.dto.InviteLinkDto;
import com.iflytek.rpa.market.entity.vo.AcceptResultVo;
import com.iflytek.rpa.market.entity.vo.InviteInfoVo;
import com.iflytek.rpa.market.entity.vo.InviteLinkVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 团队市场-SaaS服务接口
 */
public interface AppMarketInviteService {

    /**
     * 生成邀请链接
     *
     * @param inviteLinkDto 请求参数
     * @return 邀请链接响应
     * @throws NoLoginException 未登录异常
     */
    AppResponse<InviteLinkVo> generateInviteLink(InviteLinkDto inviteLinkDto) throws NoLoginException;

    /**
     * 重置邀请链接
     *
     * @param inviteLinkDto 请求参数（只需要marketId）
     * @return 邀请链接响应
     * @throws NoLoginException 未登录异常
     */
    AppResponse<InviteLinkVo> resetInviteLink(InviteLinkDto inviteLinkDto) throws NoLoginException;

    /**
     * 根据邀请key获取邀请信息
     *
     * @param inviteKey 邀请key
     * @return 邀请信息响应（包含邀请人姓名和团队名称）
     */
    AppResponse<InviteInfoVo> getInviteInfoByInviteKey(String inviteKey);

    /**
     * 接受邀请
     *
     * @param inviteKey 邀请key
     * @return 响应结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<AcceptResultVo> acceptInvite(String inviteKey) throws NoLoginException;
}
