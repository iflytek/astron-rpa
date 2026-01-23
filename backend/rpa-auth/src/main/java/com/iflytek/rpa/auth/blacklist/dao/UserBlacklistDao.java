package com.iflytek.rpa.auth.blacklist.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.auth.blacklist.entity.UserBlacklist;
import java.time.LocalDateTime;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 用户黑名单 Mapper 接口
 *
 * @author system
 * @date 2025-12-16
 */
@Mapper
public interface UserBlacklistDao extends BaseMapper<UserBlacklist> {

    /**
     * 查询用户当前生效的封禁记录
     *
     * @param userId 用户ID
     * @return 封禁记录
     */
    UserBlacklist findActiveBlacklist(@Param("userId") String userId);

    /**
     * 查询已过期的封禁记录
     *
     * @param now 当前时间
     * @param limit 限制数量
     * @return 过期的封禁记录列表
     */
    List<UserBlacklist> findExpiredBlacklist(@Param("now") LocalDateTime now, @Param("limit") int limit);

    /**
     * 解封用户（更新状态为已解封）
     *
     * @param id 记录ID
     * @return 影响行数
     */
    int unban(@Param("id") Long id);

    /**
     * 查询用户的封禁历史记录
     *
     * @param userId 用户ID
     * @return 封禁历史列表
     */
    List<UserBlacklist> findHistoryByUserId(@Param("userId") String userId);
}
