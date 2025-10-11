package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.market.constants.AuditConstant.*;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.market.dao.AppApplicationDao;
import com.iflytek.rpa.market.dao.AppApplicationTenantDao;
import com.iflytek.rpa.market.dao.AppMarketResourceDao;
import com.iflytek.rpa.market.dao.AppMarketVersionDao;
import com.iflytek.rpa.market.entity.*;
import com.iflytek.rpa.market.entity.bo.PublishInfoBo;
import com.iflytek.rpa.market.entity.dto.*;
import com.iflytek.rpa.market.entity.vo.*;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.market.service.AppMarketResourceService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.vo.ExecuteListVo;
import com.iflytek.rpa.robot.service.RobotVersionService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.DateUtils;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.casbin.casdoor.entity.User;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-07-02 11:00
 * @copyright Copyright (c) 2025 mjren
 */
@Slf4j
@Service("appApplicationService")
public class AppApplicationServiceImpl extends ServiceImpl<AppApplicationDao, AppApplication>
        implements AppApplicationService {

    @Autowired
    private AppApplicationDao appApplicationDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private AppApplicationTenantDao appApplicationTenantDao;

    @Autowired
    private AppMarketResourceDao appMarketResourceDao;

    @Autowired
    private AppMarketVersionDao appMarketVersionDao;

    @Autowired
    private RobotDesignDao robotDesignDao;

    @Autowired
    private AppMarketResourceService appMarketResourceService;

    @Autowired
    private RobotVersionService robotVersionService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> auditApplication(AuditApplicationDto auditApplicationDto) throws Exception {
        String status = auditApplicationDto.getStatus();
        String auditType = auditApplicationDto.getApplicationType();

        if ("release".equals(auditType)) {
            if (AUDIT_STATUS_APPROVED.equals(status)) {
                // 判断是否缺少信息
                if (StringUtils.isBlank(auditApplicationDto.getSecurityLevel())) {
                    return AppResponse.error("密级标识不能为空");
                }
                if ("yellow".equals(auditApplicationDto.getSecurityLevel())
                        && StringUtils.isBlank(auditApplicationDto.getAllowedDept())) {
                    return AppResponse.error("指定的部门不能为空");
                } else if ("green".equals(auditApplicationDto.getSecurityLevel())
                        && null == auditApplicationDto.getDefaultPass()) {
                    return AppResponse.error("更新发版默认通过的选项不能为空");
                }
            }
        }

        // 更新审核状态
        AppApplication awaitingUpdate = new AppApplication();
        BeanUtils.copyProperties(auditApplicationDto, awaitingUpdate);
        if ("week".equals(auditApplicationDto.getExpireTime())) {
            // 取当前时间加一周
            awaitingUpdate.setExpireTime(DateUtils.getCalDay(new Date(), 7));
        } else if ("month".equals(auditApplicationDto.getExpireTime())) {
            // 取当前时间加一个月
            awaitingUpdate.setExpireTime(DateUtils.getCalDay(new Date(), 30));
        } else if ("quarter".equals(auditApplicationDto.getExpireTime())) {
            // 取当前时间加三个月
            awaitingUpdate.setExpireTime(DateUtils.getCalDay(new Date(), 90));
        }
        // 更新 申请
        appApplicationDao.update(
                awaitingUpdate,
                new LambdaUpdateWrapper<AppApplication>()
                        .eq(AppApplication::getId, auditApplicationDto.getId())
                        .eq(AppApplication::getDeleted, 0));

        // 如果是上架审核且审核通过，自动执行分享逻辑
        if ("release".equals(auditType)) {
            releaseHandle(auditApplicationDto, awaitingUpdate);
        }
        if ("use".equals(auditType)) {
            useHandle(auditApplicationDto, awaitingUpdate);
        }

        return AppResponse.success("审批成功");
    }

    private void useHandle(AuditApplicationDto auditApplicationDto, AppApplication awaitingUpdate) {
        AppApplication application = this.getById(auditApplicationDto.getId());
        if (AUDIT_STATUS_APPROVED.equals(auditApplicationDto.getStatus())) {
            AppApplication releaseApplication = this.getOne(new LambdaQueryWrapper<AppApplication>()
                    .eq(AppApplication::getRobotId, application.getRobotId())
                    .eq(AppApplication::getRobotVersion, application.getRobotVersion())
                    .eq(AppApplication::getApplicationType, "release")
                    .eq(AppApplication::getStatus, "approved")
                    .eq(AppApplication::getDeleted, 0)
                    .last("limit 1"));
            if (releaseApplication != null && StringUtils.isNotBlank(releaseApplication.getMarketInfo())) {
                MarketInfoDto marketInfo = parseMarketInfoFromJson(releaseApplication.getMarketInfo());
                if (marketInfo != null && !marketInfo.getMarketIdList().isEmpty()) {
                    awaitingUpdate.setMarketId(marketInfo.getMarketIdList().get(0));
                }
            }
        }
    }

    private void releaseHandle(AuditApplicationDto auditApplicationDto, AppApplication awaitingUpdate)
            throws Exception {
        // 获取上架申请信息
        AppApplication application = this.getById(auditApplicationDto.getId());
        if (AUDIT_STATUS_APPROVED.equals(auditApplicationDto.getStatus())) {
            if (application != null) {
                if (StringUtils.isBlank(application.getPublishInfo())
                        && StringUtils.isNotBlank(application.getMarketInfo())) {
                    // 分享
                    shareHandle(awaitingUpdate, application);
                }
                if (StringUtils.isBlank(application.getMarketInfo())
                        && StringUtils.isNotBlank(application.getPublishInfo())) {
                    // 发版
                    publishHandle(awaitingUpdate, application);
                }
                // 第一次发版
                if (StringUtils.isNotBlank(application.getMarketInfo())
                        && StringUtils.isNotBlank(application.getPublishInfo())) {
                    publishHandle(awaitingUpdate, application);
                    shareHandle(awaitingUpdate, application);
                }
            }
        }
    }

    private void publishHandle(AppApplication awaitingUpdate, AppApplication application) throws Exception {
        PublishInfoBo publishInfoBo = parsePublishInfoBoFromJson(application.getPublishInfo());
        RobotExecute robotExecute = publishInfoBo.getRobotExecute();
        Integer nextVersion = publishInfoBo.getNextVersion();
        // 完成 应用市场 的 版本 推送
        robotVersionService.updateAppAndRobot(robotExecute, nextVersion);
    }

    private void shareHandle(AppApplication awaitingUpdate, AppApplication application) {
        // 解析市场信息
        MarketInfoDto marketInfo = parseMarketInfoFromJson(application.getMarketInfo());
        if (marketInfo != null && !CollectionUtils.isEmpty(marketInfo.getMarketIdList())) {
            // 构建分享参数
            ShareRobotDto marketResourceDto = new ShareRobotDto();
            marketResourceDto.setRobotId(application.getRobotId());
            marketResourceDto.setMarketIdList(marketInfo.getMarketIdList());
            marketResourceDto.setEditFlag(marketInfo.getEditFlag());
            marketResourceDto.setCategory(marketInfo.getCategory());

            // 获取机器人信息
            RobotDesign robotDesign = robotDesignDao.getRobotRegardlessLogicDel(
                    application.getRobotId(), application.getCreatorId(), application.getTenantId());
            if (robotDesign == null) {
                throw new ServiceException("无法获取机器人信息");
            }
            marketResourceDto.setAppName(robotDesign.getName());
            // 执行分享逻辑
            AppResponse<?> shareResponse = appMarketResourceService.executeShareRobotLogic(
                    marketResourceDto, application.getCreatorId(), application.getTenantId());
            if (!shareResponse.ok()) {
                throw new ServiceException(shareResponse.getMessage());
            }
            if (!marketInfo.getMarketIdList().isEmpty()) {
                awaitingUpdate.setMarketId(marketInfo.getMarketIdList().get(0));
            }
        }
    }

    @Override
    public AppResponse<String> changeAudit(ChangeAuditDto changeAuditDto) throws NoLoginException, IOException {
        // 1. 验证参数
        if (changeAuditDto.getId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "审批单ID不能为空");
        }
        if (StringUtils.isBlank(changeAuditDto.getRobotId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "机器人ID不能为空");
        }
        if (StringUtils.isBlank(changeAuditDto.getSecurityLevel())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "密级标识不能为空");
        }

        // 2. 获取当前审批单信息
        AppApplication currentApp = this.getById(changeAuditDto.getId());
        if (currentApp == null || currentApp.getDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "审批单不存在");
        }

        // 3. 检查是否为"已通过"状态的机器人
        if (!AUDIT_STATUS_APPROVED.equals(currentApp.getStatus())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能变更已通过状态的机器人密级");
        }

        // 4. 检查申请类型是否为release
        if (!"release".equals(currentApp.getApplicationType())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能变更上架申请的机器人密级");
        }

        // 5. 获取当前密级和新密级
        String currentSecurityLevel = currentApp.getSecurityLevel();
        String newSecurityLevel = changeAuditDto.getSecurityLevel();

        // 6. 验证新密级参数
        if ("yellow".equals(newSecurityLevel) && StringUtils.isBlank(changeAuditDto.getAllowedDept())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "黄色密级必须指定允许使用的部门");
        } else if ("green".equals(newSecurityLevel) && changeAuditDto.getDefaultPass() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "绿色密级必须设置更新发版默认通过选项");
        }

        // 7. 判断密级变更方向
        boolean isUpgrade = isSecurityLevelUpgrade(currentSecurityLevel, newSecurityLevel);
        boolean isDowngrade = isSecurityLevelDowngrade(currentSecurityLevel, newSecurityLevel);

        // 8. 处理密级变更
        if (isUpgrade) {
            // 低密级向高密级变更：检查已下载终端的权限
            return handleSecurityLevelUpgrade(currentApp, changeAuditDto);
        } else if (isDowngrade) {
            // 高密级向低密级变更：自动通过符合条件的申请
            return handleSecurityLevelDowngrade(currentApp, changeAuditDto);
        } else {
            // 同级变更：直接更新
            return updateSecurityLevel(currentApp, changeAuditDto);
        }
    }

    /**
     * 判断是否为密级升级
     */
    private boolean isSecurityLevelUpgrade(String currentLevel, String newLevel) {
        // 密级等级：green < yellow < red
        if ("green".equals(currentLevel) && ("yellow".equals(newLevel) || "red".equals(newLevel))) {
            return true;
        }
        return "yellow".equals(currentLevel) && "red".equals(newLevel);
    }

    /**
     * 判断是否为密级降级
     */
    private boolean isSecurityLevelDowngrade(String currentLevel, String newLevel) {
        // 密级等级：green < yellow < red
        if ("red".equals(currentLevel) && ("yellow".equals(newLevel) || "green".equals(newLevel))) {
            return true;
        }
        return "yellow".equals(currentLevel) && "green".equals(newLevel);
    }

    /**
     * 处理密级升级：检查已下载终端的权限
     */
    private AppResponse<String> handleSecurityLevelUpgrade(AppApplication currentApp, ChangeAuditDto changeAuditDto)
            throws NoLoginException {
        //        String robotId = currentApp.getRobotId();
        //        String tenantId = TenantUtils.getTenantId();
        //
        //        // 查询已下载该机器人的终端用户
        //        List<RobotExecute> robotExecutes = robotExecuteDao.selectList(
        //            new LambdaQueryWrapper<RobotExecute>()
        //                .eq(RobotExecute::getRobotId, robotId)
        //                .eq(RobotExecute::getTenantId, tenantId)
        //                .eq(RobotExecute::getDeleted, 0)
        //        );
        //
        //        if (!robotExecutes.isEmpty()) {
        //            // 获取所有下载用户的ID
        //            List<String> userIds = robotExecutes.stream()
        //                .map(RobotExecute::getCreatorId)
        //                .collect(Collectors.toList());
        //
        //            // 查询用户信息
        //            List<UapUser> users = UserUtils.queryUserPageList(userIds);
        //
        //            // 检查用户权限是否满足新密级要求
        //            List<String> insufficientUsers = new ArrayList<>();
        //            for (UapUser user : users) {
        //                if (!checkUserPermissionForSecurityLevel(user, changeAuditDto.getSecurityLevel(),
        // changeAuditDto.getAllowedDept())) {
        //                    insufficientUsers.add(user.getName());
        //                }
        //            }
        //
        //            if (!insufficientUsers.isEmpty()) {
        //                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK,
        //                    "以下用户权限不足，无法使用新密级：" + String.join(", ", insufficientUsers));
        //            }
        //        }

        // 更新密级
        return updateSecurityLevel(currentApp, changeAuditDto);
    }

    /**
     * 处理密级降级：自动通过符合条件的申请
     */
    private AppResponse<String> handleSecurityLevelDowngrade(AppApplication currentApp, ChangeAuditDto changeAuditDto)
            throws NoLoginException, IOException {
        String robotId = currentApp.getRobotId();
        String tenantId = TenantUtils.getTenantId();

        // 查询该机器人的所有使用申请
        List<AppApplication> useApplications = this.list(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getTenantId, tenantId)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getStatus, "pending")
                .eq(AppApplication::getDeleted, 0));

        if (!useApplications.isEmpty()) {
            // 获取申请用户信息
            List<String> userIds =
                    useApplications.stream().map(AppApplication::getCreatorId).collect(Collectors.toList());

            List<User> users = UserUtils.queryUserPageList(userIds);
            Map<String, User> userMap = UserUtils.getUserMap(users);

            // 自动通过符合条件的申请
            for (AppApplication useApp : useApplications) {
                User user = userMap.get(useApp.getCreatorId());
                if (user != null
                        && checkUserPermissionForSecurityLevel(
                                user, changeAuditDto.getSecurityLevel(), changeAuditDto.getAllowedDept())) {
                    useApp.setStatus(AUDIT_STATUS_APPROVED);
                    useApp.setSecurityLevel(changeAuditDto.getSecurityLevel());
                    useApp.setAllowedDept(changeAuditDto.getAllowedDept());
                    useApp.setUpdateTime(new Date());
                    useApp.setUpdaterId(UserUtils.nowUserId());
                    this.updateById(useApp);
                }
            }
        }

        // 更新密级
        return updateSecurityLevel(currentApp, changeAuditDto);
    }

    /**
     * 检查用户权限是否满足密级要求
     */
    private boolean checkUserPermissionForSecurityLevel(User user, String securityLevel, String allowedDept) {
        if ("green".equals(securityLevel)) {
            // 绿色密级：所有用户都可以使用
            return true;
        } else if ("red".equals(securityLevel)) {
            // 红色密级：需要特殊权限，这里可以根据实际需求扩展
            // 暂时返回false，表示需要特殊审批
            return false;
        }
        return false;
    }

    /**
     * 更新密级信息
     */
    private AppResponse<String> updateSecurityLevel(AppApplication currentApp, ChangeAuditDto changeAuditDto)
            throws NoLoginException {
        currentApp.setSecurityLevel(changeAuditDto.getSecurityLevel());
        currentApp.setAllowedDept(changeAuditDto.getAllowedDept());
        currentApp.setDefaultPass(changeAuditDto.getDefaultPass());
        currentApp.setUpdateTime(new Date());
        currentApp.setUpdaterId(UserUtils.nowUserId());

        this.updateById(currentApp);

        return AppResponse.success("密级变更成功");
    }

    @Override
    public AppResponse<IPage<ReleasePageListVo>> getReleasePageList(ReleasePageListDto queryDto) throws Exception {
        String tenantId = TenantUtils.getTenantId();
        queryDto.setTenantId(tenantId);
        IPage<ReleasePageListVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        IPage<ReleasePageListVo> releasePage = appApplicationDao.getReleasePageList(pageConfig, queryDto);
        List<ReleasePageListVo> records = releasePage.getRecords();
        records.removeIf(Objects::isNull);
        packageUserInfo(records);
        return AppResponse.success(releasePage);
    }

    @Override
    public AppResponse<IPage<UsePageListVo>> getUsePageList(UsePageListDto queryDto) throws Exception {
        String tenantId = TenantUtils.getTenantId();
        queryDto.setTenantId(tenantId);
        IPage<UsePageListVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        IPage<UsePageListVo> usePage = appApplicationDao.getUsePageList(pageConfig, queryDto);
        List<UsePageListVo> records = usePage.getRecords();
        records.removeIf(Objects::isNull);
        //        packageUseDept(records);
        return AppResponse.success(usePage);
    }

    private void packageUserInfo(List<ReleasePageListVo> recordList) throws IOException {
        List<String> userIds =
                recordList.stream().map(ReleasePageListVo::getCreatorId).collect(Collectors.toList());
        userIds.removeIf(Objects::isNull);
        if (userIds.isEmpty()) {
            return;
        }
        List<User> uapUsers = UserUtils.queryUserPageList(userIds);
        Map<String, User> userMap = UserUtils.getUserMap(uapUsers);
        recordList.forEach(record -> {
            User uapUser = userMap.get(record.getCreatorId());
            if (uapUser != null) {
                record.setCreatorName(uapUser.name);
                record.setCreatorPhone(uapUser.phone);
            }
        });
    }

    //    private void packageUseDept(List<UsePageListVo> recordList) throws IOException {
    //        List<String> userIds = recordList.stream().map(UsePageListVo::getCreatorId).collect(Collectors.toList());
    //        userIds.removeIf(Objects::isNull);
    //        if (userIds.isEmpty()) {
    //            return;
    //        }
    //        List<User> uapUsers = UserUtils.queryUserPageList(userIds);
    //        Map<String, User> userMap = UserUtils.getUserMap(uapUsers);
    //        recordList.forEach(
    //                record -> {
    //                    User uapUser = userMap.get(record.getCreatorId());
    //                    if (uapUser != null) {
    //                        record.setCreatorName(uapUser.name);
    //                        record.setCreatorPhone(uapUser.phone);
    //                        record.setCreatorDeptId(uapUser.getOrgId());
    //                        record.setCreatorDeptName(uapUser.getOrgName());
    //                    }
    //                }
    //        );
    //    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> releaseDelete(ReleaseDeleteDto releaseDeleteDto) throws NoLoginException {
        String id = releaseDeleteDto.getId();
        AppApplication appApplication = this.getById(id);
        if (appApplication == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "审批单不存在");
        }
        if (appApplication.getDeleted() == 1 || appApplication.getCloudDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "审批单已被删除");
        }
        // String status = appApplication.getStatus();
        // if (!"rejected".equals(status)) {
        //    return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能删除未通过的上架审批");
        // }
        appApplication.setCloudDeleted(1);
        appApplication.setUpdateTime(new Date());
        appApplication.setUpdaterId(UserUtils.nowUserId());
        this.updateById(appApplication);
        return AppResponse.success("删除成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> useDelete(UseDeleteDto useDeleteDto) throws NoLoginException {
        String id = useDeleteDto.getId();
        AppApplication appApplication = this.getById(id);
        if (appApplication == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "审批单不存在");
        }
        if (appApplication.getDeleted() == 1 || appApplication.getCloudDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "审批单已被删除");
        }
        String status = appApplication.getStatus();
        if (!"rejected".equals(status) && !"approved".equals(status)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能删除未通过或已通过状态的使用审批");
        }
        appApplication.setCloudDeleted(1);
        appApplication.setUpdateTime(new Date());
        appApplication.setUpdaterId(UserUtils.nowUserId());
        this.updateById(appApplication);
        return AppResponse.success("删除成功");
    }

    @Override
    public AppResponse<String> enableAudit(String status, String reason) throws NoLoginException {
        // 1. 参数验证
        if (StringUtils.isBlank(status)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "审核开关状态不能为空");
        }

        // 2. 验证状态参数是否有效
        Short auditEnable;
        if (AUDIT_ENABLE_STATUS_ON.equals(status)) {
            auditEnable = AUDIT_ENABLE_ON;
        } else if (AUDIT_ENABLE_STATUS_OFF.equals(status)) {
            auditEnable = AUDIT_ENABLE_OFF;
        } else {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "审核开关状态参数无效，只能是 'on' 或 'off'");
        }

        // 3. 获取当前租户ID和操作人
        String tenantId = TenantUtils.getTenantId();
        String operator = UserUtils.nowUserId();
        if (StringUtils.isBlank(tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
        }

        try {
            // 4. 查询当前审核开关状态
            AppApplicationTenant currentConfig = appApplicationTenantDao.getByTenantId(tenantId);

            // 5. 如果是关闭功能，需要特殊处理
            if (AUDIT_ENABLE_OFF.equals(auditEnable)) {
                return handleAuditDisable(tenantId, operator, reason);
            } else {
                // 6. 启用功能
                return handleAuditEnable(tenantId, operator, reason, currentConfig);
            }

        } catch (Exception e) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "审核开关状态更新异常：" + e.getMessage());
        }
    }

    /**
     * 处理审核功能关闭
     */
    private AppResponse<String> handleAuditDisable(String tenantId, String operator, String reason) {
        try {
            // 1. 自动审批未审核的上架申请
            int approvedCount = appApplicationDao.autoApproveReleaseApplications(tenantId, operator);

            // 2. 逻辑删除开启阶段的所有审核申请记录
            int deletedCount = appApplicationDao.deleteAuditRecords(tenantId, operator);

            // 3. 更新审核开关状态
            int result =
                    appApplicationTenantDao.insertOrUpdateAuditEnable(tenantId, AUDIT_ENABLE_OFF, operator, reason);

            if (result > 0) {
                String message = String.format("审核功能已关闭。自动审批了 %d 个上架申请，删除了 %d 条审核记录。", approvedCount, deletedCount);
                return AppResponse.success(message);
            } else {
                return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "审核开关状态更新失败");
            }

        } catch (Exception e) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "关闭审核功能异常");
        }
    }

    /**
     * 处理审核功能启用
     */
    private AppResponse<String> handleAuditEnable(
            String tenantId, String operator, String reason, AppApplicationTenant currentConfig) {
        try {
            // 1. 更新审核开关状态
            int result;
            if (currentConfig == null) {
                // 插入新配置
                result = appApplicationTenantDao.insertOrUpdateAuditEnable(tenantId, AUDIT_ENABLE_ON, operator, reason);
            } else {
                // 更新现有配置
                result = appApplicationTenantDao.updateAuditEnable(tenantId, AUDIT_ENABLE_ON, operator, reason);
            }

            if (result > 0) {
                return AppResponse.success("审核功能已启用");
            } else {
                return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "审核开关状态更新失败");
            }

        } catch (Exception e) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "启用审核功能异常");
        }
    }

    @Override
    public AppResponse<String> getAuditStatus() throws NoLoginException {
        // 1. 获取当前租户ID
        String tenantId = TenantUtils.getTenantId();
        if (StringUtils.isBlank(tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
        }

        try {
            // 2. 查询当前审核开关状态
            AppApplicationTenant currentConfig = appApplicationTenantDao.getByTenantId(tenantId);

            // 3. 如果配置不存在，默认返回禁用状态
            if (currentConfig == null) {
                return AppResponse.success(AUDIT_ENABLE_STATUS_OFF);
            }

            // 4. 根据数据库中的状态返回对应的字符串
            String status = AUDIT_ENABLE_ON.equals(currentConfig.getAuditEnable())
                    ? AUDIT_ENABLE_STATUS_ON
                    : AUDIT_ENABLE_STATUS_OFF;

            return AppResponse.success(status);

        } catch (Exception e) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "查询审核开关状态异常：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<Integer> preReleaseCheck(PreReleaseCheckDto dto) throws Exception {
        String tenantId = TenantUtils.getTenantId();
        // 1. 租户是否开启上架审核？未开启直接返回0
        AppApplicationTenant auditConfig = appApplicationTenantDao.getByTenantId(tenantId);
        if (auditConfig == null || AUDIT_ENABLE_OFF.equals(auditConfig.getAuditEnable())) {
            return AppResponse.success(0);
        }
        // 2. 租户开启上架审核；检查是否有未删除通过的上架审核？
        AppApplication approvedApplication = this.getOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, dto.getRobotId())
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0)
                .orderByDesc(AppApplication::getRobotVersion)
                .last("LIMIT 1"));
        if (approvedApplication != null) {
            // 如果是现在版本的，直接返回0
            if (Objects.equals(dto.getVersion(), approvedApplication.getRobotVersion())) {
                return AppResponse.success(0);
            }
            // 3. 如果是之前版本的：若密级为绿色且勾选自动通过则直接返回0，否则返回1
            String securityLevel = approvedApplication.getSecurityLevel();
            Integer defaultPass = approvedApplication.getDefaultPass();
            if ("green".equals(securityLevel) && Integer.valueOf(1).equals(defaultPass)) {
                return AppResponse.success(0);
            } else {
                return AppResponse.success(1);
            }
        }
        // 4. 如果没有上架审核记录，则返回1
        return AppResponse.success(1);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> submitReleaseApplication(ReleaseApplicationDto applicationDto) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        AppResponse<String> greenPass = greenPassHandle(applicationDto, userId, tenantId);
        if (greenPass != null) return greenPass;

        AppResponse<String> E_SERVICE = beforeSubmitCheck(applicationDto, userId);
        if (E_SERVICE != null) return E_SERVICE;

        // 创建上架审核申请
        AppApplication application = new AppApplication();
        application.setRobotId(applicationDto.getRobotId());
        application.setRobotVersion(applicationDto.getRobotVersion());
        application.setApplicationType("release");
        application.setStatus("pending");
        application.setCreatorId(userId);
        application.setTenantId(tenantId);
        application.setCreateTime(new Date());
        application.setUpdateTime(new Date());
        application.setDeleted(0);
        // 保存市场信息
        String marketInfoJson = convertMarketInfoToJson(
                applicationDto.getMarketIdList(), applicationDto.getEditFlag(), applicationDto.getCategory());
        application.setMarketInfo(marketInfoJson);

        appApplicationDao.insert(application);

        return AppResponse.success("上架申请提交成功，请等待审核");
    }

    private AppResponse<String> greenPassHandle(ReleaseApplicationDto applicationDto, String userId, String tenantId)
            throws Exception {
        // 先检查 上一个申请单 -> 密级为绿色并勾选自动通过的 已批准的申请单
        AppApplication greenPass = appApplicationDao.selectOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, applicationDto.getRobotId())
                .eq(
                        AppApplication::getRobotVersion,
                        applicationDto.getRobotVersion() > 1 ? applicationDto.getRobotVersion() - 1 : 1)
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getSecurityLevel, "green")
                .eq(AppApplication::getDefaultPass, 1));
        if (greenPass != null) {
            AppApplication application = createGreenPassApplication(applicationDto, userId, tenantId);
            appApplicationDao.insert(application);
            AuditApplicationDto auditApplicationDto = new AuditApplicationDto();
            BeanUtils.copyProperties(application, auditApplicationDto);
            releaseHandle(auditApplicationDto, application);
            return AppResponse.success("上架申请提交成功，请等待审核");
        }
        return null;
    }

    @NotNull
    private AppApplication createGreenPassApplication(
            ReleaseApplicationDto applicationDto, String userId, String tenantId) {
        AppApplication application = new AppApplication();
        application.setDeleted(0);
        application.setRobotId(applicationDto.getRobotId());
        application.setRobotVersion(applicationDto.getRobotVersion());

        application.setApplicationType("release");
        application.setStatus(AUDIT_STATUS_APPROVED);
        application.setCreatorId(userId);
        application.setTenantId(tenantId);
        application.setCreateTime(new Date());
        application.setUpdateTime(new Date());
        application.setSecurityLevel("green");
        application.setDefaultPass(1);
        application.setAuditOpinion("自动通过");
        // 保存市场信息
        String marketInfoJson = convertMarketInfoToJson(
                applicationDto.getMarketIdList(), applicationDto.getEditFlag(), applicationDto.getCategory());
        application.setMarketInfo(marketInfoJson);
        return application;
    }

    @Nullable
    private AppResponse<String> beforeSubmitCheck(ReleaseApplicationDto applicationDto, String userId) {
        // 作废该机器人已审核通过的历史上架申请，使已获取或部署的机器人不可用，直到这一次申请通过审核
        // status 设置为 null
        this.update(new LambdaUpdateWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, applicationDto.getRobotId())
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .set(AppApplication::getStatus, AUDIT_STATUS_NULLIFY)
                .set(AppApplication::getUpdateTime, new Date())
                .set(AppApplication::getUpdaterId, userId));

        // 检查是否已有待审核的申请
        AppApplication existingApplication = appApplicationDao.selectOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, applicationDto.getRobotId())
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, "pending")
                .eq(AppApplication::getDeleted, 0));

        if (existingApplication != null) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "当前已存在正在上架审核的申请单，请先处理后再进行分享");
        }
        return null;
    }

    @Override
    public AppResponse<?> preSubmitAfterPublishCheck(PreReleaseCheckDto dto) throws NoLoginException {
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        // 1. 租户是否开启上架审核？未开启直接返回0
        AppApplicationTenant auditConfig = appApplicationTenantDao.getByTenantId(tenantId);
        if (auditConfig == null || AUDIT_ENABLE_OFF.equals(auditConfig.getAuditEnable())) {
            return AppResponse.success(0);
        }
        // 2. 检查是否机器人是否上架过
        List<AppMarketResource> appInfoList = appMarketResourceDao.getAppInfoByRobotId(dto.getRobotId(), userId);
        if (!CollectionUtils.isEmpty(appInfoList)) {
            AppMarketResource appMarketResourceAnyOne = appInfoList.get(0);
            MarketResourceDto marketResourceDto = new MarketResourceDto();
            marketResourceDto.setMarketId(appMarketResourceAnyOne.getMarketId());
            marketResourceDto.setAppId(appMarketResourceAnyOne.getAppId());
            AppMarketVersion latestAppVersion = appMarketVersionDao.getLatestAppVersionInfo(marketResourceDto);
            String category = latestAppVersion.getCategory();
            Integer editFlag = latestAppVersion.getEditFlag();
            List<String> marketIdList =
                    appInfoList.stream().map(AppMarketResource::getMarketId).collect(Collectors.toList());
            MarketInfoVo vo = new MarketInfoVo();
            vo.setMarketIdList(marketIdList);
            vo.setEditFlag(editFlag);
            vo.setCategory(category);
            return AppResponse.success(vo);
        }
        return AppResponse.success(0);
    }

    @Override
    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRED)
    public AppResponse<String> submitAfterPublish(SubmitAfterPublishDto dto) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        AppResponse<String> greenPass = greenPassHandle(dto, userId, tenantId);
        if (greenPass != null) return greenPass;

        AppResponse<String> E_SERVICE = beforeSubmitCheck(dto, userId);
        if (E_SERVICE != null) return E_SERVICE;

        // 创建上架审核申请
        AppApplication application = new AppApplication();
        application.setRobotId(dto.getRobotId());
        application.setRobotVersion(dto.getRobotVersion());
        application.setApplicationType("release");
        application.setStatus("pending");
        application.setCreatorId(userId);
        application.setTenantId(tenantId);
        application.setCreateTime(new Date());
        application.setUpdateTime(new Date());
        application.setDeleted(0);

        dto.setCreatorId(userId);
        dto.setTenantId(tenantId);
        String publishInfo = convertPublishInfoBoToJson(dto);

        // 如果是第一次 发版的
        if (dto.getRobotVersion() <= 1) {
            // 保存市场信息
            String marketInfoJson =
                    convertMarketInfoToJson(dto.getMarketIdList(), dto.getEditFlag(), dto.getCategory());
            application.setMarketInfo(marketInfoJson);
        }

        application.setPublishInfo(publishInfo);
        appApplicationDao.insert(application);

        return AppResponse.success("上架申请提交成功，请等待审核");
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

    private String convertPublishInfoBoToJson(SubmitAfterPublishDto dto) throws JsonProcessingException {
        String creatorId = dto.getCreatorId();
        String tenantId = dto.getTenantId();
        String robotId = dto.getRobotId();
        String name = dto.getName();
        RobotExecute robotExecute = new RobotExecute();
        robotExecute.setRobotId(robotId);
        robotExecute.setCreatorId(creatorId);
        robotExecute.setTenantId(tenantId);
        robotExecute.setName(name);

        PublishInfoBo bo = new PublishInfoBo();
        bo.setRobotExecute(robotExecute);
        bo.setNextVersion(dto.getRobotVersion());
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.writeValueAsString(bo);
    }

    private PublishInfoBo parsePublishInfoBoFromJson(String PublishInfoBoJson) throws JsonProcessingException {
        if (StringUtils.isBlank(PublishInfoBoJson)) {
            return null;
        }

        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(PublishInfoBoJson, PublishInfoBo.class);
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

    //    @Override
    //    public AppResponse<?> excellenceDeployCheck(ExcellenceDeployDto deployDto) throws Exception {
    //        String tenantId = TenantUtils.getTenantId();
    //        if (!isAuditFunctionEnabled(tenantId)) {
    //            return AppResponse.success("审核功能未开启，无需权限检查");
    //        }
    //        // 获取机器人密级
    //        String robotId = deployDto.getRobotId();
    //        AppApplication robotApplication = appApplicationDao.selectOne(
    //                new LambdaQueryWrapper<AppApplication>()
    //                        .eq(AppApplication::getRobotId, robotId)
    //                        .eq(AppApplication::getApplicationType, "release")
    //                        .eq(AppApplication::getStatus, "approved")
    //                        .eq(AppApplication::getDeleted, 0)
    //                        .last("LIMIT 1")
    //        );
    //        if (robotApplication == null) {
    //            // 沒有通过的上架审核 也可以进行部署
    //            return AppResponse.success("ok");
    //        }
    //        String robotSecurityLevel = robotApplication.getSecurityLevel();
    //        if (org.apache.commons.lang3.StringUtils.isBlank(robotSecurityLevel)) {
    //            return AppResponse.success("ok");
    //        }
    //        List<String> userIdList = deployDto.getUserIdList();
    //        List<String> highSecurityUserIdList = new ArrayList<>();
    //        for (String userId : userIdList) {
    //            // 这里应根据实际业务判断租户密级权限，以下为示例
    //            if ("red".equals(robotSecurityLevel) && !hasRedSecurityPermission(userId, deployDto.getRobotId())) {
    //                highSecurityUserIdList.add(userId);
    //            } else if ("yellow".equals(robotSecurityLevel) && !hasYellowSecurityPermission(userId,
    // deployDto.getRobotId())) {
    //                highSecurityUserIdList.add(userId);
    //            }
    //        }
    //        if (!highSecurityUserIdList.isEmpty()) {
    //            String userNames = getUserNames(highSecurityUserIdList);
    //            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "当前机器人密级高于待添加账号：" + userNames + "的权限，请确认是否继续部署");
    //        }
    //        return AppResponse.success("ok");
    //    }

    // 以下为权限判断和租户名获取的占位方法
    private boolean hasRedSecurityPermission(String userId, String robotId) {
        // 查询最近申请的这个机器人是否通过
        AppApplication appApplication = appApplicationDao.selectOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getStatus, "approved")
                .eq(AppApplication::getDeleted, 0)
                .orderByDesc(AppApplication::getCreateTime)
                .last("LIMIT 1"));
        return appApplication != null;
    }

    private String getUserNames(List<String> userIdList) throws IOException {
        // 根据用户ID列表获取用户名称
        List<User> userList = UserUtils.queryUserPageList(userIdList);
        if (userList.isEmpty()) {
            return "";
        }
        return joinUserName(userList);
    }

    private String joinUserName(List<User> userList) {
        if (CollectionUtils.isEmpty(userList)) return null;

        String resStr = "";
        for (int i = 0; i < userList.size(); i++) {
            String name = userList.get(i).name;
            if (i == 0) {
                resStr = name;
                continue;
            }
            resStr = resStr + "," + name;
        }

        return resStr;
    }

    public List<LatestVersionRobotVo> getRobotListApplicationStatus(List<LatestVersionRobotVo> voList) {
        voList.removeIf(Objects::isNull);
        if (voList.isEmpty()) {
            return voList;
        }
        // 提取robotId和latestVersion构建查询条件
        List<String> robotIds = voList.stream()
                .map(LatestVersionRobotVo::getRobotId)
                .filter(Objects::nonNull)
                .distinct()
                .collect(Collectors.toList());

        if (robotIds.isEmpty()) {
            // 如果没有robotId，直接设置为none
            voList.forEach(vo -> vo.setApplicationStatus("none"));
            return voList;
        }

        // 查询审核记录
        List<AppApplication> applications = this.list(
                new LambdaQueryWrapper<AppApplication>()
                        .in(AppApplication::getRobotId, robotIds)
                        .eq(AppApplication::getDeleted, 0)
                        .eq(AppApplication::getCloudDeleted, 0)
                        .eq(AppApplication::getApplicationType, "release") // 只查询上架申请
                );

        // 构建Map便于查找: robotId_robotVersion -> status
        Map<String, String> robotVersionStatusMap = applications.stream()
                .collect(Collectors.toMap(
                        app -> app.getRobotId() + "_" + app.getRobotVersion(),
                        AppApplication::getStatus,
                        (existing, replacement) -> existing // 如果有重复，保留现有的
                        ));

        // 设置applicationStatus
        voList.forEach(vo -> {
            vo.setApplicationStatus("none");

            String key = vo.getRobotId() + "_" + vo.getLatestVersion();
            String status = robotVersionStatusMap.get(key);
            if (status != null) {
                if (Objects.equals(status, AUDIT_STATUS_PENDING) || Objects.equals(status, AUDIT_STATUS_APPROVED)) {
                    vo.setApplicationStatus(status);
                }
            }
        });
        return voList;
    }

    @Override
    public AppResponse<IPage<MyApplicationPageListVo>> getMyApplicationPageList(MyApplicationPageListDto queryDto)
            throws NoLoginException {
        String tenantId = TenantUtils.getTenantId();
        queryDto.setTenantId(tenantId);

        // 如果没有传入userId，则使用当前登录用户ID
        if (StringUtils.isBlank(queryDto.getUserId())) {
            queryDto.setUserId(UserUtils.nowUserId());
        }

        IPage<MyApplicationPageListVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        IPage<MyApplicationPageListVo> myApplicationPage =
                appApplicationDao.getMyApplicationPageList(pageConfig, queryDto);
        List<MyApplicationPageListVo> records = myApplicationPage.getRecords();
        records.removeIf(Objects::isNull);

        return AppResponse.success(myApplicationPage);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> cancelMyApplication(MyApplicationDto dto) throws NoLoginException {
        if (dto == null || StringUtils.isBlank(dto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "申请ID不能为空");
        }
        AppApplication application = this.getById(dto.getId());
        if (application == null || application.getDeleted() == 1 || application.getCloudDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "申请不存在或已被删除");
        }
        if (!AUDIT_STATUS_PENDING.equals(application.getStatus())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能撤销待审核状态的申请");
        }
        if (!UserUtils.nowUserId().equals(application.getCreatorId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能撤销自己的申请");
        }
        application.setStatus(AUDIT_STATUS_CANCELED);
        application.setUpdateTime(new Date());
        application.setUpdaterId(UserUtils.nowUserId());
        boolean updateResult = this.updateById(application);
        if (!updateResult) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "撤销申请失败");
        }
        return AppResponse.success("撤销申请成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteMyApplication(MyApplicationDto dto) throws NoLoginException {
        if (dto == null || StringUtils.isBlank(dto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "申请ID不能为空");
        }
        AppApplication application = this.getById(dto.getId());
        if (application == null || application.getDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "申请不存在或已被删除");
        }
        if (!UserUtils.nowUserId().equals(application.getCreatorId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "只能删除自己的申请");
        }
        // 根据状态决定删除方式
        String status = application.getStatus();

        if (AUDIT_STATUS_APPROVED.equals(status) || AUDIT_STATUS_REJECTED.equals(status)) {
            // 对于已通过/已驳回的申请记录，客户端单方面删除
            application.setClientDeleted(1);
        } else if (AUDIT_STATUS_PENDING.equals(status)) {
            // 对于待审核的申请记录会直接删除
            application.setDeleted(1);
        } else if (AUDIT_STATUS_CANCELED.equals(status)) {
            // 对于已撤销的申请记录会删除
            application.setCloudDeleted(1);
            application.setDeleted(1);
        } else {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "未知的申请状态：" + status);
        }
        application.setUpdateTime(new Date());
        application.setUpdaterId(UserUtils.nowUserId());
        boolean updateResult = this.updateById(application);
        if (!updateResult) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "删除申请失败");
        }
        return AppResponse.success("删除申请成功");
    }

    @Override
    public void packageApplicationInfo(
            List<AppMarketResource> appResourceList, List<ResVerDto> resVerDtoList, String userId) {
        if (appResourceList == null || resVerDtoList == null || appResourceList.isEmpty() || resVerDtoList.isEmpty()) {
            return;
        }
        List<String> robotIds = resVerDtoList.stream()
                .map(ResVerDto::getRobotId)
                .filter(StringUtils::isNotBlank)
                .distinct()
                .collect(Collectors.toList());
        if (robotIds.isEmpty()) return;

        // 通过上架申请填充密级标识
        packageReleaseApplicationInfo(appResourceList, resVerDtoList, robotIds);

        // 通过使用申请填充过期时间
        packageUseApplicationInfo(appResourceList, resVerDtoList, robotIds, userId);
    }

    private void packageReleaseApplicationInfo(
            List<AppMarketResource> appResourceList, List<ResVerDto> resVerDtoList, List<String> robotIds) {
        List<AppApplication> releaseApplicationList = this.list(new LambdaQueryWrapper<AppApplication>()
                .in(AppApplication::getRobotId, robotIds)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0));
        Map<String, AppApplication> appMap = releaseApplicationList.stream()
                .collect(Collectors.toMap(
                        app -> app.getRobotId() + "_" + app.getRobotVersion(),
                        app -> app,
                        (existing, replacement) -> existing));
        Map<String, Integer> robotVersionMap = resVerDtoList.stream()
                .collect(Collectors.toMap(
                        ResVerDto::getRobotId, ResVerDto::getLatestAppVersion, (existing, replacement) -> existing));
        appResourceList.forEach(resource -> {
            String robotId = resource.getRobotId();
            if (StringUtils.isBlank(robotId)) return;
            Integer version = robotVersionMap.get(robotId);
            if (version == null) return;
            AppApplication app = appMap.get(robotId + "_" + version);
            if (app != null) {
                resource.setSecurity_level(app.getSecurityLevel());
            }
        });
    }

    private void packageUseApplicationInfo(
            List<AppMarketResource> appResourceList,
            List<ResVerDto> resVerDtoList,
            List<String> robotIds,
            String userId) {
        List<AppApplication> useApplicationList = this.list(new LambdaQueryWrapper<AppApplication>()
                .in(AppApplication::getRobotId, robotIds)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getCreatorId, userId)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0));
        Map<String, AppApplication> appMap = useApplicationList.stream()
                .collect(Collectors.toMap(
                        app -> app.getRobotId() + "_" + app.getRobotVersion(),
                        app -> app,
                        (existing, replacement) -> existing));
        Map<String, Integer> robotVersionMap = resVerDtoList.stream()
                .collect(Collectors.toMap(
                        ResVerDto::getRobotId, ResVerDto::getLatestAppVersion, (existing, replacement) -> existing));
        appResourceList.forEach(resource -> {
            String robotId = resource.getRobotId();
            if (StringUtils.isBlank(robotId)) return;

            Integer version = robotVersionMap.get(robotId);
            if (version == null) return;

            AppApplication app = appMap.get(robotId + "_" + version);
            if (app != null) {
                // 使用期限 从 use类型的数据中读取
                resource.setExpiry_date(app.getExpireTime());
                resource.setExpiry_date_str(getExpiryDateString(app.getExpireTime()));
            }
        });
    }

    @Override
    public void packageUsePermission(List<ExecuteListVo> ansRecords) throws NoLoginException {
        ansRecords.removeIf(Objects::isNull);
        if (ansRecords.isEmpty()) {
            return;
        }
        // 1. 检查当前租户是否开启了上架审核
        String tenantId = TenantUtils.getTenantId();
        boolean isAuditEnabled = isAuditFunctionEnabled(tenantId);
        String currentUserId = UserUtils.nowUserId();

        // ===== 性能优化：批量查询减少数据库IO =====
        // 收集所有企业市场应用的appId，通过去重避免重复查询
        List<String> enterpriseAppIds = ansRecords.stream()
                .filter(record -> "企业市场".equals(record.getSourceName()))
                .map(ExecuteListVo::getAppId)
                .filter(StringUtils::isNotBlank)
                .distinct()
                .collect(Collectors.toList());

        // 预查询数据存储映射，避免在循环中重复数据库查询
        Map<String, AppApplication> approvedApplicationMap = new HashMap<>();
        Map<String, AppApplication> userApplicationMap = new HashMap<>();

        if (isAuditEnabled && !enterpriseAppIds.isEmpty()) {
            // 1. 查询所有相关的上架申请
            approvedApplicationMap = batchGetApprovedApplications(enterpriseAppIds, tenantId);

            // 2. 收集所有robotId，批量查询用户使用申请（主要优化点）
            Set<String> robotIds = approvedApplicationMap.values().stream()
                    .map(AppApplication::getRobotId)
                    .filter(StringUtils::isNotBlank)
                    .collect(Collectors.toSet());

            if (!robotIds.isEmpty()) {
                userApplicationMap = batchGetUserApplications(robotIds, currentUserId);
            }
        }

        // 2. 处理每个记录
        for (ExecuteListVo record : ansRecords) {
            // 初始化权限为null
            record.setUsePermission(null);
            // 只处理企业市场应用
            if (!"企业市场".equals(record.getSourceName())) {
                continue;
            }
            // 审核功能未开启，直接设置为有权限
            if (!isAuditEnabled) {
                record.setUsePermission(1);
                continue;
            }
            // 审核功能已开启，检查具体权限并填充过期时间
            checkMarketAppPermissionOptimized(record, currentUserId, approvedApplicationMap, userApplicationMap);
        }
    }

    /**
     * 批量查询上架申请
     * 注意：由于DAO层getApplicationByObtainedAppId方法的限制，这里仍需要逐个查询
     * 但通过预先收集和去重，减少了总的查询次数
     */
    private Map<String, AppApplication> batchGetApprovedApplications(List<String> appIds, String tenantId) {
        Map<String, AppApplication> resultMap = new HashMap<>();

        for (String appId : appIds) {
            AppApplication approvedApp = appApplicationDao.getApplicationByObtainedAppId(appId, tenantId);
            if (approvedApp != null) {
                resultMap.put(appId, approvedApp);
            }
        }
        return resultMap;
    }

    /**
     * 批量查询用户使用申请
     */
    private Map<String, AppApplication> batchGetUserApplications(Set<String> robotIds, String currentUserId) {
        List<AppApplication> userApplications = this.list(new LambdaQueryWrapper<AppApplication>()
                .in(AppApplication::getRobotId, robotIds)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getCreatorId, currentUserId)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0));

        return userApplications.stream()
                .collect(Collectors.toMap(
                        AppApplication::getRobotId, app -> app, (existing, replacement) -> existing // 保留第一个匹配的记录
                        ));
    }

    /**
     * 检查市场应用的使用权限（优化版本，使用预查询的数据）
     */
    private void checkMarketAppPermissionOptimized(
            ExecuteListVo record,
            String currentUserId,
            Map<String, AppApplication> approvedApplicationMap,
            Map<String, AppApplication> userApplicationMap) {
        String appId = record.getAppId();
        if (StringUtils.isBlank(appId)) {
            record.setUsePermission(0);
            return;
        }

        // 从预查询的映射中获取上架申请
        AppApplication approvedApplication = approvedApplicationMap.get(appId);
        if (approvedApplication == null) {
            record.setUsePermission(0);
            return;
        }

        // 检查密级权限
        String securityLevel = approvedApplication.getSecurityLevel();
        if (securityLevel == null || StringUtils.isBlank(securityLevel)) {
            record.setUsePermission(1);
            return;
        }

        // 使用申请的robotId
        String useApplicationRobotId = approvedApplication.getRobotId();

        // 根据密级检查权限
        boolean hasPermission = checkUserPermissionForSecurityLevelOptimized(
                currentUserId,
                securityLevel,
                approvedApplication.getAllowedDept(),
                useApplicationRobotId,
                userApplicationMap);
        record.setUsePermission(hasPermission ? 1 : 0);

        // 填充过期时间
        if ("red".equals(securityLevel)) {
            // 从预查询的映射中获取用户申请
            AppApplication userApplication = userApplicationMap.get(useApplicationRobotId);
            if (userApplication != null) {
                Date expireDate = userApplication.getExpireTime();
                record.setExpiryDate(expireDate);
                record.setExpiryDateStr(getExpiryDateString(expireDate));
            }
        }
    }

    /**
     * 根据密级标识检查用户权限（优化版本，用于批量处理）
     */
    private boolean checkUserPermissionForSecurityLevelOptimized(
            String currentUserId,
            String securityLevel,
            String allowedDept,
            String robotId,
            Map<String, AppApplication> userApplicationMap) {
        switch (securityLevel) {
            case "green":
                return true;
            case "yellow":
                return checkYellowLevelPermissionOptimized(currentUserId, allowedDept, robotId, userApplicationMap);
            case "red":
                return checkRedLevelPermissionOptimized(currentUserId, robotId, userApplicationMap);
            default:
                return false;
        }
    }

    /**
     * 检查黄色密级权限（优化版本）
     */
    private boolean checkYellowLevelPermissionOptimized(
            String currentUserId, String allowedDept, String robotId, Map<String, AppApplication> userApplicationMap) {
        if (StringUtils.isBlank(allowedDept)) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "部门ID不存在");
        }
        // 2. 检查用户是否有通过的使用申请（从预查询映射中获取）
        return userApplicationMap.containsKey(robotId);
    }

    /**
     * 检查红色密级权限（优化版本）
     */
    private boolean checkRedLevelPermissionOptimized(
            String currentUserId, String robotId, Map<String, AppApplication> userApplicationMap) {
        // 从预查询映射中获取用户申请
        AppApplication userApplication = userApplicationMap.get(robotId);
        if (userApplication == null) {
            return false;
        }

        // 检查是否过期
        Date expireDate = userApplication.getExpireTime();
        return expireDate == null || expireDate.after(new Date());
    }

    /**
     * 检查市场应用的使用权限（保留原方法，供其他地方调用）
     */
    private void checkMarketAppPermission(ExecuteListVo record, String currentUserId) {
        String robotId = record.getRobotId();
        Integer version = record.getVersion();
        if (StringUtils.isBlank(robotId) || version == null) {
            record.setUsePermission(0);
            return;
        }
        String tenantId = TenantUtils.getTenantId();
        // 获取对应的上架申请
        AppApplication approvedApplication =
                appApplicationDao.getApplicationByObtainedAppId(record.getAppId(), tenantId);
        if (approvedApplication == null) {
            record.setUsePermission(0);
            return;
        }
        // 检查密级权限
        String securityLevel = approvedApplication.getSecurityLevel();
        if (securityLevel == null || StringUtils.isBlank(securityLevel)) {
            record.setUsePermission(1);
            return;
        }
        // 使用申请的robotId
        String useApplicationRobotId = approvedApplication.getRobotId();
        // 根据密级检查权限
        boolean hasPermission = checkUserPermissionForSecurityLevel(
                currentUserId, securityLevel, approvedApplication.getAllowedDept(), useApplicationRobotId);
        record.setUsePermission(hasPermission ? 1 : 0);
        // 填充过期时间
        if (securityLevel.equals("red")) {
            // 检查用户是否有通过的使用申请
            AppApplication userApplication = getUserUseApplication(currentUserId, useApplicationRobotId);
            if (userApplication == null) {
            } else {
                // 检查是否过期
                Date expireDate = userApplication.getExpireTime();
                record.setExpiryDate(expireDate);
                record.setExpiryDateStr(getExpiryDateString(expireDate));
            }
        }
    }

    /**
     * 计算过期时间字符串
     */
    private String getExpiryDateString(Date expireTime) {
        if (expireTime == null) return null;

        int days = DateUtils.differentDaysByMillisecond(new Date(), expireTime);
        if (days > 0) return days + "天后到期";
        if (days == 0) return "今日到期";
        return "已过期";
    }

    @Override
    public AppResponse<Integer> usePermissionCheck(UsePermissionCheckDto dto) throws Exception {
        // 1. 参数验证
        dto.setTenantId(TenantUtils.getTenantId());
        dto.setUserId(UserUtils.nowUserId());
        // 2. 检查AppResource是否存在
        MarketDto marketDto = new MarketDto();
        marketDto.setTenantId(dto.getTenantId());
        marketDto.setMarketId(dto.getMarketId());
        marketDto.setAppId(dto.getAppId());
        AppMarketResource appResource = appMarketResourceDao.getAppInfoByAppId(marketDto);
        if (appResource == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "应用不存在");
        }
        // 3. 检查上架审核是否开启
        String tenantId = marketDto.getTenantId();
        AppApplicationTenant auditConfig = appApplicationTenantDao.getByTenantId(tenantId);
        // 如果审核未开启，直接返回yes
        if (auditConfig == null || AUDIT_ENABLE_OFF.equals(auditConfig.getAuditEnable())) {
            return AppResponse.success(1);
        }
        // 4. 获取最新版本的robotId
        List<String> appIdList = Collections.singletonList(dto.getAppId());
        List<ResVerDto> resVerDtoList = appMarketVersionDao.getResVerJoin(dto.getMarketId(), appIdList);
        if (resVerDtoList.isEmpty()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "对于应用的robotId不存在");
        }
        String robotId = resVerDtoList.get(0).getRobotId();
        // Integer robotVersion = resVerDtoList.get(0).getLatestAppVersion();
        // 5. 检查是否有通过的上架审核
        AppApplication approvedApplication = this.getOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0)
                .last("LIMIT 1"));
        // 如果没有通过的上架审核，报错
        if (approvedApplication == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "应用没有通过的上架审核");
        }
        // 6. 检查该上架审核的密级标识，根据密级标识检查该用户是否有使用权限
        String securityLevel = approvedApplication.getSecurityLevel();
        if (StringUtils.isBlank(securityLevel)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "应用没有密级标识");
        }
        String currentUserId = UserUtils.nowUserId();
        // 根据密级标识检查用户使用权限
        boolean hasPermission = checkUserPermissionForSecurityLevel(
                currentUserId, securityLevel, approvedApplication.getAllowedDept(), robotId);
        return AppResponse.success(hasPermission ? 1 : 0);
    }

    /**
     * 根据密级标识检查用户权限（用于权限检查接口）
     */
    private boolean checkUserPermissionForSecurityLevel(
            String currentUserId, String securityLevel, String allowedDept, String robotId) {
        switch (securityLevel) {
            case "green":
                return true;
            case "yellow":
                return checkYellowLevelPermission(currentUserId, allowedDept, robotId);
            case "red":
                return checkRedLevelPermission(currentUserId, robotId);
            default:
                return false;
        }
    }

    /**
     * 检查黄色密级权限
     */
    private boolean checkYellowLevelPermission(String currentUserId, String allowedDept, String robotId) {
        if (StringUtils.isBlank(allowedDept)) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "部门ID不存在");
        }
        // 2. 检查用户是否有通过的使用申请
        return hasApprovedUseApplication(currentUserId, robotId);
    }

    /**
     * 检查红色密级权限
     */
    private boolean checkRedLevelPermission(String currentUserId, String robotId) {
        // 检查用户是否有通过的使用申请
        AppApplication userApplication = getUserUseApplication(currentUserId, robotId);
        if (userApplication == null) {
            return false;
        }

        // 检查是否过期
        Date expireDate = userApplication.getExpireTime();
        return expireDate == null || expireDate.after(new Date());
    }

    /**
     * 检查用户是否有通过的使用申请
     */
    private boolean hasApprovedUseApplication(String currentUserId, String robotId) {
        return getUserUseApplication(currentUserId, robotId) != null;
    }

    /**
     * 获取对于机器人,用户的使用申请
     */
    private AppApplication getUserUseApplication(String currentUserId, String robotId) {
        return this.getOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getCreatorId, currentUserId)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0)
                .last("LIMIT 1"));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> submitUseApplication(UsePermissionCheckDto dto) throws Exception {
        dto.setTenantId(TenantUtils.getTenantId());
        dto.setUserId(UserUtils.nowUserId());

        List<String> appIdList = Collections.singletonList(dto.getAppId());
        List<ResVerDto> resVerDtoList = appMarketVersionDao.getResVerJoin(dto.getMarketId(), appIdList);
        if (resVerDtoList.isEmpty()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "找不到对应的应用版本信息");
        }
        String robotId = resVerDtoList.get(0).getRobotId();
        Integer version = resVerDtoList.get(0).getLatestAppVersion();

        // 检查是否重复提交
        AppApplication existingUseApplication = this.getOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getApplicationType, "use")
                .eq(AppApplication::getCreatorId, dto.getUserId())
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0)
                .in(AppApplication::getStatus, Arrays.asList(AUDIT_STATUS_PENDING, AUDIT_STATUS_APPROVED))
                .last("LIMIT 1"));
        if (existingUseApplication != null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "您已经有该应用的使用申请，请勿重复提交");
        }
        AppApplication approvedReleaseApplication = this.getOne(new LambdaQueryWrapper<AppApplication>()
                .eq(AppApplication::getRobotId, robotId)
                .eq(AppApplication::getRobotVersion, version)
                .eq(AppApplication::getApplicationType, "release")
                .eq(AppApplication::getStatus, AUDIT_STATUS_APPROVED)
                .eq(AppApplication::getDeleted, 0)
                .eq(AppApplication::getCloudDeleted, 0)
                .last("LIMIT 1"));
        if (approvedReleaseApplication == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "上架申请不存在");
        }
        AppApplication useApplication = new AppApplication();
        useApplication.setSecurityLevel(approvedReleaseApplication.getSecurityLevel());
        useApplication.setRobotId(robotId);
        useApplication.setRobotVersion(version);
        useApplication.setApplicationType("use");
        useApplication.setStatus(AUDIT_STATUS_PENDING);
        useApplication.setCreatorId(dto.getUserId());
        useApplication.setTenantId(dto.getTenantId());
        useApplication.setCreateTime(new Date());
        useApplication.setUpdaterId(dto.getUserId());
        useApplication.setUpdateTime(new Date());
        useApplication.setDeleted(0);
        useApplication.setClientDeleted(0);
        useApplication.setCloudDeleted(0);
        boolean saved = this.save(useApplication);
        if (!saved) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "提交使用申请失败");
        }
        return AppResponse.success("使用申请提交成功");
    }
}
