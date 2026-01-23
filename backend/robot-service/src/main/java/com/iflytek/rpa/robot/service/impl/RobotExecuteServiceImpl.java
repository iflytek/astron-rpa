package com.iflytek.rpa.robot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.market.dao.AppMarketResourceDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.dao.AppMarketVersionDao;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.AppMarketVersion;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.robot.constants.RobotConstant;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.RobotExecuteService;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.triggerTask.dao.TriggerTaskDao;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * 云端机器人表(RobotExecute)表服务实现类
 *
 * @author mjren
 * @since 2024-10-22 16:07:33
 */
@Service("robotExecuteService")
public class RobotExecuteServiceImpl extends ServiceImpl<RobotExecuteDao, RobotExecute> implements RobotExecuteService {
    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Resource
    private AppMarketVersionDao appVersionDao;

    @Resource
    private AppMarketResourceDao appResourceDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private TriggerTaskDao triggerTaskDao;

    @Resource
    private RobotExecuteRecordDao robotExecuteRecordDao;

    @Autowired
    private AppApplicationService appApplicationService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    private final String filePathPrefix = "/api/resource/file/download?fileId=";

    private static List<ExeUpdateCheckVo> getExeUpdateCheckVos(List<RobotExecute> robotExecuteList) {
        List<ExeUpdateCheckVo> resVoList = new ArrayList<>();
        for (RobotExecute robotExecute : robotExecuteList) {
            Integer updateStatus = 0;
            if (robotExecute.getResourceStatus() != null) {
                updateStatus = robotExecute.getResourceStatus().equals("toUpdate") ? 1 : 0;
            } else {
                updateStatus = 0;
            }
            ExeUpdateCheckVo exeUpdateCheckVo = new ExeUpdateCheckVo();

            exeUpdateCheckVo.setAppId(robotExecute.getAppId());
            exeUpdateCheckVo.setRobotId(robotExecute.getRobotId());
            exeUpdateCheckVo.setUpdateStatus(updateStatus);

            resVoList.add(exeUpdateCheckVo);
        }
        return resVoList;
    }

    @Override
    public AppResponse<?> executeList(ExecuteListDto queryDto) throws NoLoginException {

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

        Long pageNo = queryDto.getPageNo();
        Long pageSize = queryDto.getPageSize();
        String name = queryDto.getName();
        String sortType = StringUtils.isBlank(queryDto.getSortType()) ? "desc" : queryDto.getSortType();

        IPage<RobotExecute> page = new Page<>(pageNo, pageSize);
        LambdaQueryWrapper<RobotExecute> wrapper = new LambdaQueryWrapper<>();

        // userID tenantId 筛选
        wrapper.eq(RobotExecute::getCreatorId, userId);
        wrapper.eq(RobotExecute::getTenantId, tenantId);
        wrapper.eq(RobotExecute::getDeleted, 0);

        // 名字模糊匹配
        if (StringUtils.isNotBlank(name)) {
            wrapper.like(RobotExecute::getName, name);
        }

        // 更新时间排序
        if (sortType.equals("asc")) wrapper.orderByAsc(RobotExecute::getUpdateTime);
        else wrapper.orderByDesc(RobotExecute::getUpdateTime);

        IPage<RobotExecute> rePage = this.page(page, wrapper);
        List<RobotExecute> recordRobotList = rePage.getRecords();

        if (CollectionUtils.isEmpty(recordRobotList)) return AppResponse.success(rePage);

        IPage<ExecuteListVo> ansPage = new Page<>(pageNo, pageSize);
        List<ExecuteListVo> ansRecords = new ArrayList<>();

        for (RobotExecute record : recordRobotList) {
            String dataSource = record.getDataSource();
            String sourceName;
            String appId = "";
            Integer updateStatus = 0;
            updateStatus = StringUtils.isNotBlank(record.getResourceStatus())
                            && record.getResourceStatus().equals("toUpdate")
                    ? 1
                    : 0;

            if (dataSource.equals("create")) {
                sourceName = RobotConstant.CREATE_NAME;
            } else if (dataSource.equals("deploy")) {
                sourceName = RobotConstant.DEPLOY_NAME;
            } else {
                sourceName = RobotConstant.MARKET_NAME;
                appId = record.getAppId();
            }

            ExecuteListVo executeListVo = new ExecuteListVo();

            executeListVo.setRobotName(record.getName());
            executeListVo.setUpdateTime(record.getUpdateTime());
            executeListVo.setRobotId(record.getRobotId());
            executeListVo.setSourceName(sourceName);
            executeListVo.setAppId(appId);
            executeListVo.setAppVersion(record.getAppVersion());
            executeListVo.setUpdateStatus(updateStatus);

            ansRecords.add(executeListVo);
        }

        setExecuteListRecord(ansRecords, recordRobotList);

        // 开启上架审核后，填充使用权限
        appApplicationService.packageUsePermission(ansRecords);

        ansPage.setSize(rePage.getSize());
        ansPage.setTotal(rePage.getTotal());
        ansPage.setRecords(ansRecords);

        return AppResponse.success(ansPage);
    }

