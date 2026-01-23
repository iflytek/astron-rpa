package com.iflytek.rpa.auth.blacklist.service;

import com.iflytek.rpa.auth.blacklist.dto.BlacklistCacheDto;
import com.iflytek.rpa.auth.blacklist.entity.UserBlacklist;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * 黑名单服务接口
 *
 * @author system
 * @date 2025-12-16
 */
public interface BlackListService {

    /**
     * 添加用户到黑名单
     * 如果用户已在黑名单中，则升级封禁等级
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param reason 封禁原因
     * @param operator 操作人
     * @return 黑名单记录
     */
    UserBlacklist add(String userId, String username, String reason, String operator);

    /**
     * 检查用户是否被封禁
     * 优先从 Redis 查询，miss 时查 DB 并回填
     *
     * @param userId 用户ID
     * @return 如果被封禁返回封禁信息，否则返回 null
     */
    BlacklistCacheDto isBlocked(String userId);

    /**
     * 解封用户（如果已过期）
     *
     * @param userId 用户ID
     */
    void unbanIfExpired(String userId);

    /**
     * 手动解封用户
     *
     * @param userId 用户ID
     * @param operator 操作人
     * @return 是否成功
     */
    boolean unban(String userId, String operator);

    /**
     * 查询用户的封禁历史
     *
     * @param userId 用户ID
     * @return 封禁历史列表
     */
    List<UserBlacklist> getHistory(String userId);

    /**
     * 定时任务：批量解封已过期的用户
     *
     * @return 解封数量
     */
    int batchUnbanExpired();

    /**
     * 强制注销用户会话
     * 从 request 中清除会话信息，调用 UapUserInfoAPI.logout 注销会话
     *
     * @param request HTTP 请求
     * @param response HTTP 响应
     */
    void forceLogout(HttpServletRequest request, HttpServletResponse response);
}
