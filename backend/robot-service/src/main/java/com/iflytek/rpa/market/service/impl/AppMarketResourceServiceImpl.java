package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.*;

import cn.hutool.core.bean.BeanUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Sets;
import com.iflytek.rpa.base.dao.*;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.market.dao.*;
import com.iflytek.rpa.market.entity.*;
import com.iflytek.rpa.market.entity.dto.*;
import com.iflytek.rpa.market.entity.vo.AppDetailVersionInfo;
import com.iflytek.rpa.market.entity.vo.AppDetailVo;
import com.iflytek.rpa.market.entity.vo.AppInfoVo;
import com.iflytek.rpa.market.entity.vo.AppUpdateCheckVo;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.market.service.AppMarketResourceService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.PrePage;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 团队市场-资源映射表(AppMarketResource)表服务实现类
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
@Service("appMarketResourceService")
@RequiredArgsConstructor
public class AppMarketResourceServiceImpl extends ServiceImpl<AppMarketResourceDao, AppMarketResource>
        implements AppMarketResourceService {
    @Resource
    private AppMarketResourceDao appMarketResourceDao;

    @Autowired
    private AppApplicationDao appApplicationDao;

    @Autowired
    private AppMarketVersionDao appMarketVersionDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RobotDesignDao robotDesignDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private CProcessDao processDao;

    @Autowired
    private CGroupDao groupDao;

    @Autowired
    private CElementDao elementDao;

    @Autowired
    private CGlobalVarDao globalVarDao;

    @Autowired
    private CRequireDao requireDao;

    @Autowired
    private CParamService paramService;

    @Autowired
    private CParamDao paramDao;

    @Autowired
    private CModuleDao cModuleDao;

    @Autowired
    private AppApplicationTenantDao appApplicationTenantDao;

    @Autowired
    private ComponentRobotUseDao componentUseDao;

    @Autowired
    private AppApplicationService appApplicationService;

    @Value("${casdoor.database.name:casdoor}")
    private String databaseName;

    private String filePathPrefix = "/api/resource/file/download?fileId=";

    private final StringRedisTemplate stringRedisTemplate;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> shareRobot(ShareRobotDto marketResourceDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 如果开启了上架审核功能
        if (isAuditFunctionEnabled(tenantId)) {
            return handleShareRobotWithAudit(marketResourceDto, userId, tenantId);
        }

        // 未开启审核功能，使用现有的分享逻辑
        return executeShareRobotLogic(marketResourceDto, userId, tenantId);
    }

    /**
     * 处理开启审核功能时的分享逻辑
     */
    private AppResponse<?> handleShareRobotWithAudit(ShareRobotDto marketResourceDto, String userId, String tenantId) {
        String robotId = marketResourceDto.getRobotId();

        // 检查是否已有待审核的申请
        AppApplication existingPendingApplication = appApplicationDao.selectOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, "pending")
                .eq(AppApplication::getDeleted, 0));

        if (existingPendingApplication != null) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "该机器人已有待审核的上架申请，请等待审核结果");
        }

        // 检查是否已有审核通过的申请
        AppApplication approvedApplication = appApplicationDao.selectOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, "approved")
                .eq(AppApplication::getDeleted, 0)
                .orderByDesc(AppApplication::getCreateTime)
                .last("LIMIT 1"));

        // 获取机器人最新版本
        RobotVersion robotVersion =
                robotVersionDao.getLastRobotVersionInfo(marketResourceDto.getRobotId(), userId, tenantId);
        if (null == robotVersion || null == robotVersion.getVersion()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人无版本信息");
        }

        // 检查是否是第一次上架申请
        if (approvedApplication == null) {
            // 第一次上架申请，返回提示信息
            return AppResponse.success("企业管理员开启了上架前审核，审核通过后方可分享至应用市场，请确认是否发起申请。");
        }
        Integer applicationVersion = approvedApplication.getRobotVersion();
        Integer toShareVersion = marketResourceDto.getVersion();
        // 不是第一次上架申请，如果勾选了更新发版自动通过选项
        if (approvedApplication.getDefaultPass() != null && approvedApplication.getDefaultPass() == 1) {
            // 勾选了自动通过选项，直接执行分享逻辑
            return executeShareRobotLogic(marketResourceDto, userId, tenantId);
        } else if (null != applicationVersion && applicationVersion.equals(toShareVersion)) {
            // 未发版的前提下再次分享到其他市场，直接执行分享逻辑，无需再次发起审核
            return executeShareRobotLogic(marketResourceDto, userId, tenantId);
        } else {
            // 未勾选自动通过选项，需要重新发起审核申请
            return AppResponse.success("企业管理员开启了上架前审核，审核通过后方可分享至应用市场，请确认是否发起申请。");
        }
    }

    /**
     * 执行分享（供审核通过后自动调用）
     */
    @Override
    public AppResponse<?> executeShareRobotLogic(ShareRobotDto marketResourceDto, String userId, String tenantId) {
        List<String> marketIdList = marketResourceDto.getMarketIdList();
        if (CollectionUtils.isEmpty(marketIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "缺少市场id");
        }
        marketResourceDto.setCreatorId(userId);
        marketResourceDto.setUpdaterId(userId);
        marketResourceDto.setTenantId(tenantId);
        String robotName = marketResourceDto.getAppName();
        if (null == robotName) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "缺少机器人名称");
        }

        // 获取机器人最新版本
        RobotVersion robotVersion =
                robotVersionDao.getLastRobotVersionInfo(marketResourceDto.getRobotId(), userId, tenantId);
        if (null == robotVersion || null == robotVersion.getVersion()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人无版本信息");
        }
        marketResourceDto.setVersion(robotVersion.getVersion());

        // 获取未离开市场已存在的appId
        List<AppMarketResource> appExestInfoList =
                appMarketResourceDao.getAppInfoByRobotId(marketResourceDto.getRobotId(), userId);
        Map<String, String> exestAppMap = new HashMap<>();
        if (!CollectionUtils.isEmpty(appExestInfoList)) {
            exestAppMap = appExestInfoList.stream()
                    .collect(Collectors.toMap(
                            AppMarketResource::getMarketId, AppMarketResource::getAppId, (existingValue, newValue) -> {
                                // 处理重复键， 使用新值
                                return newValue;
                            }));
        }
        List<AppMarketResource> appInsertInfoList = new ArrayList<>();
        List<AppMarketResource> appUpdateInfoList = new ArrayList<>();
        for (String marketId : marketIdList) {
            AppMarketResource appMarketResource = new AppMarketResource();
            appMarketResource.setMarketId(marketId);
            if (!CollectionUtils.isEmpty(exestAppMap) && exestAppMap.containsKey(marketId)) {
                appMarketResource.setAppId(exestAppMap.get(marketId));
                appUpdateInfoList.add(appMarketResource);
            } else {
                // 产生appId
                appMarketResource.setAppId(idWorker.nextId() + "");
                appInsertInfoList.add(appMarketResource);
            }
        }
        if (!CollectionUtils.isEmpty(appInsertInfoList)) {
            // 第一次分享到市场，插入
            marketResourceDto.setAppInsertInfoList(appInsertInfoList);
            appMarketResourceDao.addAppResource(marketResourceDto);
            appMarketVersionDao.addAppVersionBatch(marketResourceDto);
        }
        if (!CollectionUtils.isEmpty(appUpdateInfoList)) {
            // 分享过的市场，更新
            marketResourceDto.setAppUpdateInfoList(appUpdateInfoList);
            appMarketResourceDao.updateAppResource(marketResourceDto);
            // 1、已上架，再次上架
            // 只有更新，不会出现插入的情况；对于分享过的市场，手动点击分享时一定是已上架状态，没有版本的新增；版本新增，发版时已经同步到市场了
            appMarketVersionDao.updateAppVersionBatch(marketResourceDto);
        }
        robotDesignDao.updateTransformStatus(userId, marketResourceDto.getRobotId(), null, SHARED);
        return AppResponse.success(true);
    }

    /**
     * 将市场信息转换为JSON字符串
     */
    private String convertMarketInfoToJson(List<String> marketIdList, Integer editFlag, String category) {
        try {
            MarketInfoDto marketInfoDto = new MarketInfoDto();
            marketInfoDto.setMarketIdList(marketIdList);
            marketInfoDto.setEditFlag(editFlag);
            marketInfoDto.setCategory(category);
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.writeValueAsString(marketInfoDto);
        } catch (JsonProcessingException e) {
            log.error("转换市场信息为JSON失败", e);
            return null;
        }
    }

    /**
     * 从JSON字符串解析市场信息
     */
    private MarketInfoDto parseMarketInfoFromJson(String marketInfoJson) {
        if (StringUtils.isBlank(marketInfoJson)) {
            return null;
        }
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.readValue(marketInfoJson, MarketInfoDto.class);
        } catch (JsonProcessingException e) {
            log.error("解析市场信息JSON失败", e);
            return null;
        }
    }

    /**
     * 检查是否开启了上架审核功能
     */
    public boolean isAuditFunctionEnabled(String tenantId) {
        // 这里需要查询审核功能开关状态
        AppApplicationTenant currentConfig = appApplicationTenantDao.getByTenantId(tenantId);
        if (currentConfig == null) {
            return false; // 默认关闭，避免影响现有功能
        }
        return currentConfig.getAuditEnable() == 1;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> obtainRobot(MarketResourceDto marketResourceDto) throws NoLoginException {
        List<String> obtainDirectory = marketResourceDto.getObtainDirection();
        String robotName = marketResourceDto.getAppName();
        Integer appVersion = marketResourceDto.getVersion();
        String marketId = marketResourceDto.getMarketId();

        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        marketResourceDto.setCreatorId(userId);
        marketResourceDto.setUpdaterId(userId);
        marketResourceDto.setTenantId(tenantId);

        String newRobotId = idWorker.nextId() + "";
        // 判断该版本机器人是否存在
        RobotVersion robotVersion = robotVersionDao.getVersionInfo(marketResourceDto);
        if (null == robotVersion) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "该版本机器人不存在");
        }
        // 获取到设计器
        if (obtainDirectory.contains("design")) {
            // 插入机器人表，
            RobotDesign robotDesign = new RobotDesign();
            robotDesign.setName(robotName);
            robotDesign.setCreatorId(userId);
            robotDesign.setUpdaterId(userId);
            robotDesign.setTenantId(tenantId);
            // 重名校验
            Long count = robotDesignDao.countRobotByName(robotDesign);
            if (null != count && count > 0) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "设计器存在同名机器人，请修改名称");
            }
            robotDesign.setRobotId(newRobotId);
            robotDesign.setAppId(marketResourceDto.getAppId());
            robotDesign.setAppVersion(appVersion);
            robotDesign.setMarketId(marketId);
            robotDesign.setResourceStatus(OBTAINED);
            robotDesign.setDataSource(MARKET);
            // 查询源码权限
            AppMarketVersion appMarketVersion = appMarketVersionDao.getLatestAppVersionInfo(marketResourceDto);
            if (null == appMarketVersion) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "应用版本不存在");
            }
            // 获取者如果是作者，有编辑权限
            String authorId = robotVersion.getCreatorId();
            Integer editFlag = appMarketVersion.getEditFlag();
            if (null == editFlag || editFlag == 1 || userId.equals(authorId)) {
                robotDesign.setTransformStatus(EDITING);
            } else {
                robotDesign.setTransformStatus(LOCKED);
            }
            //            robotDesign.setEditEnable(editFlag);
            robotDesignDao.obtainRobotToDesign(robotDesign);
            // 复制流程等数据
            createDateForInit(robotDesign, robotVersion);

            increaseDownloadNum(marketResourceDto);
        }
        if (obtainDirectory.contains("execute")) {
            // 获取到执行器

            // 检查是自获取
            Integer selfObtained = checkSelfObtain(marketResourceDto);
            if (selfObtained > 0) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT, "本地已存在该机器人");
            }

            // 是否重复获取
            Integer countObtained = robotExecuteDao.countObtainedExecute(marketResourceDto);
            if (countObtained > 0) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT, "执行器中该机器人当前版本已存在");
            }
            RobotExecute robotExecute = new RobotExecute();
            BeanUtil.copyProperties(marketResourceDto, robotExecute);
            robotExecute.setName(robotName);
            robotExecute.setUpdateTime(new Date());
            robotExecute.setAppVersion(appVersion);
            robotExecute.setResourceStatus(OBTAINED);
            robotExecute.setDataSource(MARKET);
            // 查询该应用是否获取过，
            Integer obtainCount = robotExecuteDao.getObtainCount(marketResourceDto);
            if (obtainCount > 0) {
                // 更新
                robotExecuteDao.updateObtainedRobot(robotExecute);
            } else {
                // 插入
                robotExecute.setRobotId(newRobotId);
                robotExecuteDao.insertObtainedRobot(robotExecute);

                // 组件的引用也需要插入一下
                addCompUseList(newRobotId, appVersion, robotVersion, tenantId, userId);
            }
            increaseDownloadNum(marketResourceDto);
        }

        return AppResponse.success(true);
    }

    private Integer checkSelfObtain(MarketResourceDto marketResourceDto) {
        MarketDto marketDto = new MarketDto();
        BeanUtils.copyProperties(marketResourceDto, marketDto);
        AppMarketResource appResource = appMarketResourceDao.getAppInfoByAppId(marketDto);
        String robotId = appResource.getRobotId();
        String creatorId = marketResourceDto.getCreatorId();
        String tenantId = marketResourceDto.getTenantId();
        if (!StringUtils.isEmpty(robotId) && !StringUtils.isEmpty(creatorId) && !StringUtils.isEmpty(tenantId)) {
            RobotExecute robotExecute = robotExecuteDao.getRobotExecute(robotId, creatorId, tenantId);
            if (null != robotExecute) {
                return 1;
            }
        }
        return 0;
    }

    public void addCompUseList(
            String newRobotId,
            Integer newRobotVersion,
            RobotVersion authorRobotVersion,
            String tenantId,
            String userId) {
        String authorRobotId = authorRobotVersion.getRobotId();
        Integer authorVersion = authorRobotVersion.getVersion();
        List<ComponentRobotUse> compUseListAuth =
                componentUseDao.getByRobotIdAndVersion(authorRobotId, authorVersion, tenantId);

        List<ComponentRobotUse> newCompUseList = new ArrayList<>();

        for (ComponentRobotUse compRobotUse : compUseListAuth) {
            ComponentRobotUse newCompUse = new ComponentRobotUse();

            BeanUtils.copyProperties(compRobotUse, newCompUse);
            newCompUse.setRobotId(newRobotId);
            newCompUse.setRobotVersion(newRobotVersion);
            newCompUse.setCreatorId(userId);
            newCompUse.setUpdaterId(userId);
            newCompUse.setTenantId(tenantId);
            newCompUse.setCreateTime(new Date());
            newCompUse.setUpdateTime(new Date());

            newCompUseList.add(newCompUse);
        }
        if (!newCompUseList.isEmpty()) {
            componentUseDao.insertBatch(newCompUseList);
        }
    }

    private void increaseDownloadNum(MarketResourceDto marketResourceDto) {
        AppMarketResource appResource =
                appMarketResourceDao.getAppResource(marketResourceDto.getAppId(), marketResourceDto.getMarketId());
        appResource.setDownloadNum(appResource.getDownloadNum() + 1);
        int i = appMarketResourceDao.updateById(appResource);
    }

    /**
     * 初始化获取到的机器人的数据
     *
     * @param obtainedRobotDesign
     * @param authorRobotVersion
     */
    public void createDateForInit(RobotDesign obtainedRobotDesign, RobotVersion authorRobotVersion) {
        // 流程
        processDao.createProcessForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // 组
        groupDao.createGroupForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // 元素
        elementDao.createElementForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // 全局变量
        globalVarDao.createGlobalVarForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // python依赖
        requireDao.createRequireForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // python模块代码
        createModuleForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
        // 配置参数
        createParamForCurrentVersion(obtainedRobotDesign, authorRobotVersion);
        // 组件引用
        addCompUseList(
                obtainedRobotDesign.getRobotId(),
                0,
                authorRobotVersion,
                obtainedRobotDesign.getTenantId(),
                obtainedRobotDesign.getCreatorId());
    }

    public void createModuleForObtainedVersion(RobotDesign obtainedRobotDesign, RobotVersion authorRobotVersion) {
        // 不需要 robotVersion 直接赋值 0
        authorRobotVersion.setVersion(0);
        cModuleDao.createModuleForObtainedVersion(obtainedRobotDesign, authorRobotVersion);
    }

    public void createParamForCurrentVersion(RobotDesign obtainedRobotDesign, RobotVersion authorRobotVersion) {
        // 查询0版本机器人所有参数
        List<CParam> cParamList =
                paramDao.getAllParams(null, authorRobotVersion.getRobotId(), authorRobotVersion.getVersion());
        for (CParam cParam : cParamList) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(obtainedRobotDesign.getRobotId());
            // 更新版本号
            cParam.setRobotVersion(0);
            cParam.setCreatorId(obtainedRobotDesign.getCreatorId());
            cParam.setCreateTime(new Date());
            cParam.setUpdaterId(obtainedRobotDesign.getUpdaterId());
            cParam.setUpdateTime(new Date());
        }
        if (!cParamList.isEmpty()) {
            paramDao.createParamForCurrentVersion(cParamList);
        }
    }

    @Override
    public AppResponse<?> deployRobot(MarketDto marketDto) {
        List<String> userIdList = marketDto.getUserIdList();
        if (CollectionUtils.isEmpty(userIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少用户id");
        }
        String appId = marketDto.getAppId();
        String marketId = marketDto.getMarketId();
        if (StringUtils.isBlank(marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "市场参数缺失");
        }
        if (StringUtils.isBlank(appId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = TenantUtils.getTenantId();
        // 判断获取者是否在本团队内
        Set<String> marketUserSet = appMarketUserDao.getMarketUserListForDeploy(marketId, userIdList);

        for (String userId : userIdList) {
            if (null == userId) {
                continue;
            }
            if (!marketUserSet.contains(userId)) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "某些用户不在该团队内，请先邀请");
            }
        }
        // 查询部署版本：最新版本
        //        RobotVersion robotVersion = robotVersionDao.getLatestRobotVersion(appId);
        //        if(null == robotVersion){
        //            return AppResponse.error(ErrorCodeEnum.E_PARAM,"应用市场机器人不存在");
        //        }
        //        Integer appVersion = robotVersion.getVersion();

        // 获取市场中的最大版本
        MarketResourceDto marketResourceDto = new MarketResourceDto();
        marketResourceDto.setAppId(appId);
        marketResourceDto.setMarketId(marketId);
        AppMarketVersion maxVersionInMarket = appMarketVersionDao.getLatestAppVersionInfo(marketResourceDto);
        if (null == maxVersionInMarket || null == maxVersionInMarket.getAppVersion()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "获取不到市场中应用的版本");
        }
        Integer appVersion = maxVersionInMarket.getAppVersion();
        List<RobotExecute> robotExecuteList = new ArrayList<>();
        for (String userId : userIdList) {
            RobotExecute robotExecute = new RobotExecute();
            robotExecute.setRobotId(idWorker.nextId() + "");
            robotExecute.setName(marketDto.getAppName());
            robotExecute.setCreatorId(userId);
            robotExecute.setUpdaterId(userId);
            robotExecute.setTenantId(tenantId);
            robotExecute.setAppId(appId);
            robotExecute.setAppVersion(appVersion);
            robotExecute.setMarketId(marketId);
            robotExecute.setResourceStatus(OBTAINED);
            robotExecute.setDataSource(MARKET);
            robotExecuteList.add(robotExecute);
        }
        robotExecuteDao.addRobotByDeploy(robotExecuteList);

        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> updateRobotByPush(MarketDto marketDto) {
        List<String> userIdList = marketDto.getUserIdList();
        userIdList.removeIf(Objects::isNull);
        marketDto.setUserIdList(userIdList);
        String appId = marketDto.getAppId();
        Integer appVersion = marketDto.getAppVersion();
        if (CollectionUtils.isEmpty(userIdList) || StringUtils.isBlank(appId) || appVersion == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        // 检查推送版本是否存在
        MarketResourceDto marketResourceDto = new MarketResourceDto();
        marketResourceDto.setAppId(appId);
        marketResourceDto.setMarketId(marketDto.getMarketId());
        marketResourceDto.setTenantId(TenantUtils.getTenantId());
        marketResourceDto.setVersion(appVersion);
        RobotVersion robotVersion = robotVersionDao.getVersionInfo(marketResourceDto);
        if (null == robotVersion) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "该版本机器人不存在");
        }
        // 查询是否有用户没有获取过应用
        Set<String> obtainedUserList = robotExecuteDao.getUserListByAppId(appId);
        for (String userId : userIdList) {
            if (!obtainedUserList.contains(userId)) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "某用户没有获取过应用");
            }
        }
        // 查询推送版本的应用名字
        String appName = appMarketResourceDao.getAppNameByAppId(appId);
        marketDto.setAppName(appName);
        robotExecuteDao.updateRobotByPush(marketDto);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> getDeployedUserList(MarketDto marketDto) throws NoLoginException {
        String appId = marketDto.getAppId();
        String marketId = marketDto.getMarketId();
        if (StringUtils.isBlank(appId) || StringUtils.isBlank(marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        marketDto.setCreatorId(userId);
        marketDto.setTenantId(tenantId);
        // 查询原始robotid
        AppMarketResource appMarketResource = appMarketResourceDao.getAppInfoByAppId(marketDto);
        if (null == appMarketResource) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "获取不到应用信息");
        }
        String robotId = appMarketResource.getRobotId();
        if (StringUtils.isBlank(robotId)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "获取不到原始机器人信息");
        }
        // 查询创建者信息
        RobotExecute robotExecute = robotExecuteDao.getAuthInfo(appMarketResource);
        if (null == robotExecute) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "获取不到创建者信息");
        }
        String authorName = UserUtils.getRealNameById(appMarketResource.getCreatorId());
        if (StringUtils.isBlank(authorName)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "未获取到创建者姓名");
        }
        robotExecute.setName(authorName);
        robotExecute.setIsCreator(true);
        String userName = marketDto.getRealName();
        if (StringUtils.isNotBlank(userName)) {
            // 模糊查询
            marketDto.setCreatorId(userId);
            if (authorName.toLowerCase().contains(userName.toLowerCase())) {
                // 模糊查询，包含创建者
                return getResultWitchHaveAuthor(marketDto, robotExecute);
            }
            // 模糊查询，不包含创建者
            PrePage<RobotExecute> pages = new PrePage<>(0L);
            if (null == marketDto.getPageNo() || null == marketDto.getPageSize()) {
                return AppResponse.success(pages);
            }
            PrePage<RobotExecute> pageConfig = new PrePage<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
            // 查询获取者信息
            pages = robotExecuteDao.getDeployedUserList(pageConfig, marketDto, databaseName);
            return AppResponse.success(pages);
        }
        // 查全部
        return getResultWitchHaveAuthor(marketDto, robotExecute);
    }

    private AppResponse<?> getResultWitchHaveAuthor(MarketDto marketDto, RobotExecute robotExecute) {
        PrePage<RobotExecute> pages = new PrePage<>(1L);
        if (null == marketDto.getPageNo() || null == marketDto.getPageSize()) {
            List<RobotExecute> oneResult = new ArrayList<>();
            oneResult.add(robotExecute);
            pages.setRecords(oneResult);
            pages.setTotal(1);
            return AppResponse.success(pages);
        }
        PrePage<RobotExecute> pageConfig = new PrePage<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
        // 查询获取者信息
        pages = robotExecuteDao.getDeployedUserList(pageConfig, marketDto, databaseName);
        List<RobotExecute> robotExecuteList = pages.getRecords();
        robotExecuteList = new ArrayList<>(robotExecuteList);
        if (CollectionUtils.isEmpty(robotExecuteList)) {
            robotExecuteList.add(robotExecute);
        } else {
            for (RobotExecute execute : robotExecuteList) {
                execute.setCreateTime(execute.getUpdateTime());
            }
            robotExecuteList.add(0, robotExecute);
        }
        pages.setRecords(robotExecuteList);
        pages.setTotal(pages.getTotal() + 1);
        return AppResponse.success(pages);
    }

    @Override
    public AppResponse<?> getVersionListForApp(MarketDto marketDto) throws NoLoginException {
        // 版本、更新日志、发版时间
        String appId = marketDto.getAppId();
        String marketId = marketDto.getMarketId();
        if (StringUtils.isBlank(appId) || StringUtils.isBlank(marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        marketDto.setCreatorId(UserUtils.nowUserId());
        marketDto.setTenantId(TenantUtils.getTenantId());
        // 获取市场中的最大版本
        MarketResourceDto marketResourceDto = new MarketResourceDto();
        marketResourceDto.setAppId(appId);
        marketResourceDto.setMarketId(marketId);
        AppMarketVersion maxVersionInMarket = appMarketVersionDao.getLatestAppVersionInfo(marketResourceDto);
        if (null == maxVersionInMarket || null == maxVersionInMarket.getAppVersion()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "获取不到市场中应用的版本");
        }
        marketDto.setAppVersion(maxVersionInMarket.getAppVersion());
        // 退出市场再发版不更新到市场，所以只查小于等于市场最大版本的记录
        List<RobotVersion> robotVersionList = robotVersionDao.getVersionListForApp(marketDto);
        return AppResponse.success(robotVersionList);
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> deleteApp(String appId, String marketId) throws Exception {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            MarketDto marketDto = new MarketDto();
            marketDto.setTenantId(tenantId);
            marketDto.setAppId(appId);
            marketDto.setMarketId(marketId);

            AppMarketResource appResource = appMarketResourceDao.getAppInfoByAppId(marketDto);

            // app_resource 删除
            Integer i = appMarketResourceDao.deleteApp(appId, marketId, tenantId);
            Integer j = appMarketVersionDao.deleteAppVersion(appId, marketId);

            // 更新robotDesign表和robotExecute表
            RobotDesign robotDesign =
                    robotDesignDao.getRobotRegardlessLogicDel(appResource.getRobotId(), userId, tenantId);
            if (robotDesign != null) {
                String transformStatus = robotDesign.getTransformStatus();
                transformStatus = transformStatus.equals("shared") ? "published" : transformStatus;
                robotDesign.setUpdateTime(new Date());
                robotDesign.setTransformStatus(transformStatus);
                Integer z = robotDesignDao.updateById(robotDesign);
                if (!i.equals(0) && !j.equals(0) && !z.equals(0)) {
                    return AppResponse.success("删除机器人成功");
                } else {
                    throw new Exception();
                }
            } else {
                if (!i.equals(0) && !j.equals(0)) {
                    return AppResponse.success("删除机器人成功");
                } else {
                    throw new Exception();
                }
            }
        }
        return response;
    }

    @Override
    public AppResponse<?> getALlAppList(AllAppListDto allAppListDto) throws NoLoginException {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            Long pageNo = allAppListDto.getPageNo();
            Long pageSize = allAppListDto.getPageSize();
            String appName = allAppListDto.getAppName();
            String marketId = allAppListDto.getMarketId();

            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            IPage<AppMarketResource> page = new Page<>(pageNo, pageSize);
            LambdaQueryWrapper<AppMarketResource> wrapper = new LambdaQueryWrapper<>();

            // 市场筛选
            if (StringUtils.isBlank(marketId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
            }
            wrapper.eq(AppMarketResource::getMarketId, marketId);

            // 根据creatorId筛选
            if (StringUtils.isNotBlank(allAppListDto.getCreatorId())) {
                wrapper.eq(AppMarketResource::getCreatorId, allAppListDto.getCreatorId());
            }

            // 模糊匹配
            if (StringUtils.isNotBlank(appName)) {
                wrapper.like(AppMarketResource::getAppName, appName);
            }

            // 排序方式
            HashSet<String> set = Sets.newHashSet("createTime", "downloadNum", "checkNum");
            String sortKey = allAppListDto.getSortKey();
            sortKey = StringUtils.isBlank(sortKey) ? "createTime" : sortKey; // 默认为createTime 倒序
            if (StringUtils.isNotBlank(sortKey) && !set.contains(sortKey)) {
                AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
            }

            switch (sortKey) {
                case "createTime":
                    wrapper.orderByDesc(AppMarketResource::getCreateTime);
                    break;
                case "downloadNum":
                    wrapper.orderByDesc(AppMarketResource::getDownloadNum);
                    break;
                case "checkNum":
                    wrapper.orderByDesc(AppMarketResource::getCheckNum);
                    break;
                default:
                    AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
            }

            // 初次分页
            IPage<AppMarketResource> rePage = this.page(page, wrapper);

            if (CollectionUtils.isEmpty(rePage.getRecords())) return AppResponse.success(rePage);

            // 得到结果页
            IPage<AppInfoVo> ansPage = getAppListAnsPage(rePage, userId, tenantId, pageNo, pageSize, marketId);

            return AppResponse.success(ansPage);
        }

        return response;
    }

    @Override
    public AppResponse<?> appUpdateCheck(AppUpdateCheckDto queryDto) throws NoLoginException {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            String marketId = queryDto.getMarketId();
            String appIdListStr = queryDto.getAppIdListStr();

            if (StringUtils.isBlank(appIdListStr)) return AppResponse.error(ErrorCodeEnum.E_PARAM);

            // appIdList
            List<String> appIdList = Arrays.stream(appIdListStr.split(",")).collect(Collectors.toList());

            // 获取
            List<RobotExecute> robotExecuteList =
                    robotExecuteDao.getExecuteByAppIdList(userId, tenantId, marketId, appIdList);
            List<RobotDesign> robotDesignList =
                    robotDesignDao.getDesignByAppIdList(userId, tenantId, marketId, appIdList);

            List<AppUpdateCheckVo> appUpdateCheckVos = new ArrayList<>();

            for (String appId : appIdList) {
                AppUpdateCheckVo appUpdateCheckVo = new AppUpdateCheckVo();
                appUpdateCheckVo.setAppId(appId);
                appUpdateCheckVo.setUpdateStatus(0);

                List<RobotExecute> robotExecuteListTmp = robotExecuteList.stream()
                        .filter(robotExecute -> robotExecute.getAppId().equals(appId))
                        .collect(Collectors.toList());

                // 是否提示更新
                // 只有其中一个获取过
                if (!CollectionUtils.isEmpty(robotExecuteListTmp)) {
                    RobotExecute robotExecute = robotExecuteListTmp.get(0);
                    if (robotExecute.getResourceStatus().equals("toUpdate")) appUpdateCheckVo.setUpdateStatus(1);
                    else appUpdateCheckVo.setUpdateStatus(0);
                }

                appUpdateCheckVos.add(appUpdateCheckVo);
            }

            return AppResponse.success(appUpdateCheckVos);
        }

        return response;
    }

    @Override
    public AppResponse<?> appDetail(String appId, String marketId) throws Exception {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            if (StringUtils.isBlank(appId) || StringUtils.isBlank(marketId))
                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);

            AppDetailVo appDetailVo = new AppDetailVo();

            AppMarketResource appResource = appMarketResourceDao.getAppResource(appId, marketId);
            AppMarketVersion latestAppVersion = appMarketVersionDao.getLatestAppVersion(appId, marketId);

            if (appResource == null || latestAppVersion == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY);

            // 查看数目加一
            appResource.setCheckNum(appResource.getCheckNum() + 1);
            appMarketResourceDao.updateById(appResource);

            setAppDetailVo(appDetailVo, appResource, latestAppVersion, userId, tenantId);

            return AppResponse.success(appDetailVo);
        }
        return response;
    }

    private void setAppDetailVo(
            AppDetailVo appDetailVo,
            AppMarketResource appResource,
            AppMarketVersion latestAppVersion,
            String userId,
            String tenantId) {

        String appId = appResource.getAppId();
        String marketId = appResource.getMarketId();

        String robotId = appResource.getRobotId();
        Integer appVersionNum = latestAppVersion.getAppVersion();

        RobotVersion robotVersion = robotVersionDao.getLatestVersionRegardlessDel(robotId);
        List<RobotVersion> robotVersionList = robotVersionDao.getAllVersionWithoutUser(robotId);
        String fileName = robotVersionDao.getFileName(robotVersion.getAppendixId());
        String creatorName = UserUtils.getRealNameById(robotVersion.getCreatorId());
        RobotExecute robotExecute = robotExecuteDao.getExecuteByAppId(userId, tenantId, marketId, appId);
        RobotDesign robotDesign = robotDesignDao.getDesignByAppId(userId, tenantId, marketId, appId);

        appDetailVo.setIconUrl(robotVersion.getIcon());
        appDetailVo.setAppName(appResource.getAppName());
        appDetailVo.setIntroduction(robotVersion.getIntroduction());
        appDetailVo.setVideoPath(
                StringUtils.isBlank(robotVersion.getVideoId()) ? "" : filePathPrefix + robotVersion.getVideoId());

        // 基本信息
        appDetailVo.setDownloadNum(appResource.getDownloadNum());
        appDetailVo.setCheckNum(appResource.getCheckNum());
        appDetailVo.setCreatorName(creatorName);
        appDetailVo.setCategory(latestAppVersion.getCategory());
        appDetailVo.setFileName(StringUtils.isBlank(fileName) ? "" : fileName);
        appDetailVo.setFilePath(
                StringUtils.isBlank(robotVersion.getAppendixId()) ? "" : filePathPrefix + robotVersion.getAppendixId());
        appDetailVo.setUseDescription(robotVersion.getUseDescription());

        // 版本信息设置
        List<AppDetailVersionInfo> appDetailVersionInfoList = new ArrayList<>();

        for (int i = 0; i < robotVersionList.size(); i++) {
            RobotVersion rVersion = robotVersionList.get(i);
            Integer online = Integer.MIN_VALUE;

            // online 设置
            if (userId.equals(appResource.getCreatorId())) {
                // 如果发布者就是当前的userId
                online = i == 0 ? 1 : 0;
            } else {
                // 如果发布者不是当前的userId
                Integer obtainedLatestVersionNum = getObtainedLatestVersionNum(robotExecute, robotDesign);
                if (obtainedLatestVersionNum.equals(rVersion.getVersion())) online = 1;
            }

            AppDetailVersionInfo appDetailVersionInfo = new AppDetailVersionInfo();

            appDetailVersionInfo.setUpdateLog(rVersion.getUpdateLog());
            appDetailVersionInfo.setVersionNum(rVersion.getVersion());
            appDetailVersionInfo.setCreateTime(rVersion.getCreateTime());
            appDetailVersionInfo.setOnline(online);
            appDetailVersionInfoList.add(appDetailVersionInfo);
        }

        appDetailVo.setVersionInfoList(appDetailVersionInfoList);
    }

    private Integer getObtainedLatestVersionNum(RobotExecute robotExecute, RobotDesign robotDesign) {
        Integer obtainedLatestVersionNum = Integer.MIN_VALUE;

        Integer robotExecuteAppVersionNum = robotExecute == null ? Integer.MIN_VALUE : robotExecute.getAppVersion();
        Integer robotDesignAppVersionNum = robotDesign == null ? Integer.MIN_VALUE : robotDesign.getAppVersion();

        obtainedLatestVersionNum = Math.max(robotExecuteAppVersionNum, robotDesignAppVersionNum);

        return obtainedLatestVersionNum;
    }

    private IPage<AppInfoVo> getAppListAnsPage(
            IPage<AppMarketResource> rePage,
            String userId,
            String tenantId,
            Long pageNo,
            Long pageSize,
            String marketId) {

        IPage<AppInfoVo> ansPage = new Page<>(pageNo, pageSize);
        List<AppInfoVo> ansRecords = new ArrayList<>();

        List<AppMarketResource> appResourceList = rePage.getRecords();
        List<String> appIdList =
                appResourceList.stream().map(AppMarketResource::getAppId).collect(Collectors.toList());

        // 获取所有的appId对应最大的version号和于其对应的robotId
        List<ResVerDto> resVerDtoList = appMarketVersionDao.getResVerJoin(marketId, appIdList);

        // 根据 版本号  和  robotId 查询  上架审核记录 填充相关信息
        appApplicationService.packageApplicationInfo(appResourceList, resVerDtoList, userId);

        // 获取在市场中的角色
        Integer allowOperate = 0; // 初始不允许操作
        String userType = appMarketUserDao.getMarketUserType(marketId, userId, tenantId);
        allowOperate = userType.equals("acquirer") ? 0 : 1;

        // 获取robotExecuteList
        List<RobotExecute> robotExecuteList =
                robotExecuteDao.getExecuteByAppIdList(userId, tenantId, marketId, appIdList);
        List<RobotDesign> robotDesignList = robotDesignDao.getDesignByAppIdList(userId, tenantId, marketId, appIdList);

        for (AppMarketResource record : appResourceList) {
            String appId = record.getAppId();
            AppInfoVo appInfoVo = new AppInfoVo();

            List<ResVerDto> resVerDtos = resVerDtoList.stream()
                    .filter(resVerDto -> resVerDto.getAppId().equals(appId))
                    .collect(Collectors.toList());

            String intro = "";
            String iconUrl = "";
            if (!CollectionUtils.isEmpty(resVerDtos)) {
                ResVerDto resVerDto = resVerDtos.get(0);
                intro = resVerDto.getIntroduction();
                iconUrl = resVerDto.getIconUrl();
            }

            // 设置获取和更新状态
            setObtainUpdateStatus(appId, appInfoVo, robotExecuteList, robotDesignList);
            appInfoVo.setAppName(record.getAppName());
            appInfoVo.setCheckNum(record.getCheckNum());
            appInfoVo.setDownloadNum(record.getDownloadNum());
            appInfoVo.setAppIntro(intro);
            appInfoVo.setAllowOperate(allowOperate);
            appInfoVo.setAppId(appId);
            appInfoVo.setMarketId(marketId);
            appInfoVo.setIconUrl(iconUrl);

            appInfoVo.setSecurityLevel(record.getSecurity_level());
            appInfoVo.setExpiryDate(record.getExpiry_date());
            appInfoVo.setExpiryDateStr(record.getExpiry_date_str());

            ansRecords.add(appInfoVo);
        }

        ansPage.setRecords(ansRecords);
        ansPage.setSize(rePage.getSize());
        ansPage.setTotal(rePage.getTotal());

        return ansPage;
    }

    private void setObtainUpdateStatus(
            String appId, AppInfoVo appInfoVo, List<RobotExecute> robotExecuteList, List<RobotDesign> robotDesignList) {

        // 过滤
        List<RobotDesign> robotDesignListTmp = robotDesignList.stream()
                .filter(robotDesign -> robotDesign.getAppId().equals(appId))
                .collect(Collectors.toList());

        List<RobotExecute> robotExecuteListTmp = robotExecuteList.stream()
                .filter(robotExecute -> robotExecute.getAppId().equals(appId))
                .collect(Collectors.toList());

        if (CollectionUtils.isEmpty(robotExecuteListTmp) && CollectionUtils.isEmpty(robotDesignListTmp)) {
            // 都没有获取过
            appInfoVo.setObtainStatus(0); // 获取
            appInfoVo.setUpdateStatus(0); // 不提示更新
            return;
        } else { // 说明有获取记录
            appInfoVo.setObtainStatus(1); // 重新获取状态
        }

        if (CollectionUtils.isEmpty(robotExecuteListTmp)) appInfoVo.setUpdateStatus(0);
        else {
            RobotExecute robotExecute = robotExecuteListTmp.get(0);
            if (robotExecute.getResourceStatus().equals("toUpdate")
                    && StringUtils.isNotBlank(robotExecute.getResourceStatus())) appInfoVo.setUpdateStatus(1);
            else appInfoVo.setUpdateStatus(0);
        }
    }
}
