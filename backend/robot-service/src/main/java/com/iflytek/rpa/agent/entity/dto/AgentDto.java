package com.iflytek.rpa.agent.entity.dto;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import java.util.List;
import lombok.Data;
import lombok.experimental.Accessors;

/**
 * Agent操作DTO
 * 会话记录存储在content JSON中
 */
@Data
@Accessors(chain = true)
public class AgentDto {

    /**
     * RPA Agent ID
     */
    private String agentId;

    /**
     * Agent名称
     */
    private String agentName;

    /**
     * 系统提示词
     */
    private String systemPrompt;

    /**
     * MCP服务器列表
     */
    private JSONArray mcpServers;

    /**
     * RPA机器人配置
     */
    private JSONObject rpaRobots;

    /**
     * 会话记录列表
     * 在content JSON中存储，格式：
     * [
     *   {"role": "user", "content": "用户消息", "timestamp": "2025-01-01 10:00:00"},
     *   {"role": "assistant", "content": "AI回复", "timestamp": "2025-01-01 10:00:01"}
     * ]
     */
    private List<ChatMessage> chatHistory;
}
