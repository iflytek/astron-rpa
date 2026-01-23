package com.iflytek.rpa.agent.service;

import com.iflytek.rpa.agent.entity.dto.AgentDto;
import com.iflytek.rpa.agent.entity.vo.AgentVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;

/**
 * Agent Service接口
 */
public interface AgentService {

    /**
     * 保存Agent配置
     *
     * @param agentDto Agent配置信息
     * @return 保存结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<AgentVo> save(AgentDto agentDto) throws NoLoginException;

    /**
     * 根据AgentId获取配置信息
     *
     * @param agentId Agent ID
     * @return Agent详情
     * @throws NoLoginException 未登录异常
     */
    AppResponse<AgentVo> getByAgentId(String agentId);

    /**
     * 删除Agent配置
     *
     * @param agentId Agent ID
     * @return 删除结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<AgentVo> delete(String agentId) throws NoLoginException;

    /**
     * 获取所有Agent配置
     *
     * @return 所有Agent配置
     * @throws NoLoginException 未登录异常
     */
    AppResponse<List<AgentVo>> listAllAgents() throws NoLoginException;

    /**
     * 新建Agent，仅入参agentName，返回agentId
     *
     * @param agentName Agent名称
     * @return 仅包含agentId的结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<AgentVo> create(String agentName) throws NoLoginException;
}
