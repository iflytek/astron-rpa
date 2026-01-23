package com.iflytek.rpa.auth.sp.casdoor.entity;

import lombok.Data;

/**
 * Casdoor 登录结果
 */
@Data
public class CasdoorLoginResult {
    /**
     * 用户ID
     */
    private String userId;

    /**
     * Casdoor Session ID（从响应头 Set-Cookie 中提取的 casdoor_session_id 值）
     */
    private String session;
}
