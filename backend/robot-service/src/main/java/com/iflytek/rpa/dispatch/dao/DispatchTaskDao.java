package com.iflytek.rpa.dispatch.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.dispatch.entity.DispatchTask;
import com.iflytek.rpa.dispatch.entity.vo.TerminalTaskDetailVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 调度模式-计划任务 Mapper 接口
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Mapper
public interface DispatchTaskDao extends BaseMapper<DispatchTask> {
    /**
     * 根据终端ID查询任务信息
     *
     * @param terminalId 终端ID
     * @return 任务信息列表
     */
    List<TerminalTaskDetailVo.DispatchTaskInfo> selectTaskInfoByTerminalId(@Param("terminalId") String terminalId);
    /**
     * 根据任务ID查询手动任务详情
     *
     * @param taskId 任务ID
     * @return 任务信息
     */
    TerminalTaskDetailVo.DispatchTaskInfo selectTaskInfoByTaskId(@Param("taskId") String taskId);
    /**
     * 根据任务ID列表批量查询机器人信息
     *
     * @param taskIds 任务ID列表
     * @return 机器人信息列表
     */
    List<TerminalTaskDetailVo.DispatchRobotInfo> selectRobotInfoByTaskIds(@Param("taskIds") List<String> taskIds);
}
