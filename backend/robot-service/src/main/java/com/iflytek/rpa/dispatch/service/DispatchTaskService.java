package com.iflytek.rpa.dispatch.service;

import com.iflytek.rpa.dispatch.entity.vo.TerminalTaskDetailVo;
import com.iflytek.rpa.utils.response.AppResponse;

public interface DispatchTaskService {
    /**
     * 获取终端任务详情
     *
     * @param terminalId 终端ID
     * @return 终端任务详情
     */
    AppResponse<TerminalTaskDetailVo> getTerminalTaskDetail(String terminalId);

    /**
     * 轮询检查指定终端是否有任务更新
     *
     * @param terminalId 终端ID
     * @return true表示有数据更新，false表示无数据更新
     */
    boolean checkTaskUpdate(String terminalId);
}
