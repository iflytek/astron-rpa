package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketInvite;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 团队市场-邀请链接表
 */
@Mapper
public interface AppMarketInviteDao extends BaseMapper<AppMarketInvite> {
    /**
     * 根据邀请key查询邀请链接（未删除的）
     *
     * @param inviteKey 邀请key
     * @return 邀请链接实体
     */
    AppMarketInvite selectByInviteKey(@Param("inviteKey") String inviteKey);

    AppMarketInvite selectByMarketIdAndInviterId(String marketId, String userId);

    int cancelById(Long id);
}