    private void setExecuteListRecord(List<ExecuteListVo> ansRecords, List<RobotExecute> robotList) {

        // 只查询自己创建的机器人的版本信息，避免市场机器人的版本污染
        List<String> createRobotIdList = robotList.stream()
                .filter(robot -> RobotConstant.CREATE.equals(robot.getDataSource()))
                .map(RobotExecute::getRobotId)
                .collect(Collectors.toList());

        List<RobotVersion> robotVersionList = CollectionUtils.isEmpty(createRobotIdList)
                ? new ArrayList<>()
                : robotDesignDao.getRobotVersionList(createRobotIdList);

        for (ExecuteListVo ansRecord : ansRecords) {
            String robotId = ansRecord.getRobotId();

            // 根据数据来源决定版本获取方式
            if (RobotConstant.CREATE_NAME.equals(ansRecord.getSourceName())) {
                // 自己创建的机器人，从robot_version表查询版本
                List<RobotVersion> robotVersionsTmp = robotVersionList.stream()
                        .filter(robotVersion -> robotVersion.getRobotId().equals(robotId))
                        .collect(Collectors.toList());

                if (!CollectionUtils.isEmpty(robotVersionsTmp)) {
                    // 展示启用版本
                    RobotVersion robotVersion = robotVersionsTmp.stream()
                            .filter(robotVersion1 -> robotVersion1.getOnline().equals(1))
                            .collect(Collectors.toList())
                            .get(0);

                    ansRecord.setVersion(robotVersion.getVersion());
                } else {
                    // 没有版本记录，设为0
                    ansRecord.setVersion(0);
                }
            } else {
                // 从市场获取的机器人，直接使用app_version作为版本号
                ansRecord.setVersion(ansRecord.getAppVersion());
            }
        }
    }

