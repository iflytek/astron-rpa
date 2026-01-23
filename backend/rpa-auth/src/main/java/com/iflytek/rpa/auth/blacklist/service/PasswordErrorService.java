package com.iflytek.rpa.auth.blacklist.service;

/**
 * 密码错误计数服务
 *
 * @author system
 * @date 2025-12-16
 */
public interface PasswordErrorService {

    /**
     * 记录密码错误
     * 如果达到阈值，抛出 ShouldBeBlackException
     *
     * @param userId 用户ID
     * @param username 用户名
     * @return 当前错误次数
     */
    int recordPasswordError(String userId, String username);

    /**
     * 清除密码错误记录
     * 登录成功后调用
     *
     * @param userId 用户ID
     */
    void clearPasswordError(String userId);

    /**
     * 获取当前密码错误次数
     *
     * @param userId 用户ID
     * @return 错误次数
     */
    int getPasswordErrorCount(String userId);
}
