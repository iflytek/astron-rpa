package com.iflytek.rpa.robot.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.ROBOT_RESULT_EXECUTE;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.dispatch.entity.dto.RobotExecuteStatusDto;
import com.iflytek.rpa.dispatch.service.DispatchTaskExecuteRecordService;
import com.iflytek.rpa.monitor.entity.RobotMonitorDto;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteRecordsBatchDeleteDto;
import com.iflytek.rpa.robot.service.HisDataEnumService;
import com.iflytek.rpa.robot.service.RobotExecuteRecordService;
import com.iflytek.rpa.task.dao.ScheduleTaskDao;
import com.iflytek.rpa.utils.DateUtils;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.NumberUtils;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.math.BigDecimal;
import java.util.Date;
import java.util.List;
import java.util.Objects;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 云端机器人执行记录表(RobotExecute)表服务实现类
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Slf4j
@Service("robotExecuteRecordService")
public class RobotExecuteRecordServiceImpl extends ServiceImpl<RobotExecuteRecordDao, RobotExecuteRecord>
        implements RobotExecuteRecordService {

    @Autowired
    private RobotExecuteRecordDao robotExecuteRecordDao;

    @Autowired
    private HisDataEnumService hisDataEnumService;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    ScheduleTaskDao scheduleTaskDao;

    @Autowired
    private DispatchTaskExecuteRecordService dispatchTaskExecuteRecordService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<?> recordList(ExecuteRecordDto recordDto) throws NoLoginException {
        IPage<RobotExecuteRecord> pages = new Page<>();
        if (null == recordDto.getPageNo() || null == recordDto.getPageSize()) {
            return AppResponse.success(pages);
        }
        AppResponse<User> resp = rpaAuthFeign.getLoginUser();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = resp.getData();
        String userId = loginUser.getId();

        recordDto.setCreatorId(userId);
        AppResponse<String> res = rpaAuthFeign.getTenantId();
        if (res == null || res.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = res.getData();
        recordDto.setTenantId(tenantId);
        IPage<RobotExecuteRecord> pageConfig = new Page<>(recordDto.getPageNo(), recordDto.getPageSize(), true);
        pages = robotExecuteRecordDao.getExecuteRecordList(pageConfig, recordDto);
        List<RobotExecuteRecord> list = pages.getRecords();
        if (list.isEmpty()) {
            AppResponse.success(pages);
        }
        packageTaskInfo(list);
        return AppResponse.success(pages);
    }

    private void packageTaskInfo(List<RobotExecuteRecord> list) {
        for (RobotExecuteRecord robotExecuteRecord : list) {
            String taskExecuteId = robotExecuteRecord.getTaskExecuteId();
            if (!StringUtils.isEmpty(taskExecuteId)) {
                String taskName = scheduleTaskDao.getTaskNameByTaskExecuteId(taskExecuteId);
                if (taskName != null && !StringUtils.isEmpty(taskName)) {
                    robotExecuteRecord.setTaskName(taskName);
                } else {
                    robotExecuteRecord.setTaskName(null);
                }
            }
        }
    }

    @Override
    public AppResponse<?> getExecuteLog(ExecuteRecordDto recordDto) throws NoLoginException {
        String executeId = recordDto.getExecuteId();
        if (null == executeId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "执行ID为空");
        }
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
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
        recordDto.setTenantId(tenantId);
        String executeLog = robotExecuteRecordDao.getExecuteLog(recordDto);
        return AppResponse.success(executeLog);
    }

    @Override
    public AppResponse<?> robotOverview(RobotMonitorDto robotMonitorDto) {

        //        Date date = DateUtil.parse(deadline);
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (null == tenantId) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "租户信息获取失败");
        }
        String robotId = robotMonitorDto.getRobotId();
        // 今天的和历史的都需要实时统计，因为表里面没存累计历史数据，只存了每日历史数据
        Date countTime = DateUtils.getEndOfDay(robotMonitorDto.getDeadline());
        RobotMonitorDto robotMonitorData =
                robotExecuteRecordDao.robotOverview(tenantId, robotId, countTime, robotMonitorDto.getVersion());
        robotMonitorData.setExecuteSuccessRate(NumberUtils.getRate(
                new BigDecimal(robotMonitorData.getExecuteSuccess()),
                new BigDecimal(robotMonitorData.getExecuteTotal())));
        robotMonitorData.setExecuteFailRate(NumberUtils.getRate(
                new BigDecimal(robotMonitorData.getExecuteFail()), new BigDecimal(robotMonitorData.getExecuteTotal())));
        robotMonitorData.setExecuteAbortRate(NumberUtils.getRate(
                new BigDecimal(robotMonitorData.getExecuteAbort()),
                new BigDecimal(robotMonitorData.getExecuteTotal())));
        robotMonitorData.setExecuteRunningRate(NumberUtils.getRate(
                new BigDecimal(robotMonitorData.getExecuteRunning()),
                new BigDecimal(robotMonitorData.getExecuteTotal())));
        return AppResponse.success(
                hisDataEnumService.getOverViewData("robotOverview", robotMonitorData, RobotMonitorDto.class));
    }

    @Override
    @RobotVersionAnnotation(clazz = ExecuteRecordDto.class)
    public AppResponse<?> saveExecuteResult(ExecuteRecordDto recordDto, String currentRobotId) throws NoLoginException {
        // 判断是否为dispatch模式
        if (recordDto.getIsDispatch() != null && recordDto.getIsDispatch()) {
            // 调用dispatch服务
            RobotExecuteStatusDto statusDto = new RobotExecuteStatusDto();
            statusDto.setExecuteId(recordDto.getExecuteId() != null ? Long.valueOf(recordDto.getExecuteId()) : null);
            statusDto.setRobotId(recordDto.getRobotId());
            statusDto.setRobotVersion(recordDto.getRobotVersion());
            statusDto.setDispatchTaskExecuteId(recordDto.getDispatchTaskExecuteId());
            statusDto.setTerminalId(recordDto.getTerminalId());
            statusDto.setResult(recordDto.getResult());
            statusDto.setError_reason(recordDto.getError_reason());
            statusDto.setExecuteLog(recordDto.getExecuteLog());
            statusDto.setVideoLocalPath(recordDto.getVideoLocalPath());
            statusDto.setParamJson(recordDto.getParamJson());

            return dispatchTaskExecuteRecordService.reportRobotStatus(statusDto);
        }

        // 原有业务逻辑
        String executeId = recordDto.getExecuteId();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
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
        recordDto.setRobotId(currentRobotId);

        AppResponse<String> currentLevelCodeRes = rpaAuthFeign.getCurrentLevelCode();
        if (!currentLevelCodeRes.ok()) throw new ServiceException("rpa-auth 服务未响应");
        String deptIdPath = currentLevelCodeRes.getData();
        recordDto.setDeptIdPath(deptIdPath);
        // 根据executeId，是否是第一次，是第一次，设置开始时间
        if (null == executeId) {
            if (null == recordDto.getResult() || !ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "执行结果为空或数据错误");
            }
            executeId = idWorker.nextId() + "";
            recordDto.setExecuteId(executeId);
            recordDto.setStartTime(new Date());
            // 插入
            robotExecuteRecordDao.insertExecuteRecord(recordDto);
        } else {
            if (null == recordDto.getResult() || ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "执行结果错误");
            }
            RobotExecuteRecord executeRecord = robotExecuteRecordDao.getExecuteRecord(recordDto);
            if (null == executeRecord || null == executeRecord.getStartTime()) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "执行记录数据异常");
            }

            Date endTime = new Date();
            recordDto.setEndTime(endTime);
            // 计算执行耗时
            recordDto.setExecuteTime(endTime.toInstant().getEpochSecond()
                    - executeRecord.getStartTime().toInstant().getEpochSecond());
            robotExecuteRecordDao.updateExecuteRecord(recordDto);
        }
        return AppResponse.success(executeId);
    }

    @Override
    public AppResponse<String> deleteRobotExecuteRecords(RobotExecuteRecordsBatchDeleteDto batchDeleteDto)
            throws NoLoginException {
        // 批量删除机器人执行记录
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        List<String> recordsIds = batchDeleteDto.getRecordIds();
        recordsIds.removeIf(Objects::isNull);
        if (recordsIds.isEmpty()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "任务执行ID列表不能为空");
        }
        // 2. 批量删除
        int deleted = baseMapper.deleteRobotExecuteRecords(recordsIds, userId, tenantId);
        if (deleted != recordsIds.size()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "批量删除共享文件失败");
        }
        return AppResponse.success("删除成功");
    }
}
