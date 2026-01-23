package com.iflytek.rpa.agent.entity.dto;

import lombok.Data;
import lombok.experimental.Accessors;

/**
 * 会话消息结构
 */
@Data
@Accessors(chain = true)
public class ChatMessage {

    /**
     * 角色：user或assistant
     */
    private String role;

    /**
     * 消息内容
     */
    private String content;

    /**
     * 创建时间
     */
    private String createTime;
}