    @Override
    public AppResponse<?> updateRobotByPull(String robotId) throws NoLoginException {
        // 更新robotID机器人的appVersion,name,updatetime,obtained,
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
        RobotExecute robotExecute = robotExecuteDao.queryByRobotId(robotId, userId, tenantId);
        if (robotExecute == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人不存在");
        }
        // 查询是否已退出市场
        String marketId = robotExecute.getMarketId();
        if (StringUtils.isBlank(marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场信息缺失");
        }
        AppMarketUser appMarketUser = appMarketUserDao.getMarketUser(marketId, userId);
        if (null == appMarketUser) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "当前未加入该机器人所在的团队市场，且点击后按钮消失");
        }
        // 查询市场中机器人的版本信息
        RobotVersionDto robotVersion = robotVersionDao.getLatestRobotVersion(robotExecute.getAppId());
        if (null == robotVersion) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "应用市场机器人不存在");
        }
        robotExecute.setAppVersion(robotVersion.getVersion());
        robotExecute.setName(robotVersion.getName());
        robotExecuteDao.updateRobotByPull(robotExecute);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> deleteRobotRes(String robotId) throws NoLoginException {

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

        if (StringUtils.isBlank(robotId)) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);

        RobotExecute robotExecute = robotExecuteDao.getRobotExecute(robotId, userId, tenantId);
        if (robotExecute == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);

        // 执行器只能删除市场获取的
        if (robotExecute.getDataSource().equals("create")) return AppResponse.error("只能在设计器中删除该机器人");

        // 获取所有引用该机器人的task
        List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotDao.getAllTaskRobot(robotId, userId, tenantId);

        DelExecuteRobotVo resVo = getDeleteRobotVo(robotExecute, taskRobotList, robotId);

        return AppResponse.success(resVo);
    }

    @Override
    public AppResponse<?> deleteRobot(DeleteDesignDto queryDto) throws Exception {

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

        Integer situation = queryDto.getSituation();
        String robotId = queryDto.getRobotId();
        String taskIds = queryDto.getTaskIds();

        // 删除相关的执行记录
        Integer n = robotExecuteRecordDao.deleteRecord(tenantId, robotId, userId);

        switch (situation) {
            case 1: // 只有执行器中存在
                Integer i = robotExecuteDao.deleteExecute(robotId, userId, tenantId);

                if (i.equals(1)) return AppResponse.success("删除执行器成功");
                else throw new Exception(); // 回滚

            case 3: // 设计器、 执行期、 计划任务也引用
                if (StringUtils.isBlank(taskIds)) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);

                List<String> taskIdList = Arrays.stream(taskIds.split(",")).collect(Collectors.toList());
                Integer y = robotExecuteDao.deleteExecute(robotId, userId, tenantId);
                Integer z = scheduleTaskRobotDao.taskRobotDelete(robotId, userId, tenantId, taskIdList);

                // 删除taskRobot后处理
                taskRobotDeleteAfter(taskIdList);

                if (y.equals(1) && z.equals(taskIdList.size())) {
                    return AppResponse.success("执行器,相关计划任务引用成功");
                } else throw new Exception();

            default:
                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
        }
    }

    @Override
    public AppResponse<?> robotDetail(String robotId) throws Exception {

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

        ExecuteDetailVo resVo = new ExecuteDetailVo();

        RobotExecute robotExecute = robotExecuteDao.getRobotExecute(robotId, userId, tenantId);
        RobotVersion robotVersion = null;
        if (robotExecute.getDataSource().equals("create")) {
            // 如果是自己获取的, 采用启用版本
            robotVersion = robotVersionDao.getEnableVersion(robotId, userId, tenantId);
        } else if (robotExecute.getDataSource().equals("market")) {
            // 如果是市场中获取的，用溯源的最新版本
            AppMarketResource appResource =
                    appResourceDao.getAppResourceRegardlessDel(robotExecute.getAppId(), robotExecute.getMarketId());
            robotVersion = robotVersionDao.getLatestVersionRegardlessDel(appResource.getRobotId());
        } else if (robotExecute.getDataSource().equals("deploy")) {
            String oriRobotId = robotExecute.getAppId();
            robotVersion = robotVersionDao.getDeployEnableVersion(oriRobotId, tenantId);
        }
        if (robotExecute == null || robotVersion == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY);
        }

        // set 基本信息
        setBasicInfo(robotExecute, robotVersion, resVo);

        // set 版本信息
        setVersionNCreatorInfo(robotExecute, resVo, robotExecute.getDataSource(), userId, tenantId);

        return AppResponse.success(resVo);
    }

    @Override
    public AppResponse<?> executeUpdateCheck(ExeUpdateCheckDto queryDto) throws NoLoginException {

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

        String appIdListStr = queryDto.getAppIdListStr();
        String robotIdListStr = queryDto.getRobotIdListStr();

        if (StringUtils.isBlank(appIdListStr)) return AppResponse.error(ErrorCodeEnum.E_PARAM);
        if (StringUtils.isBlank(robotIdListStr)) return AppResponse.error(ErrorCodeEnum.E_PARAM);

        List<String> appIdList = Arrays.stream(appIdListStr.split(",")).collect(Collectors.toList());
        List<String> robotIdList = Arrays.stream(robotIdListStr.split(",")).collect(Collectors.toList());

        if (appIdList.size() != robotIdList.size()) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);

        List<RobotExecute> queryInfoList = getQueryInfo(appIdList, robotIdList);

        List<RobotExecute> robotExecuteList = robotExecuteDao.getExeByAppIdsRobotIds(userId, tenantId, queryInfoList);

        List<ExeUpdateCheckVo> resVoList = getExeUpdateCheckVos(robotExecuteList);

        return AppResponse.success(resVoList);
    }

    private List<RobotExecute> getQueryInfo(List<String> appIdList, List<String> robotIdList) {
        List<RobotExecute> robotExecuteList = new ArrayList<>();
        for (int i = 0; i < appIdList.size(); i++) {
            String appId = appIdList.get(i);
            String robotId = robotIdList.get(i);

            RobotExecute robotExecute = new RobotExecute();
            robotExecute.setRobotId(robotId);
            robotExecute.setAppId(appId);

            robotExecuteList.add(robotExecute);
        }

        return robotExecuteList;
    }

    private void setVersionNCreatorInfo(
            RobotExecute robotExecute, ExecuteDetailVo resVo, String dataSource, String userId, String tenantId)
            throws Exception {

        if (dataSource.equals("create")) resVo.setSourceName("本地");
        else if (dataSource.equals("market")) resVo.setSourceName("企业市场");
        else if (dataSource.equals("deploy")) resVo.setSourceName("调度中心");

        List<VersionInfo> versionInfoList = new ArrayList<>();

        switch (dataSource) {
            case "create": // 自己创建的应用

                // 版本信息
                List<RobotVersion> robotVersionList =
                        robotVersionDao.getAllVersion(robotExecute.getRobotId(), userId, tenantId);
                for (RobotVersion robotVersion : robotVersionList) {
                    VersionInfo versionInfo = new VersionInfo();

                    versionInfo.setVersionNum(robotVersion.getVersion());
                    versionInfo.setCreateTime(robotVersion.getCreateTime());
                    versionInfo.setOnline(robotVersion.getOnline());

                    versionInfoList.add(versionInfo);
                }

                // 创建者信息
                AppResponse<String> realNameResp = rpaAuthFeign.getNameById(userId);
                if (realNameResp == null || realNameResp.getData() == null) {
                    throw new ServiceException("用户名获取失败");
                }
                String creatorName = realNameResp.getData();

                resVo.setCreateTime(robotExecute.getCreateTime());
                resVo.setCreatorName(creatorName);
                break;

            case "market": // 市场获取的应用
                String appId = robotExecute.getAppId();
                String marketId = robotExecute.getMarketId();
                Integer version = robotExecute.getAppVersion(); // 获取时的AppVersion

                List<AppMarketVersion> appVersionList = appVersionDao.getAllAppVersionRegardlessDel(appId, marketId);
                AppMarketResource appResource = appResourceDao.getAppResourceRegardlessDel(appId, marketId);

                for (AppMarketVersion appVersionTmp : appVersionList) {
                    VersionInfo versionInfo = new VersionInfo();

                    Integer appVersionNumTmp = appVersionTmp.getAppVersion();
                    Integer online = 0;
                    online = appVersionNumTmp.equals(version) ? 1 : 0;

                    versionInfo.setVersionNum(appVersionNumTmp);
                    versionInfo.setCreateTime(appVersionTmp.getCreateTime());
                    versionInfo.setOnline(online);

                    versionInfoList.add(versionInfo);
                }
                // 创建者信息
                AppResponse<String> realNameResp1 = rpaAuthFeign.getNameById(appResource.getCreatorId());
                if (realNameResp1 == null || realNameResp1.getData() == null) {
                    throw new ServiceException("用户名获取失败");
                }
                String creatorName1 = realNameResp1.getData();

                resVo.setCreateTime(appResource.getCreateTime());
                resVo.setCreatorName(creatorName1);
                break;

            case "deploy":
                String oriRobotId = robotExecute.getAppId();
                // 版本信息
                List<RobotVersion> deployRobotVersionList = robotVersionDao.getDeployAllVersion(oriRobotId, tenantId);
                for (RobotVersion robotVersion : deployRobotVersionList) {
                    VersionInfo versionInfo = new VersionInfo();
                    versionInfo.setVersionNum(robotVersion.getVersion());
                    versionInfo.setCreateTime(robotVersion.getCreateTime());
                    versionInfo.setOnline(robotVersion.getOnline());
                    versionInfoList.add(versionInfo);
                }
                // 创建者信息
                AppResponse<String> realNameRes = rpaAuthFeign.getNameById(userId);
                if (realNameRes == null || realNameRes.getData() == null) {
                    throw new ServiceException("用户名获取失败");
                }
                String creatorName2 = realNameRes.getData();
                resVo.setCreateTime(robotExecute.getCreateTime());
                resVo.setCreatorName(creatorName2);
                break;
            default:
                throw new Exception();
        }

        resVo.setVersionInfoList(versionInfoList);
    }

    private void setBasicInfo(RobotExecute robotExecute, RobotVersion robotVersion, ExecuteDetailVo resVo) {
        String robotName = robotExecute.getName();
        Integer versionNum = robotVersion.getVersion();
        String useDescription = robotVersion.getUseDescription();
        String introduction = robotVersion.getIntroduction();

        String fileId = robotVersion.getAppendixId();
        String videoId = robotVersion.getVideoId();
        String fileName = robotExecuteDao.getFileName(fileId);
        String videoName = robotExecuteDao.getFileName(videoId);

        resVo.setRobotName(robotName);
        resVo.setVersionNum(versionNum);
        resVo.setUseDescription(useDescription);
        resVo.setIntroduction(introduction);
        resVo.setFileName(fileName);
        resVo.setFilePath(filePathPrefix + fileId);
        resVo.setVideoName(videoName);
        resVo.setVideoPath(StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));
    }

    private void taskRobotDeleteAfter(List<String> taskIdList) throws Exception {
        List<TaskRobotCountDto> taskRobotCountDtoList = scheduleTaskRobotDao.taskRobotCount(taskIdList);

        Set<String> taskIdNotInList = new HashSet<>();

        for (String taskId : taskIdList) {
            List<TaskRobotCountDto> collect = taskRobotCountDtoList.stream()
                    .filter(taskRobotCountDto -> taskRobotCountDto.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            if (collect == null || collect.size() == 0) {
                taskIdNotInList.add(taskId);
            }
        }

        // 删除不存在于taskRobot对应schedule task
        Integer i = 0;
        if (!CollectionUtils.isEmpty(taskIdNotInList)) i = triggerTaskDao.deleteTasks(taskIdNotInList);

        if (!i.equals(taskIdNotInList.size())) throw new Exception();
    }

    private DelExecuteRobotVo getDeleteRobotVo(
            RobotExecute robotExecute, List<ScheduleTaskRobot> taskRobotList, String robotId) {
        DelExecuteRobotVo resVo = new DelExecuteRobotVo();
        resVo.setRobotId(robotId);

        // 1 : 执行器中出现
        if (robotExecute != null && (CollectionUtils.isEmpty(taskRobotList))) resVo.setSituation(1);

        // 3 : 执行器 被计划任务引用
        else {
            resVo.setSituation(3);
            setDelExecuteRobotVo(resVo, taskRobotList, robotId);
        }

        return resVo;
    }

    private void setDelExecuteRobotVo(DelExecuteRobotVo resVo, List<ScheduleTaskRobot> taskRobotList, String robotId) {
        List<TaskReferInfo> taskReferInfoList = new ArrayList<>();

        // 获取所有引用该执行器的taskId
        List<String> taskIdList =
                taskRobotList.stream().map(ScheduleTaskRobot::getTaskId).collect(Collectors.toList());

        // 查询数据
        List<ScheduleTaskRobot> taskRobots = scheduleTaskRobotDao.getScheduleRobotByTaskIds(taskIdList);

        // 处理数据
        for (String taskId : taskIdList) {
            TaskReferInfo taskReferInfo = new TaskReferInfo();

            // 筛选出当前taskId的taskRobot
            List<ScheduleTaskRobot> taskRobotsTmp = taskRobots.stream()
                    .filter(taskRobot -> taskRobot.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            // 通过sort字段排序  正序
            taskRobotsTmp.sort((o1, o2) -> o1.getSort().compareTo(o2.getSort()));

            List<String> robotNames = new ArrayList<>();
            List<Integer> highIndex = new ArrayList<>();
            for (int i = 0; i < taskRobotsTmp.size(); i++) {
                ScheduleTaskRobot taskRobot = taskRobotsTmp.get(i);
                String robotNameTmp = taskRobot.getRobotName();
                String robotIdTmp = taskRobot.getRobotId();
                if (robotIdTmp.equals(robotId)) {
                    highIndex.add(i);
                }
                robotNames.add(robotNameTmp);
            }

            taskReferInfo.setTaskId(taskId);
            taskReferInfo.setTaskName(taskRobotsTmp.get(0).getTaskName());
            taskReferInfo.setRobotNames(robotNames);
            taskReferInfo.setHighIndex(highIndex);

            taskReferInfoList.add(taskReferInfo);
        }

        resVo.setTaskReferInfoList(taskReferInfoList);
    }

    @Override
    public AppResponse<List<RobotExecuteByNameNDeptVo>> getRobotExecuteList(RobotExecuteByNameNDeptDto queryDto)
            throws NoLoginException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (tenantId == null) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        queryDto.setTenantId(tenantId);
        List<RobotExecuteByNameNDeptVo> resVoList = robotExecuteDao.getRobotExecuteByNameNDept(queryDto);
        if (CollectionUtils.isEmpty(resVoList)) return AppResponse.success(Collections.EMPTY_LIST);
        return AppResponse.success(resVoList);
    }
}
