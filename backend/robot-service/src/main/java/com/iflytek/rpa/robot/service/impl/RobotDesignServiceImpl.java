package com.iflytek.rpa.robot.service.impl;

import static com.iflytek.rpa.market.constants.AuditConstant.AUDIT_ENABLE_STATUS_OFF;
import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.*;
import com.iflytek.rpa.base.entity.*;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.component.dao.ComponentRobotBlockDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotBlock;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.example.constants.ExampleConstants;
import com.iflytek.rpa.market.entity.vo.AcceptResultVo;
import com.iflytek.rpa.market.entity.vo.LatestVersionRobotVo;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.DeleteDesignDto;
import com.iflytek.rpa.robot.entity.dto.DesignListDto;
import com.iflytek.rpa.robot.entity.dto.ShareDesignDto;
import com.iflytek.rpa.robot.entity.dto.TaskRobotCountDto;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.RobotDesignService;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.triggerTask.dao.TriggerTaskDao;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.response.QuotaCodeEnum;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.web.client.RestTemplate;

/**
 * 云端机器人表(Robot)表服务实现类
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Slf4j
@Service("robotDesignService")
public class RobotDesignServiceImpl extends ServiceImpl<RobotDesignDao, RobotDesign> implements RobotDesignService {
    @Resource
    private RobotDesignDao robotDesignDao;

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Resource
    private RobotVersionDao robotVersionDao;

    @Autowired
    private CGroupDao groupDao;

    @Resource
    private CElementDao elementDao;

    @Resource
    private CGlobalVarDao globalVarDao;

    @Resource
    private CProcessDao processDao;

    @Resource
    private CRequireDao requireDao;

    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private CProcessDao cProcessDao;

    @Autowired
    private TriggerTaskDao triggerTaskDao;

    @Autowired
    private CParamDao cParamDao;

    @Autowired
    private CModuleDao cModuleDao;

    @Autowired
    private CSmartComponentDao cSmartComponentDao;

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private ComponentRobotBlockDao componentRobotBlockDao;

    @Resource
    private RobotExecuteRecordDao robotExecuteRecordDao;

    @Resource
    private AppApplicationService appApplicationService;

    private final String filePathPrefix = "/api/resource/file/download?fileId=";

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Autowired
    private QuotaCheckService quotaCheckService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse createRobot(RobotDesign robot) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        robot.setCreatorId(userId);
        robot.setUpdaterId(userId);
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        robot.setTenantId(tenantId);
        String robotName = robot.getName();
        robotName = robotName.trim();
        if (StringUtils.isBlank(robotName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人名称不能为空");
        }
        robot.setName(robotName);
        Long countRobot = robotDesignDao.countRobotByName(robot);
        if (countRobot > 0) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "存在同名机器人，请重新命名");
        }

        // 校验设计器配额
        if (!quotaCheckService.checkDesignerQuota()) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_OVER_LIMIT);
            return AppResponse.success(resultVo);
        }

        String robotId = idWorker.nextId() + "";
        robot.setRobotId(robotId);
        robot.setDataSource("create");
        robot.setEditEnable(1);
        robot.setTransformStatus(EDITING);
        robotDesignDao.createRobot(robot);

        // 清除设计器数量缓存（通过Redis直接清除）
        String cacheKey = "quota:count:designer:" + tenantId + ":" + userId;
        com.iflytek.rpa.utils.RedisUtils.del(cacheKey);

        // 新建默认流程,机器人版本是0
        CProcess cProcess = new CProcess();
        cProcess.setRobotId(robotId);
        cProcess.setProcessId(idWorker.nextId() + "");
        cProcess.setProcessName("主流程");
        cProcess.setCreatorId(userId);
        cProcess.setUpdaterId(userId);
        cProcess.setRobotVersion(0);
        cProcessDao.createProcess(cProcess);
        CProcess cProcess1 = new CProcess();
        cProcess1.setRobotId(robotId);
        cProcess1.setProcessId(cProcess.getProcessId());
        return AppResponse.success(cProcess1);
    }

    @Override
    public AppResponse<?> createRobotName() throws NoLoginException {
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
        String robotNameBase = "应用";
        List<String> getRobotNameList = robotDesignDao.getRobotNameList(tenantId, userId, robotNameBase);
        int robotNameIndex = 1;
        List<Integer> robotNameIndexList = new ArrayList<>();
        for (String robotName : getRobotNameList) {
            String[] robotNameSplit = robotName.split(robotNameBase);
            if (robotNameSplit.length == 2 && robotNameSplit[1].matches("^[1-9]\\d*$")) {
                int robotNameNum = Integer.parseInt(robotNameSplit[1]);
                robotNameIndexList.add(robotNameNum);
            }
        }
        Collections.sort(robotNameIndexList);
        for (int i = 0; i < robotNameIndexList.size(); i++) {
            if (robotNameIndexList.get(i) != i + 1) {
                robotNameIndex = i + 1;
                break;
            } else {
                robotNameIndex += 1;
            }
        }
        return AppResponse.success(robotNameBase + robotNameIndex);
    }

    @Override
    public AppResponse<?> designList(DesignListDto queryDto) throws NoLoginException {

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
        String dataSource = queryDto.getDataSource() == null ? "create" : queryDto.getDataSource();

        IPage<RobotDesign> page = new Page<>(pageNo, pageSize);
        LambdaQueryWrapper<RobotDesign> wrapper = new LambdaQueryWrapper<>();

        // userID tenantId 筛选
        wrapper.eq(RobotDesign::getCreatorId, userId);
        wrapper.eq(RobotDesign::getTenantId, tenantId);
        wrapper.eq(RobotDesign::getDeleted, 0);

        // dataSource 筛选
        wrapper.eq(RobotDesign::getDataSource, dataSource);

        // 名字模糊匹配
        if (StringUtils.isNotBlank(name)) {
            wrapper.like(RobotDesign::getName, name);
        }

        // 更新时间排序
        if (sortType.equals("asc")) wrapper.orderByAsc(RobotDesign::getUpdateTime);
        else wrapper.orderByDesc(RobotDesign::getUpdateTime);

        IPage<RobotDesign> rePage = this.page(page, wrapper);

        if (CollectionUtils.isEmpty(rePage.getRecords())) return AppResponse.success(rePage);

        IPage<DesignListVo> ansPage = new Page<>(pageNo, pageSize);
        List<DesignListVo> ansRecords = new ArrayList<>();

        ArrayList<String> robotIdList = new ArrayList<>();

        for (RobotDesign record : rePage.getRecords()) {

            DesignListVo designListVo = new DesignListVo();
            designListVo.setRobotName(record.getName());
            designListVo.setUpdateTime(record.getUpdateTime());
            designListVo.setRobotId(record.getRobotId());
            designListVo.setPublishStatus(record.getTransformStatus());
            designListVo.setEditEnable(record.getTransformStatus().equals("locked") ? 0 : 1);

            ansRecords.add(designListVo);
        }

        setAnsRecords(rePage, ansRecords);
        // 设置上架申请状态
        packageApplicationStatus(ansRecords);

        ansPage.setSize(rePage.getSize());
        ansPage.setTotal(rePage.getTotal());
        ansPage.setRecords(ansRecords);

        return AppResponse.success(ansPage);
    }

    private void packageApplicationStatus(List<DesignListVo> ansRecords) throws NoLoginException {
        AppResponse<String> auditStatus = appApplicationService.getAuditStatus();
        if (auditStatus.ok()) {
            if (auditStatus.getData().equals(AUDIT_ENABLE_STATUS_OFF)) {
                ansRecords.forEach(record -> {
                    record.setApplicationStatus(null);
                });
                return;
            }
            // 开启了上架审核，查询上架状态
            List<LatestVersionRobotVo> robotVoList = ansRecords.stream()
                    .map(record -> {
                        LatestVersionRobotVo vo = new LatestVersionRobotVo();
                        vo.setRobotId(record.getRobotId());
                        vo.setLatestVersion(record.getLatestVersion());
                        return vo;
                    })
                    .collect(Collectors.toList());

            // 调用方法获取上架申请状态
            List<LatestVersionRobotVo> resultList = appApplicationService.getRobotListApplicationStatus(robotVoList);

            Map<String, String> robotStatusMap = resultList.stream()
                    .collect(Collectors.toMap(
                            vo -> vo.getRobotId() + "_" + vo.getLatestVersion(),
                            LatestVersionRobotVo::getApplicationStatus,
                            (existing, replacement) -> existing));
            ansRecords.forEach(record -> {
                String key = record.getRobotId() + "_" + record.getLatestVersion();
                String status = robotStatusMap.get(key);
                record.setApplicationStatus(status != null ? status : "none");
            });
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> rename(String newName, String robotId) throws NoLoginException {

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

        if (StringUtils.isBlank(newName) || StringUtils.isBlank(robotId)) return AppResponse.error("更新失败，新名字或机器人Id为空");

        // 去掉首尾的空格
        newName = trimSpaces(newName);
        String robotName = robotDesignDao.getRobotName(robotId, userId, tenantId);

        if (StringUtils.isBlank(newName)) return AppResponse.error("新名字不能为空");

        Integer i = robotDesignDao.checkNameDup(userId, tenantId, newName, robotId);
        if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");

        boolean b = false;
        // 如果不开放源码，就不改为editing
        RobotDesign robotDesign = robotDesignDao.getRobot(robotId, userId, tenantId);
        if (robotDesign.getTransformStatus().equals("locked") || newName.equals(robotName)) {
            b = robotDesignDao.updateRobotNameWithoutSetEditing(newName, robotId, userId, tenantId);
        } else {
            b = robotDesignDao.updateRobotName(newName, robotId, userId, tenantId);
        }

        if (b) return AppResponse.success("更新成功");
        else return AppResponse.error("更新失败");
    }

    @Override
    public AppResponse<?> designNameDup(String newName, String robotId) throws NoLoginException {

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

        if (StringUtils.isNotBlank(newName)) {

            //                String oriRobotName = robotDesignDao.getRobotName(robotId, userId, tenantId);
            //                if (newName.equals(oriRobotName)) return AppResponse.error("不能和原名相同");
            trimSpaces(newName); // 去除首尾空格
            if (StringUtils.isBlank(newName)) return AppResponse.error("新名字不能为空");

            Integer i = robotDesignDao.checkNameDup(userId, tenantId, newName, robotId);
            if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");
            else return AppResponse.success("重命名校验通过");
        }

        return AppResponse.error("校验失败，新名字为空");
    }

    @Override
    public AppResponse<?> myRobotDetail(String robotId) throws NoLoginException {

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

        RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
        RobotVersion enableVersion = robotVersionDao.getEnableVersion(robotId, userId, tenantId);

        if (robot.getDataSource().equals("market")) return AppResponse.error("设计器来源错误，请检查数据");

        if (robot == null) return AppResponse.error("机器人不存在");

        MyRobotDetailVo resVo = getMyRobotDetailRes(robot, enableVersion);

        return AppResponse.success(resVo);
    }

    @Override
    public AppResponse<?> marketRobotDetail(String robotId) throws Exception {

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

        RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
        RobotVersion enableVersion = robotVersionDao.getEnableVersion(robotId, userId, tenantId);

        if (robot.getDataSource().equals("create")) return AppResponse.error("设计器来源错误，请检查数据");

        MarketRobotDetailVo resVo = getMarketRobotDetailRes(robot, enableVersion, userId, tenantId);

        return AppResponse.success(resVo);
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> copyDesignRobot(String robotId, String robotName) throws Exception {

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

        RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
        if (robot == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);

        String newName = robot.getName() + "副本1";
        if (StringUtils.isNotBlank(robotName)) {
            // 重命名校验
            Integer i = robotDesignDao.checkNameDup(userId, tenantId, robotName, robotId);
            if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");

            newName = robotName;
        }

        // 校验设计器配额
        if (!quotaCheckService.checkDesignerQuota()) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_OVER_LIMIT);
            return AppResponse.success(resultVo);
        }

        // 开始复制
        designRobotCopy(robot, userId, robotId, newName);

        return AppResponse.success("创建副本成功");
    }

    @Override
    public AppResponse<?> deleteRobotRes(String robotId) throws Exception {

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

        RobotExecute robotExecute = robotExecuteDao.getRobotExecute(robotId, userId, tenantId);
        // 获取所有引用该机器人的task
        List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotDao.getAllTaskRobot(robotId, userId, tenantId);

        // 获取响应结果
        DelDesignRobotVo resVo = getDeleteRobotVo(robotExecute, taskRobotList, robotId, userId, tenantId);

        return AppResponse.success(resVo);
    }

    @Transactional(rollbackFor = Exception.class)
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

        // 删除相关的执行记录：先查询 id，再根据 id 更新
        List<Integer> recordIdList = robotExecuteRecordDao.getRecordIds(tenantId, robotId, userId);
        Integer n = 0;
        if (recordIdList != null && !recordIdList.isEmpty()) {
            n = robotExecuteRecordDao.deleteRecordByIds(recordIdList);
        }
        switch (situation) {
            case 1: // 只有设计器中存在
                // 先查询 id，再根据 id 更新
                Integer designId = robotDesignDao.getDesignId(robotId, userId, tenantId);
                if (designId != null) {
                    robotDesignDao.deleteDesignById(designId);
                    // 向 openapi 发送删除请求
                    sendDeleteRequestToOpenApi(robotId, userId);
                    return AppResponse.success("删除成功");
                }
            case 2: // 设计器 执行器 和 执行器中都存在
                // 先查询 id，再根据 id 更新
                Integer designId2 = robotDesignDao.getDesignId(robotId, userId, tenantId);
                if (designId2 != null) {
                    robotDesignDao.deleteDesignById(designId2);
                }
                Integer executeId = robotExecuteDao.getExecuteId(robotId, userId, tenantId);
                if (executeId != null) {
                    robotExecuteDao.deleteExecuteById(executeId);
                }
                // 向 openapi 发送删除请求
                sendDeleteRequestToOpenApi(robotId, userId);
                return AppResponse.success("删除成功");
            case 3: // 设计器、 执行期、 计划任务也引用
                if (StringUtils.isBlank(taskIds)) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
                List<String> taskIdList = Arrays.stream(taskIds.split(",")).collect(Collectors.toList());
                // 先查询 id，再根据 id 更新
                Integer z = 0;
                Integer designId3 = robotDesignDao.getDesignId(robotId, userId, tenantId);
                if (designId3 != null) {
                    robotDesignDao.deleteDesignById(designId3);
                }
                Integer executeId3 = robotExecuteDao.getExecuteId(robotId, userId, tenantId);
                if (executeId3 != null) {
                    robotExecuteDao.deleteExecuteById(executeId3);
                }
                List<Integer> taskRobotIdList =
                        scheduleTaskRobotDao.getTaskRobotIds(robotId, userId, tenantId, taskIdList);
                if (taskRobotIdList != null && !taskRobotIdList.isEmpty()) {
                    z = scheduleTaskRobotDao.taskRobotDeleteByIds(taskRobotIdList);
                }
                taskRobotDeleteAfter(taskIdList);
                int expectedTaskRobotCount = (taskRobotIdList != null) ? taskRobotIdList.size() : 0;
                if (z.equals(expectedTaskRobotCount)) {
                    // 向 openapi 发送删除请求
                    sendDeleteRequestToOpenApi(robotId, userId);
                    return AppResponse.success("删除成功");
                } else throw new ServiceException("删除失败");

            default:
                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
        }
    }

    /**
     * 向 openapi 发送删除机器人的请求
     *
     * @param robotId 机器人ID
     * @param userId   用户ID
     */
    private void sendDeleteRequestToOpenApi(String robotId, String userId) {
        try {
            log.info("删除机器人时请求openapi，robotId: {}", robotId);

            // 构建请求体
            JSONObject requestBody = new JSONObject();
            requestBody.put("project_id", robotId);
            requestBody.put("status", 0);

            String requestBodyStr = requestBody.toJSONString();
            log.info("请求openapi参数: {}", requestBodyStr);

            // 创建 RestTemplate 实例
            RestTemplate restTemplate = new RestTemplate();

            // 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.add("user_id", userId);

            // 创建请求实体
            HttpEntity<String> requestEntity = new HttpEntity<>(requestBodyStr, headers);

            // openapi URL
            String openApiUrl = ExampleConstants.WORKFLOWS_UPSERT_URL;

            // 发起 POST 请求
            ResponseEntity<String> response =
                    restTemplate.exchange(openApiUrl, HttpMethod.POST, requestEntity, String.class);

            log.info(
                    "OpenAPI 请求成功，URL: {}, 响应状态: {}, 响应体: {}",
                    openApiUrl,
                    response.getStatusCode(),
                    response.getBody());
        } catch (Exception e) {
            log.error("OpenAPI 请求失败，robotId: {}, 错误信息: {}", robotId, e.getMessage(), e);
            // 不抛出异常，避免影响删除操作
        }
    }

    // 后处理，查看以taskIdList为taskId的在taskRobot中还是否存在，如果不存在，则需要在schedule task表中也删除
    public void taskRobotDeleteAfter(List<String> taskIdList) throws Exception {
        List<TaskRobotCountDto> taskRobotCountDtoList = scheduleTaskRobotDao.taskRobotCount(taskIdList);
        // 求 taskRobotCountDtoList 与  taskIdList 的 差集，  taskIdNotInList中存放差集元素
        Set<String> taskIdNotInList = taskIdList.stream()
                .filter(taskId -> taskRobotCountDtoList.stream()
                        .noneMatch(taskRobotCountDto ->
                                taskRobotCountDto.getTaskId().equals(taskId)))
                .collect(Collectors.toSet());
        /*for (String taskId : taskIdList) {
            List<TaskRobotCountDto> collect = taskRobotCountDtoList
                    .stream()
                    .filter(taskRobotCountDto -> taskRobotCountDto.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            if (collect == null || collect.size() == 0){
                taskIdNotInList.add(taskId);
            }
        }*/
        // 删除不存在于taskRobot对应schedule task
        Integer i = 0;
        if (!taskIdNotInList.isEmpty()) {
            i = triggerTaskDao.deleteTasks(taskIdNotInList);
        }

        if (!i.equals(taskIdNotInList.size())) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "删除数据与实际数据不对应");
        }
    }

    private DelDesignRobotVo getDeleteRobotVo(
            RobotExecute robotExecute,
            List<ScheduleTaskRobot> taskRobotList,
            String robotId,
            String userId,
            String tenantId)
            throws Exception {

        DelDesignRobotVo resVo = new DelDesignRobotVo();
        resVo.setRobotId(robotId);

        // 1：设计器
        if (robotExecute == null) resVo.setSituation(1);
        // 2：设计器 执行器
        else if (robotExecute != null && (CollectionUtils.isEmpty(taskRobotList))) resVo.setSituation(2);
        // 3：设计器 执行器 被计划任务引用
        else {
            resVo.setSituation(3);
            setDelDesignRobotVo(resVo, taskRobotList, robotId);
        }

        return resVo;
    }

    // 第三种情况
    public void setDelDesignRobotVo(DelDesignRobotVo resVo, List<ScheduleTaskRobot> taskRobotList, String robotId)
            throws Exception {

        List<TaskReferInfo> taskReferInfoList = new ArrayList<>();

        // 获取所有引用该执行器的taskId
        List<String> taskIdList =
                taskRobotList.stream().map(ScheduleTaskRobot::getTaskId).collect(Collectors.toList());

        // 查询数据
        List<ScheduleTaskRobot> taskRobots = scheduleTaskRobotDao.getScheduleRobotByTaskIds(taskIdList);
        if (CollectionUtils.isEmpty(taskRobots)) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "机器人引用关系异常");
        }

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

    public void designRobotCopy(RobotDesign robot, String userId, String robotId, String robotName) throws Exception {

        String newRobotId = String.valueOf(idWorker.nextId());

        robot.setId(null);
        robot.setRobotId(newRobotId);
        robot.setName(robotName);
        robot.setCreateTime(new Date());
        robot.setUpdateTime(new Date());
        robot.setTransformStatus("editing");
        robot.setDataSource("create");
        robotDesignDao.insert(robot);

        // 复制基础工程内容，复制的版本 0 的内容
        copyEditingBase(robotId, newRobotId, userId);
    }

    @Override
    public void copyEditingBase(String oldRobotId, String newRobotId, String userId) throws Exception {
        // 分组
        groupCopy(oldRobotId, newRobotId, userId);
        // 元素
        elementCopy(oldRobotId, newRobotId, userId);
        // 全局变量
        globalValCopy(oldRobotId, newRobotId, userId);
        // 流程
        processCopy(oldRobotId, newRobotId, userId);
        // python依赖
        requireCopy(oldRobotId, newRobotId, userId);
        // python模块
        moduleCopy(oldRobotId, newRobotId, userId);
        // 配置参数
        paramCopy(oldRobotId, newRobotId, userId);
        // 组件引用数据
        componentUseCopy(oldRobotId, newRobotId, userId);
        // 组件屏蔽数据
        componentBlockCopy(oldRobotId, newRobotId, userId);
        // 智能组件拷贝
        smartComponentCopy(oldRobotId, newRobotId, userId);
    }

    public void smartComponentCopy(String oldRobotId, String newRobotId, String userId) {
        // 先查询旧机器人的smartComponent列表
        List<CSmartComponent> oldSmartComponentList =
                cSmartComponentDao.getAllSmartComponentList(oldRobotId, 0, userId);

        if (CollectionUtils.isEmpty(oldSmartComponentList)) {
            return;
        }

        // 创建旧id到新id的映射
        Map<String, String> oldNewSmartComponentIdMap = new HashMap<>();

        // 复制smartComponent并建立映射关系
        List<CSmartComponent> smartComponentList = new ArrayList<>();
        for (CSmartComponent oldSmartComponent : oldSmartComponentList) {
            CSmartComponent newSmartComponent = new CSmartComponent();
            newSmartComponent.setSmartId(String.valueOf(idWorker.nextId()));
            newSmartComponent.setRobotId(newRobotId);
            newSmartComponent.setContent(oldSmartComponent.getContent());
            newSmartComponent.setSmartType(oldSmartComponent.getSmartType());
            newSmartComponent.setRobotVersion(oldSmartComponent.getRobotVersion());
            newSmartComponent.setCreatorId(oldSmartComponent.getCreatorId());
            newSmartComponent.setUpdaterId(oldSmartComponent.getUpdaterId());

            oldNewSmartComponentIdMap.put(oldSmartComponent.getSmartId(), newSmartComponent.getSmartId());
            smartComponentList.add(newSmartComponent);
        }

        // 获取旧机器人的process内容
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, userId);

        // 如果没有process，直接插入smartComponent并返回
        if (CollectionUtils.isEmpty(oldProcessList)) {
            cSmartComponentDao.insertBatch(smartComponentList);
            return;
        }

        // 获取新机器人的process列表（需要更新smartId引用）
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, userId);
        // 如果没有process，直接插入smartComponent并返回
        if (CollectionUtils.isEmpty(newProcessList)) {
            cSmartComponentDao.insertBatch(smartComponentList);
            return;
        }

        // 更新所有process content中的smart ID引用（主流程和子流程）
        for (int i = 0; i < newProcessList.size() && i < oldProcessList.size(); i++) {
            String currentContent = newProcessList.get(i).getProcessContent();
            // 如果content为空或null，跳过处理
            if (currentContent == null || currentContent.trim().isEmpty()) {
                continue;
            }

            // 使用映射关系更新smartComponent引用（currentContent已经是更新过process ID的版本）
            String newContent = replaceSmartIdsWithMap(currentContent, oldNewSmartComponentIdMap);
            newProcessList.get(i).setProcessContent(newContent);
            processDao.updateById(newProcessList.get(i));
        }

        cSmartComponentDao.insertBatch(smartComponentList);
    }

    public void moduleCopy(String oldRobotId, String newRobotId, String userId) {
        // 先查询旧机器人的module列表
        List<CModule> oldModuleList = cModuleDao.getAllModuleListOrderByIdAsc(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(oldModuleList)) {
            return;
        }

        // 创建旧moduleId到新moduleId的映射
        Map<String, String> oldNewModuleIdMap = new HashMap<>();

        // 复制module并建立映射关系
        List<CModule> moduleList = new ArrayList<>();
        for (CModule oldModule : oldModuleList) {
            CModule newModule = new CModule();
            newModule.setModuleId(String.valueOf(idWorker.nextId()));
            newModule.setRobotId(newRobotId);
            newModule.setModuleContent(oldModule.getModuleContent());
            newModule.setModuleName(oldModule.getModuleName());
            newModule.setRobotVersion(oldModule.getRobotVersion());
            newModule.setDeleted(oldModule.getDeleted());
            newModule.setCreatorId(oldModule.getCreatorId());
            newModule.setUpdaterId(oldModule.getUpdaterId());
            newModule.setCreateTime(new Date());
            newModule.setUpdateTime(new Date());

            oldNewModuleIdMap.put(oldModule.getModuleId(), newModule.getModuleId());
            moduleList.add(newModule);
        }

        // 获取旧机器人的process内容
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(oldProcessList)) {
            // 如果没有process，直接插入module并返回
            cModuleDao.insertBatch(moduleList);
            return;
        }

        // 获取新机器人的process列表（需要更新module ID引用）
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, userId);
        if (CollectionUtils.isEmpty(newProcessList)) {
            // 如果没有process，直接插入module并返回
            cModuleDao.insertBatch(moduleList);
            return;
        }

        // 更新所有process content中的module ID引用（主流程和子流程）
        for (int i = 0; i < newProcessList.size() && i < oldProcessList.size(); i++) {
            String currentContent = newProcessList.get(i).getProcessContent();
            // 如果content为空或null，跳过处理
            if (currentContent == null || currentContent.trim().isEmpty()) {
                continue;
            }

            // 使用映射关系更新module引用（currentContent已经是更新过process ID的版本）
            String newContent = replaceModuleIdsWithMap(currentContent, oldNewModuleIdMap);
            newProcessList.get(i).setProcessContent(newContent);
            processDao.updateById(newProcessList.get(i));
        }

        cModuleDao.insertBatch(moduleList);
    }

    public void paramCopy(String oldRobotId, String newRobotId, String userId) {
        List<CParam> params = cParamDao.getParams(oldRobotId, userId);
        copyProcessParam(oldRobotId, newRobotId, userId, params);
        copyModuleParam(oldRobotId, newRobotId, userId, params);
    }

    private void copyProcessParam(String oldRobotId, String newRobotId, String userId, List<CParam> params) {
        List<CParam> processParams = params.stream()
                .filter(param -> StringUtils.isNotEmpty(param.getProcessId()))
                .collect(Collectors.toList());
        processParams.removeIf(Objects::isNull);
        if (CollectionUtils.isEmpty(processParams)) return;
        // 原机器人的流程id  和  副本机器人的流程id 的映射Map:（k,v） 为 （oldProcessId,newProcessId）
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, userId);
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, userId);
        Map<String, String> oldNewProcessIdMap = getOldNewProcessIdMap(newProcessList, oldProcessList);
        for (CParam cParam : processParams) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(newRobotId);
            // 保证子流程的processId和配置参数对应
            cParam.setProcessId(oldNewProcessIdMap.get(cParam.getProcessId()));
            cParam.setRobotVersion(0); // 新版本为0
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(userId);
            cParam.setUpdaterId(userId);
            cParam.setDeleted(0);
        }
        if (!processParams.isEmpty()) {
            cParamDao.insertParamBatch(processParams);
        }
    }

    private void copyModuleParam(String oldRobotId, String newRobotId, String userId, List<CParam> params) {
        List<CParam> moduleParams = params.stream()
                .filter(param -> StringUtils.isNotEmpty(param.getModuleId()))
                .collect(Collectors.toList());
        moduleParams.removeIf(Objects::isNull);
        if (CollectionUtils.isEmpty(moduleParams)) return;
        // 原机器人的流程id  和  副本机器人的流程id 的映射Map:（k,v） 为 （oldProcessId,newProcessId）
        List<CModule> oldModuleList = cModuleDao.getAllModuleListOrderByIdAsc(oldRobotId, 0, userId);
        List<CModule> newModuleList = cModuleDao.getAllModuleListOrderByIdAsc(newRobotId, 0, userId);
        Map<String, String> OldNewModuleIdMap = getOldNewModuleIdMap(newModuleList, oldModuleList);
        for (CParam cParam : moduleParams) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(newRobotId);
            // 保证子流程的moduleId和配置参数对应
            cParam.setModuleId(OldNewModuleIdMap.get(cParam.getModuleId()));
            cParam.setRobotVersion(0); // 新版本为0
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(userId);
            cParam.setUpdaterId(userId);
            cParam.setDeleted(0);
        }
        if (!moduleParams.isEmpty()) {
            cParamDao.insertParamBatch(moduleParams);
        }
    }

    private Map<String, String> getOldNewModuleIdMap(List<CModule> newModuleList, List<CModule> oldModuleList) {
        if (newModuleList.size() != oldModuleList.size()) throw new ServiceException(ErrorCodeEnum.E_SQL.getCode());

        Map<String, String> OldNewModuleIdMap = new HashMap<>();
        for (int i = 0; i < oldModuleList.size(); i++) {
            OldNewModuleIdMap.put(
                    oldModuleList.get(i).getModuleId(), newModuleList.get(i).getModuleId());
        }

        return OldNewModuleIdMap;
    }

    private Map<String, String> getOldNewProcessIdMap(List<CProcess> newProcessList, List<CProcess> oldProcessList) {
        if (newProcessList.size() != oldProcessList.size()) throw new ServiceException(ErrorCodeEnum.E_SQL.getCode());

        Map<String, String> oldNewProcessIdMap = new HashMap<>();
        for (int i = 0; i < oldProcessList.size(); i++) {
            oldNewProcessIdMap.put(
                    oldProcessList.get(i).getProcessId(), newProcessList.get(i).getProcessId());
        }

        return oldNewProcessIdMap;
    }

    public void groupCopy(String oldRobotId, String newRobotId, String userId) {
        groupDao.copyGroupBatch(oldRobotId, newRobotId, userId);
    }

    public void elementCopy(String oldRobotId, String newRobotId, String userId) {

        List<CElement> elementList = elementDao.getElement(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(elementList)) return;

        for (CElement element : elementList) {
            //            String nextId = String.valueOf(idWorker.nextId());

            element.setId(null);
            //            element.setElementId(nextId);
            element.setRobotId(newRobotId);
            element.setCreateTime(new Date());
            element.setUpdateTime(new Date());
        }

        // 最后批量插入
        elementDao.insertEleBatch(elementList);
    }

    public void globalValCopy(String oldRobotId, String newRobotId, String userId) {

        List<CGlobalVar> globalVarList = globalVarDao.getGlobalVar(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(globalVarList)) return;

        for (CGlobalVar globalVar : globalVarList) {
            String nextId = String.valueOf(idWorker.nextId());

            globalVar.setId(null);
            globalVar.setGlobalId(nextId);
            globalVar.setRobotId(newRobotId);
            globalVar.setCreateTime(new Date());
            globalVar.setUpdateTime(new Date());
        }

        globalVarDao.insertGloBatch(globalVarList);
    }

    public void processCopy(String oldRobotId, String newRobotId, String userId) throws Exception {
        // 先查询旧机器人的process列表
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(oldProcessList)) throw new Exception();

        // 创建旧processId到新processId的映射
        Map<String, String> oldNewProcessIdMap = new HashMap<>();

        // 复制process并建立映射关系
        List<CProcess> processList = new ArrayList<>();
        for (CProcess oldProcess : oldProcessList) {
            CProcess newProcess = new CProcess();
            newProcess.setProcessId(String.valueOf(idWorker.nextId()));
            newProcess.setRobotId(newRobotId);
            newProcess.setProcessContent(oldProcess.getProcessContent());
            newProcess.setProcessName(oldProcess.getProcessName());
            newProcess.setRobotVersion(oldProcess.getRobotVersion());
            newProcess.setDeleted(oldProcess.getDeleted());
            newProcess.setCreatorId(oldProcess.getCreatorId());
            newProcess.setUpdaterId(oldProcess.getUpdaterId());
            newProcess.setCreateTime(new Date());
            newProcess.setUpdateTime(new Date());

            // 创建旧processId到新processId的映射
            oldNewProcessIdMap.put(oldProcess.getProcessId(), newProcess.getProcessId());
            processList.add(newProcess);
        }

        // 主流程中子流程的引用重新替换成新的子流程 processId
        subProcessWrite(processList, oldProcessList, oldNewProcessIdMap);

        processDao.insertProcessBatch(processList);
    }

    /**
     * 主流程中子流程的引用重新替换成新的子流程 processId
     *
     * @param processList
     * @param oldProcessList
     * @param oldNewProcessIdMap
     */
    public void subProcessWrite(
            List<CProcess> processList, List<CProcess> oldProcessList, Map<String, String> oldNewProcessIdMap) {
        // 说明不存在子流程
        if (processList.size() == 1) return;
        if (processList.size() != oldProcessList.size())
            throw new ServiceException("the size of new process is not equal to the size of old process");

        // 遍历每个流程，使用正则安全地替换process引用
        for (int i = 0; i < oldProcessList.size(); i++) {
            String oldContent = oldProcessList.get(i).getProcessContent();
            // 如果content为空，直接使用
            if (oldContent == null || oldContent.trim().isEmpty()) {
                processList.get(i).setProcessContent(oldContent);
                continue;
            }

            // 使用正则表达式安全地替换process引用
            String newContent = replaceProcessIdsWithMap(oldContent, oldNewProcessIdMap);
            processList.get(i).setProcessContent(newContent);
        }
    }

    private String replaceModuleIds(String processContent, List<String> moduleIdList) {
        if (processContent == null || moduleIdList == null) {
            throw new IllegalArgumentException("processContent and moduleIdList cannot be null.");
        }

        String patternString = Pattern.quote("\"key\":\"content\",\"value\":\"") + "(\\d+)";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();
        int matchCount = 0;

        // 查找所有匹配项
        while (matcher.find()) {
            matchCount++;
            if (matchCount > moduleIdList.size()) {
                // 如果匹配到的位置数量超过了提供的ID数量，说明不匹配
                throw new IllegalArgumentException("Number of matched positions (" + matchCount
                        + ") exceeds the size of moduleIdList (" + moduleIdList.size() + ").");
            }
            // 获取当前匹配到的ID
            String replacementId = moduleIdList.get(moduleIdList.size() - matchCount); // moduleIdList 是0-indexed

            // 构建替换文本：模板部分 + 替换的ID
            String replacementText = "\"key\":\"content\",\"value\":\"" + replacementId;
            matcher.appendReplacement(resultBuffer, replacementText);
        }

        // 检查匹配到的位置数量是否与moduleIdList的size相同
        if (matchCount != moduleIdList.size()) log.info("主流程对子模块可能没有引用全");

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    /**
     * 使用ID映射替换module引用，支持同一个module被多次引用
     */
    private String replaceModuleIdsWithMap(String processContent, Map<String, String> oldNewModuleIdMap) {
        if (processContent == null || oldNewModuleIdMap == null || oldNewModuleIdMap.isEmpty()) {
            if (processContent == null) {
                throw new IllegalArgumentException("processContent cannot be null.");
            }
            return processContent;
        }

        String patternString = Pattern.quote("\"key\":\"content\",\"value\":\"") + "(\\d+)";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();

        // 查找所有匹配项
        while (matcher.find()) {
            String oldModuleId = matcher.group(1);
            String newModuleId = oldNewModuleIdMap.get(oldModuleId);

            // 如果找到映射关系，使用新的ID；否则保持原ID
            if (newModuleId != null) {
                String replacementText = "\"key\":\"content\",\"value\":\"" + newModuleId;
                matcher.appendReplacement(resultBuffer, replacementText);
            } else {
                // 如果没有找到映射关系，保持原样
                matcher.appendReplacement(resultBuffer, matcher.group(0));
            }
        }

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    /**
     * 使用ID映射替换smartComponent引用，支持同一个smartComponent被多次引用
     */
    private String replaceSmartIdsWithMap(String processContent, Map<String, String> oldNewSmartComponentIdMap) {
        if (processContent == null || oldNewSmartComponentIdMap == null || oldNewSmartComponentIdMap.isEmpty()) {
            if (processContent == null) {
                throw new IllegalArgumentException("processContent cannot be null.");
            }
            return processContent;
        }

        String patternString = "\"key\":\"Smart\\.run_code\\.(\\d+)\"";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();

        // 查找所有匹配项
        while (matcher.find()) {
            String oldSmartId = matcher.group(1);
            String newSmartId = oldNewSmartComponentIdMap.get(oldSmartId);

            // 如果找到映射关系，使用新的ID；否则保持原ID
            if (newSmartId != null) {
                String replacementText = String.format("\"key\":\"Smart.run_code.%s\"", newSmartId);
                matcher.appendReplacement(resultBuffer, replacementText);
            } else {
                // 如果没有找到映射关系，保持原样
                matcher.appendReplacement(resultBuffer, matcher.group(0));
            }
        }

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    private String replaceProcessIds(String processContent, List<String> processIdList) {
        if (processContent == null || processIdList == null) {
            throw new IllegalArgumentException("processContent and processIdList cannot be null.");
        }

        String patternString = Pattern.quote("\"key\":\"process\",\"value\":\"") + "(\\d+)";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();
        int matchCount = 0;

        // 查找所有匹配项
        while (matcher.find()) {
            matchCount++;
            if (matchCount > processIdList.size()) {
                // 如果匹配到的位置数量超过了提供的ID数量，说明不匹配
                throw new IllegalArgumentException("Number of matched positions (" + matchCount
                        + ") exceeds the size of processIdList (" + processIdList.size() + ").");
            }
            // 获取当前匹配到的ID
            String replacementId = processIdList.get(matchCount - 1); // processIdList 是0-indexed

            // 构建替换文本：模板部分 + 替换的ID
            String replacementText = "\"key\":\"process\",\"value\":\"" + replacementId;
            matcher.appendReplacement(resultBuffer, replacementText);
        }

        // 检查匹配到的位置数量是否与processIdList的size相同
        if (matchCount != processIdList.size()) log.info("主流程对子流程可能没有引用全");

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    /**
     * 使用ID映射替换process引用，支持同一个process被多次引用
     */
    private String replaceProcessIdsWithMap(String processContent, Map<String, String> oldNewProcessIdMap) {
        if (processContent == null || oldNewProcessIdMap == null || oldNewProcessIdMap.isEmpty()) {
            if (processContent == null) {
                throw new IllegalArgumentException("processContent cannot be null.");
            }
            return processContent;
        }

        String patternString = Pattern.quote("\"key\":\"process\",\"value\":\"") + "(\\d+)";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();

        // 查找所有匹配项
        while (matcher.find()) {
            String oldProcessId = matcher.group(1);
            String newProcessId = oldNewProcessIdMap.get(oldProcessId);

            // 如果找到映射关系，使用新的ID；否则保持原ID
            if (newProcessId != null) {
                String replacementText = "\"key\":\"process\",\"value\":\"" + newProcessId;
                matcher.appendReplacement(resultBuffer, replacementText);
            } else {
                // 如果没有找到映射关系，保持原样
                matcher.appendReplacement(resultBuffer, matcher.group(0));
            }
        }

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    public void requireCopy(String oldRobotId, String newRobotId, String userId) {
        List<CRequire> requireList = requireDao.getRequire(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(requireList)) return;

        for (CRequire require : requireList) {

            require.setId(null);
            require.setRobotId(newRobotId);
            require.setCreateTime(new Date());
            require.setUpdateTime(new Date());
        }

        requireDao.insertReqBatch(requireList);
    }

    private MarketRobotDetailVo getMarketRobotDetailRes(
            RobotDesign robot, RobotVersion enableVersion, String userId, String tenantId) throws Exception {

        String appId = robot.getAppId();
        Integer appVersion = robot.getAppVersion();

        MyRobotDetailVo myRobotDetailRes = getMyRobotDetailRes(robot, enableVersion);

        // 设置useDescription 和 file相关信息
        setAddInfo(myRobotDetailRes, robot);

        String robotId = robotDesignDao.getRobotIdFromAppResourceRegardlessDel(appId);

        List<RobotVersion> allVersion = robotVersionDao.getAllVersionWithoutUserId(robotId, tenantId);
        List<VersionInfo> versionInfoList = new ArrayList<>();

        for (int i = 0; i < allVersion.size(); i++) {
            RobotVersion robotVersion = allVersion.get(i);
            Integer online = 0;

            VersionInfo versionInfo = new VersionInfo();
            versionInfo.setVersionNum(robotVersion.getVersion());
            versionInfo.setCreateTime(robotVersion.getCreateTime());

            // 这是他获取时候的version
            online = appVersion.equals(robotVersion.getVersion()) ? 1 : 0;

            versionInfo.setOnline(online);

            versionInfoList.add(versionInfo);
        }

        MarketRobotDetailVo resVo = new MarketRobotDetailVo();
        resVo.setMyRobotDetailVo(myRobotDetailRes);
        resVo.setSourceName("团队市场");
        resVo.setVersionInfoList(versionInfoList);

        return resVo;
    }

    private void setAddInfo(MyRobotDetailVo myRobotDetailRes, RobotDesign robot) throws Exception {
        String appId = robot.getAppId();
        String sourceRobotId = robotDesignDao.getRobotIdFromAppResourceRegardlessDel(appId);

        RobotVersion latestRobotVersion = robotVersionDao.getLatestVersionRegardlessDel(sourceRobotId);
        if (latestRobotVersion == null) throw new Exception();

        String fileId = latestRobotVersion.getAppendixId();
        String videoId = latestRobotVersion.getVideoId();
        String fileName = robotExecuteDao.getFileName(fileId);
        String videoName = robotExecuteDao.getFileName(videoId);

        myRobotDetailRes.setUseDescription(latestRobotVersion.getUseDescription());
        myRobotDetailRes.setFileName(fileName);
        myRobotDetailRes.setFilePath(filePathPrefix + fileId);
        myRobotDetailRes.setVideoName(videoName);
        myRobotDetailRes.setVideoPath(StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));
    }

    private MyRobotDetailVo getMyRobotDetailRes(RobotDesign robot, RobotVersion enableVersion) {
        MyRobotDetailVo resVo = new MyRobotDetailVo();
        String introduction = "";
        Integer version = 0;
        String fileId = null;
        String videoId = null;
        String fileName = null;
        String videoName = null;
        String useDescription = null;

        if (enableVersion != null) {
            introduction = enableVersion.getIntroduction();
            version = enableVersion.getVersion();
            fileId = enableVersion.getAppendixId();
            videoId = enableVersion.getVideoId();
            fileName = robotExecuteDao.getFileName(fileId);
            videoName = robotExecuteDao.getFileName(videoId);
            useDescription = enableVersion.getUseDescription();
        }

        AppResponse<String> realNameResp = rpaAuthFeign.getNameById(robot.getCreatorId());
        if (realNameResp == null || realNameResp.getData() == null) {
            throw new ServiceException("用户名获取失败");
        }
        String creatorName = realNameResp.getData();

        resVo.setName(robot.getName());
        resVo.setVersion(version);
        resVo.setIntroduction(introduction);
        resVo.setUseDescription(useDescription);
        resVo.setCreatorName(creatorName);
        resVo.setCreateTime(robot.getCreateTime());
        resVo.setFileName(fileName);
        resVo.setFilePath(filePathPrefix + fileId);
        resVo.setVideoName(videoName);
        resVo.setVideoPath(StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));

        return resVo;
    }

    private void setAnsRecords(IPage<RobotDesign> rePage, List<DesignListVo> ansRecords) {

        List<RobotDesign> robotDesignList = rePage.getRecords();

        List<String> robotIdList =
                robotDesignList.stream().map(RobotDesign::getRobotId).collect(Collectors.toList());

        List<RobotVersion> robotVersionList = robotDesignDao.getRobotVersionList(robotIdList);

        for (DesignListVo ansRecord : ansRecords) {
            String robotId = ansRecord.getRobotId();

            // 过滤出当前robotId的robotVersion
            List<RobotVersion> robotVersionsTmp = robotVersionList.stream()
                    .filter(robotVersion -> robotVersion.getRobotId().equals(robotId))
                    .collect(Collectors.toList());

            if (robotVersionsTmp.size() == 0 || robotVersionsTmp == null) {
                // 说明没有发过版本， 团队市场获取的设计器没有版本，和产品确认过了
                ansRecord.setVersion(0);
            } else {

                List<RobotVersion> enableList = robotVersionsTmp.stream()
                        .filter(robotVersion1 -> robotVersion1.getOnline().equals(1))
                        .collect(Collectors.toList());

                if (CollectionUtils.isEmpty(enableList))
                    throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "数据异常，发过版本的机器人无启用版本");

                // 发过版本的，设置启用启用版本
                RobotVersion enableRobotVersion = enableList.get(0);

                // 发过版本的，设置最新版本
                Optional<RobotVersion> optionalRobotVersion =
                        robotVersionsTmp.stream().max(Comparator.comparing(RobotVersion::getVersion));

                ansRecord.setLatestVersion(optionalRobotVersion.get().getVersion());
                ansRecord.setVersion(enableRobotVersion.getVersion());
                ansRecord.setIconUrl(enableRobotVersion.getIcon());
            }
        }
    }

    public String trimSpaces(String input) {
        if (input == null) {
            return null;
        }
        return input.trim();
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> shareRobot(ShareDesignDto queryDto) throws Exception {

        String robotId = queryDto.getRobotId();
        String sharedUserId = queryDto.getSharedUserId();
        String sharedTenantId = queryDto.getSharedTenantId();
        String receivedUserId = queryDto.getReceivedUserId();
        String receivedTenantId = queryDto.getReceivedTenantId();

        // 获取要分享的机器人
        RobotDesign robot = robotDesignDao.getRobot(robotId, sharedUserId, sharedTenantId);
        if (robot == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
        String receivedRobotName = robot.getName() + "分享";
        // 检查接收用户 机器人是否重名
        Integer i = robotDesignDao.checkNameDupWithoutRobotId(receivedUserId, receivedTenantId, receivedRobotName);
        while (i > 1) {
            receivedRobotName += "分享";
            i = robotDesignDao.checkNameDupWithoutRobotId(receivedUserId, receivedTenantId, receivedRobotName);
        }

        String newRobotId = designRobotShare(robot, sharedUserId, receivedUserId, receivedTenantId, receivedRobotName);
        return AppResponse.success(newRobotId);
    }

    /**
     * 设计器分享
     *
     * @param robot             分享的机器人
     * @param receivedUserId    接收机器人的用户id
     * @param receivedTenantId  接收机器人的用户的租户id
     * @param receivedRobotName 机器人名称
     */
    public String designRobotShare(
            RobotDesign robot,
            String sharedUserId,
            String receivedUserId,
            String receivedTenantId,
            String receivedRobotName)
            throws Exception {
        String oldRobotId = robot.getRobotId();
        // 修改 robotDesign 的 信息
        robot.setId(null);
        String newRobotId = String.valueOf(idWorker.nextId());
        robot.setRobotId(newRobotId);
        robot.setName(receivedRobotName);
        // 租户id
        robot.setTenantId(receivedTenantId);
        // 用户id
        robot.setCreatorId(receivedUserId);
        robot.setUpdaterId(receivedUserId);
        robot.setCreateTime(new Date());
        robot.setUpdateTime(new Date());
        robot.setTransformStatus("editing");
        robot.setDataSource("create");
        robotDesignDao.insert(robot);
        // 迁移其他相关的数据
        shareRobotBaseInfo(oldRobotId, newRobotId, sharedUserId, receivedUserId);

        return robot.getRobotId();
    }

    public void shareRobotBaseInfo(String oldRobotId, String newRobotId, String sharedUserId, String receivedUserId)
            throws Exception {
        // 分组
        groupShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 元素
        elementShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 全局变量
        globalValShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 流程
        processShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // python依赖
        requireShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 配置参数
        paramShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
    }

    private void groupShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        groupDao.shareGroupBatch(oldRobotId, sharedUserId, newRobotId, receivedUserId);
    }

    private void elementShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CElement> elementList = elementDao.getElement(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(elementList)) return;
        for (CElement element : elementList) {
            element.setId(null);
            element.setRobotId(newRobotId);
            element.setCreateTime(new Date());
            element.setUpdateTime(new Date());
            element.setCreatorId(receivedUserId);
            element.setUpdaterId(receivedUserId);
        }
        elementDao.insertEleBatch(elementList);
    }

    private void globalValShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CGlobalVar> globalVarList = globalVarDao.getGlobalVar(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(globalVarList)) return;
        for (CGlobalVar globalVar : globalVarList) {
            String nextId = String.valueOf(idWorker.nextId());
            globalVar.setId(null);
            globalVar.setGlobalId(nextId);
            globalVar.setRobotId(newRobotId);
            globalVar.setCreateTime(new Date());
            globalVar.setUpdateTime(new Date());
            globalVar.setCreatorId(receivedUserId);
            globalVar.setUpdaterId(receivedUserId);
        }
        globalVarDao.insertGloBatch(globalVarList);
    }

    private void processShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId)
            throws Exception {
        List<CProcess> processList = processDao.getProcess(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(processList)) throw new Exception();
        for (CProcess process : processList) {
            String nextId = String.valueOf(idWorker.nextId());
            process.setId(null);
            process.setProcessId(nextId);
            process.setRobotId(newRobotId);
            process.setCreateTime(new Date());
            process.setUpdateTime(new Date());
            process.setCreatorId(receivedUserId);
            process.setUpdaterId(receivedUserId);
        }
        processDao.insertProcessBatch(processList);
    }

    private void requireShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CRequire> requireList = requireDao.getRequire(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(requireList)) return;
        for (CRequire require : requireList) {
            require.setId(null);
            require.setRobotId(newRobotId);
            require.setCreateTime(new Date());
            require.setUpdateTime(new Date());
            require.setCreatorId(receivedUserId);
            require.setUpdaterId(receivedUserId);
        }
        requireDao.insertReqBatch(requireList);
    }

    private void paramShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CParam> params = cParamDao.getParams(oldRobotId, sharedUserId);
        // 原机器人的流程id  和  副本机器人的流程id 的映射Map:（k,v） 为 （oldProcessId,newProcessId）
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, sharedUserId);
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, receivedUserId);
        Map<String, String> oldNewProcessIdMap = getOldNewProcessIdMap(newProcessList, oldProcessList);
        for (CParam cParam : params) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(newRobotId);
            // 保证子流程的processId和配置参数对应
            cParam.setProcessId(oldNewProcessIdMap.get(cParam.getProcessId()));
            cParam.setRobotVersion(0); // 新版本为0
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(receivedUserId);
            cParam.setUpdaterId(receivedUserId);
            cParam.setDeleted(0);
        }
        if (!params.isEmpty()) {
            cParamDao.insertParamBatch(params);
        }
    }

    /**
     * 复制组件引用数据
     *
     * @param oldRobotId 原机器人ID
     * @param newRobotId 新机器人ID
     * @param userId     用户ID
     */
    private void componentUseCopy(String oldRobotId, String newRobotId, String userId) {
        // 查询原机器人的组件引用记录（版本0）
        List<ComponentRobotUse> componentRobotUseList =
                componentRobotUseDao.getComponentRobotUse(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(componentRobotUseList)) return;

        // 处理每条记录：id置为null，robotId改为新ID，更新时间
        for (ComponentRobotUse componentRobotUse : componentRobotUseList) {
            componentRobotUse.setId(null);
            componentRobotUse.setRobotId(newRobotId);
            componentRobotUse.setCreateTime(new Date());
            componentRobotUse.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotUseDao.insertBatch(componentRobotUseList);
    }

    /**
     * 复制组件屏蔽数据
     *
     * @param oldRobotId 原机器人ID
     * @param newRobotId 新机器人ID
     * @param userId     用户ID
     */
    private void componentBlockCopy(String oldRobotId, String newRobotId, String userId) {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        // 查询原机器人的组件屏蔽记录（版本0）
        List<ComponentRobotBlock> componentRobotBlockList =
                componentRobotBlockDao.getComponentRobotBlockForCopy(oldRobotId, 0, tenantId);
        if (CollectionUtils.isEmpty(componentRobotBlockList)) return;

        // 处理每条记录：id置为null，robotId改为新ID，更新时间
        for (ComponentRobotBlock componentRobotBlock : componentRobotBlockList) {
            componentRobotBlock.setId(null);
            componentRobotBlock.setRobotId(newRobotId);
            componentRobotBlock.setCreateTime(new Date());
            componentRobotBlock.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotBlockDao.insertBatch(componentRobotBlockList);
    }
}
