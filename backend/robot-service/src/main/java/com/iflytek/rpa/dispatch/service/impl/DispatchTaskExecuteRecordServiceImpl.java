package com.iflytek.rpa.dispatch.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.ROBOT_RESULT_EXECUTE;
import static com.iflytek.rpa.task.constants.TaskConstant.TASK_RESULT_EXECUTE;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.dispatch.dao.DispatchTaskExecuteRecordDao;
import com.iflytek.rpa.dispatch.entity.DispatchTask;
import com.iflytek.rpa.dispatch.entity.DispatchTaskExecuteRecord;
import com.iflytek.rpa.dispatch.entity.DispatchTaskRobotExecuteRecord;
import com.iflytek.rpa.dispatch.entity.dto.RobotExecuteStatusDto;
import com.iflytek.rpa.dispatch.entity.dto.TaskExecuteStatusDto;
import com.iflytek.rpa.dispatch.service.DispatchTaskExecuteRecordService;
import com.iflytek.rpa.robot.entity.vo.RecordLogVo;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.time.Duration;
import java.util.Date;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class DispatchTaskExecuteRecordServiceImpl
        extends ServiceImpl<DispatchTaskExecuteRecordDao, DispatchTaskExecuteRecord>
        implements DispatchTaskExecuteRecordService {

    @Autowired
    private IdWorker idWorker;

    @Value("${deBounce.prefix}")
    private String doBouncePrefix; // 防抖前缀

    @Value("${deBounce.window}")
    private Long deBounceWindow; // 防抖窗口

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<String> reportTaskStatus(TaskExecuteStatusDto statusDto) throws NoLoginException {
        // 生成executeId
        String terminalId = statusDto.getTerminalId();
        if (terminalId == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "终端ID不能为空");
        }
        DispatchTask task = baseMapper.selectTaskById(statusDto.getDispatchTaskId());
        if (task == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "计划任务数据异常");
        }
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        Long taskExecuteId = statusDto.getDispatchTaskExecuteId();
        if (null == taskExecuteId) {
            // 第一次执行
            taskExecuteId = idWorker.nextId();
            DispatchTaskExecuteRecord taskExecuteRecord = new DispatchTaskExecuteRecord();
            taskExecuteRecord.setDispatchTaskId(statusDto.getDispatchTaskId());
            taskExecuteRecord.setDispatchTaskExecuteId(taskExecuteId);
            taskExecuteRecord.setDispatchTaskType(task.getType());
            taskExecuteRecord.setResult(TASK_RESULT_EXECUTE);
            taskExecuteRecord.setTenantId(tenantId);
            taskExecuteRecord.setCreatorId(userId);
            taskExecuteRecord.setTerminalId(terminalId);
            taskExecuteRecord.setUpdaterId(userId);
            taskExecuteRecord.setStartTime(new Date());
            // 获取最大批次号
            Integer maxBatch = baseMapper.getMaxBatch(statusDto.getDispatchTaskId());
            if (null == maxBatch || 0 == maxBatch) {
                taskExecuteRecord.setCount(1);
            } else {
                taskExecuteRecord.setCount(maxBatch + 1);
            }
            // 插入
            baseMapper.insertTaskExecuteRecord(taskExecuteRecord);
            // 返回执行id
            return AppResponse.success(taskExecuteId + "");
        }
        DispatchTaskExecuteRecord record = baseMapper.selectByExecuteId(taskExecuteId);
        //        Integer executeCount = baseMapper.countExecuteRecord(taskExecuteId);
        if (record == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "计划任务执行记录数据异常");
        }
        // 不是第一次执行，更新执行状态
        if (null == statusDto.getResult()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "计划任务执行结果不能为空");
        }
        //        if(null == statusDto.getTaskDetailJson() || "".equals(statusDto.getTaskDetailJson())){
        //            return AppResponse.error(ErrorCodeEnum.E_PARAM, "请传入计划任务详情");
        //        }
        Date startTime = record.getStartTime();
        Date endTime = new Date();
        statusDto.setEndTime(endTime);
        Duration duration = Duration.between(startTime.toInstant(), endTime.toInstant());
        statusDto.setExecuteTime(duration.getSeconds());
        baseMapper.updateTaskExecuteStatus(statusDto);
        return AppResponse.success(taskExecuteId + "");
    }

    @Override
    public AppResponse<String> reportRobotStatus(RobotExecuteStatusDto recordDto) throws NoLoginException {
        Long executeId = recordDto.getExecuteId();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        recordDto.setCreatorId(userId);
        recordDto.setUpdaterId(userId);
        recordDto.setTenantId(tenantId);

        AppResponse<String> currentLevelCodeRes = rpaAuthFeign.getCurrentLevelCode();
        if (!currentLevelCodeRes.ok()) throw new ServiceException("rpa-auth 服务未响应");
        String deptIdPath = currentLevelCodeRes.getData();
        recordDto.setDeptIdPath(deptIdPath);
        // 根据executeId，是否是第一次，是第一次，设置开始时间
        if (null == executeId) {
            if (null == recordDto.getResult() || !ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "执行结果为空或数据错误");
            }
            executeId = idWorker.nextId();
            recordDto.setExecuteId(executeId);
            recordDto.setStartTime(new Date());
            // 插入
            baseMapper.insertRobotExecuteRecord(recordDto);
            return AppResponse.success(executeId + "");
        } else {
            if (null == recordDto.getResult() || ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "执行结果错误");
            }
            DispatchTaskRobotExecuteRecord executeRecord = baseMapper.getRobotExecuteRecord(recordDto);
            if (null == executeRecord || null == executeRecord.getStartTime()) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "执行记录数据异常");
            }

            Date endTime = new Date();
            recordDto.setEndTime(endTime);
            // 计算执行耗时
            recordDto.setExecuteTime(endTime.toInstant().getEpochSecond()
                    - executeRecord.getStartTime().toInstant().getEpochSecond());
            baseMapper.updateRobotExecuteRecord(recordDto);
        }
        return AppResponse.success("任务结束");
    }

    @Override
    public AppResponse<RecordLogVo> getRobotExecuteLog(Long executeId) throws NoLoginException {
        if (executeId == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人执行ID不能为空");
        }

        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        RecordLogVo executeLog = baseMapper.getRobotExecuteLog(executeId, tenantId);

        if (executeLog == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "未查询到该机器人执行记录");
        }

        return AppResponse.success(executeLog);
    }
}
