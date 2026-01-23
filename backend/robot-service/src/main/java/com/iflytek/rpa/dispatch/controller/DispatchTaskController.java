package com.iflytek.rpa.dispatch.controller;

import com.iflytek.rpa.dispatch.entity.vo.TerminalTaskDetailVo;
import com.iflytek.rpa.dispatch.service.DispatchTaskService;
import com.iflytek.rpa.utils.response.AppResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 调度管理-计划任务
 *
 * @author jqfang
 * @since 2025-08-15
 */
@RestController
@RequestMapping("dispatch-task")
@Slf4j
public class DispatchTaskController {

    @Autowired
    private DispatchTaskService dispatchTaskService;

    /**
     * 轮询检查指定终端是否有任务更新
     *
     * @param terminalId 终端ID
     * @return true表示有数据更新，false表示无数据更新
     */
    @GetMapping("/poll-task-update")
    public AppResponse<Boolean> pollTaskUpdate(@RequestParam("terminalId") String terminalId) {
        boolean hasUpdate = dispatchTaskService.checkTaskUpdate(terminalId);
        return AppResponse.success(hasUpdate);
    }

    /**
     * 获取终端任务详情
     *
     * @param terminalId 终端ID
     * @return 终端任务详情
     */
    @GetMapping("/terminal-task-detail")
    public AppResponse<TerminalTaskDetailVo> getTerminalTaskDetail(@RequestParam("terminalId") String terminalId) {
        return dispatchTaskService.getTerminalTaskDetail(terminalId);
    }
}
