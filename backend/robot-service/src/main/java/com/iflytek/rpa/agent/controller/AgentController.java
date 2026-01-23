package com.iflytek.rpa.agent.controller;

import com.iflytek.rpa.agent.entity.dto.AgentDto;
import com.iflytek.rpa.agent.entity.vo.AgentVo;
import com.iflytek.rpa.agent.service.AgentService;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

/**
 * Agent配置控制器
 */
@RestController
@RequestMapping("/agent")
public class AgentController {

    @Resource
    private AgentService agentService;

    /**
     * 保存Agent配置
     *
     * @param agentDto Agent配置信息
     * @return 保存结果
     * @throws Exception 异常
     */
    @PostMapping("/save")
    public AppResponse<AgentVo> save(@RequestBody AgentDto agentDto) throws Exception {
        return agentService.save(agentDto);
    }

    /**
     * 根据AgentId获取配置信息
     *
     * @param agentId Agent ID
     * @return Agent配置信息
     * @throws Exception 异常
     */
    @GetMapping("/detail")
    public AppResponse<AgentVo> getByAgentId(@RequestParam("agentId") String agentId) throws Exception {
        return agentService.getByAgentId(agentId);
    }

    /**
     * 删除Agent配置
     *
     * @param agentId Agent ID
     * @return 删除结果
     * @throws Exception 异常
     */
    @GetMapping("/delete")
    public AppResponse<AgentVo> delete(@RequestParam("agentId") String agentId) throws Exception {
        return agentService.delete(agentId);
    }

    /**
     * 获取所有Agent配置列表
     *
     * @return 所有Agent配置
     * @throws Exception 异常
     */
    @GetMapping("/list")
    public AppResponse<List<AgentVo>> listAllAgents() throws Exception {
        return agentService.listAllAgents();
    }

    /**
     * 新建Agent，仅入参agentName，返回agentId
     *
     * @param agentName Agent名称
     * @return 仅包含agentId的结果
     * @throws Exception 异常
     */
    @PostMapping("/create")
    public AppResponse<AgentVo> create(@RequestBody AgentDto agentDto) throws Exception {
        return agentService.create(agentDto.getAgentName());
    }
}
