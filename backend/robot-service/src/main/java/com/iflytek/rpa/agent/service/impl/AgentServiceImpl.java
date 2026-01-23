package com.iflytek.rpa.agent.service.impl;

import com.alibaba.fastjson.JSON;
import com.iflytek.rpa.agent.dao.AgentDao;
import com.iflytek.rpa.agent.entity.Agent;
import com.iflytek.rpa.agent.entity.dto.AgentDto;
import com.iflytek.rpa.agent.entity.vo.AgentVo;
import com.iflytek.rpa.agent.service.AgentService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * Agent Service实现类
 */
@Service
public class AgentServiceImpl implements AgentService {

    @Resource
    private IdWorker idWorker;

    @Resource
    private AgentDao agentDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<AgentVo> save(AgentDto agentDto) throws NoLoginException {
        String agentId = agentDto.getAgentId();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();

        // 将DTO转换为JSON字符串存储
        String content = JSON.toJSONString(agentDto);

        Agent agent = new Agent().setAgentId(agentId).setContent(content).setUpdaterId(userId);

        // agentId不存在，则创建新的agentId
        if (StringUtils.isEmpty(agentId)) {
            agentId = "agent_" + idWorker.nextId();
            agent.setCreatorId(userId).setAgentId(agentId);
            agentDto.setAgentId(agentId); // 更新DTO中的agentId
            content = JSON.toJSONString(agentDto); // 重新序列化
            agent.setContent(content);
            create(agent);
            // 保存接口只返回agentId
            return AppResponse.success(new AgentVo().setAgentId(agentId));
        }

        // agentId存在，则更新已有的Agent配置
        int result = agentDao.updateContent(agent);
        if (result != 1) {
            throw new RuntimeException("Failed to update agent configuration");
        }

        return AppResponse.success(new AgentVo().setAgentId(agentId));
    }

    @Override
    public AppResponse<AgentVo> getByAgentId(String agentId) {
        Agent agent = agentDao.getByAgentId(agentId);

        if (agent == null) {
            AppResponse<AgentVo> response = AppResponse.success(null);
            response.setMessage("Agent configuration not found");
            return response;
        }

        // 将存储的JSON字符串解析为DTO
        AgentDto agentDto = JSON.parseObject(agent.getContent(), AgentDto.class);

        // 按照API规范，返回扁平化的AgentVo
        AgentVo agentVo = new AgentVo()
                .setAgentId(agent.getAgentId())
                .setAgentName(agentDto.getAgentName())
                .setSystemPrompt(agentDto.getSystemPrompt())
                .setMcpServers(agentDto.getMcpServers())
                .setRpaRobots(agentDto.getRpaRobots())
                .setChatHistory(agentDto.getChatHistory());

        return AppResponse.success(agentVo);
    }

    @Override
    public AppResponse<AgentVo> delete(String agentId) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();

        int result = agentDao.deleteAgent(agentId, userId);

        if (result != 1) {
            throw new RuntimeException("Failed to delete agent configuration");
        }
        return AppResponse.success(new AgentVo().setAgentId(agentId));
    }

    @Override
    public AppResponse<List<AgentVo>> listAllAgents() throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();

        List<Agent> agentList = agentDao.listAgentsByUserId(userId);

        List<AgentVo> agentVoList = agentList.stream()
                .map(agent -> {
                    // 将存储的JSON字符串解析为DTO
                    AgentDto agentDto = JSON.parseObject(agent.getContent(), AgentDto.class);

                    // 按照API规范，返回扁平化的AgentVo
                    return new AgentVo()
                            .setAgentId(agent.getAgentId())
                            .setAgentName(agentDto.getAgentName())
                            .setSystemPrompt(agentDto.getSystemPrompt())
                            .setMcpServers(agentDto.getMcpServers())
                            .setRpaRobots(agentDto.getRpaRobots())
                            .setChatHistory(agentDto.getChatHistory());
                })
                .collect(Collectors.toList());

        return AppResponse.success(agentVoList);
    }

    /**
     * 创建新的Agent配置
     */
    private Integer create(Agent agent) {
        int insert = agentDao.insertAgent(agent);

        if (insert != 1) {
            throw new RuntimeException("Failed to create agent configuration");
        }

        return insert;
    }

    @Override
    public AppResponse<AgentVo> create(String agentName) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();

        // 生成新的agentId
        String agentId = "agent_" + idWorker.nextId();

        // 构建最小内容的DTO，仅包含agentId与agentName
        AgentDto agentDto = new AgentDto().setAgentId(agentId).setAgentName(agentName);

        String content = JSON.toJSONString(agentDto);

        Agent agent = new Agent()
                .setAgentId(agentId)
                .setContent(content)
                .setCreatorId(userId)
                .setUpdaterId(userId);

        create(agent);

        return AppResponse.success(new AgentVo().setAgentId(agentId));
    }
}
