package com.iflytek.rpa.agent.entity.vo;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.agent.entity.dto.ChatMessage;
import java.util.List;
import lombok.Data;
import lombok.experimental.Accessors;

/**
 * Agent返回VO
 * 用于列表返回（扁平化结构）
 */
@Data
@Accessors(chain = true)
public class AgentVo {

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
     */
    private List<ChatMessage> chatHistory;
}
