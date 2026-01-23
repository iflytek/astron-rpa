package com.iflytek.rpa.auth.idp.iflytekIdentity.task;

import cn.hutool.core.collection.CollectionUtil;
import com.iflytek.rpa.auth.idp.iflytekIdentity.IflytekAuthenticationServiceImpl;
import com.iflytek.rpa.auth.idp.iflytekIdentity.dto.IflytekSyncUserInfoAccount;
import com.iflytek.rpa.auth.idp.iflytekIdentity.dto.IflytekSyncUserInfoUserInfo;
import com.iflytek.rpa.auth.sp.uap.dao.RoleDao;
import com.iflytek.rpa.auth.sp.uap.dao.TenantDao;
import com.iflytek.rpa.auth.sp.uap.dao.UserDao;
import com.iflytek.rpa.auth.sp.uap.entity.SyncUserInfo;
import com.iflytek.rpa.auth.sp.uap.service.impl.UserServiceImpl;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.tenant.ListTenantDto;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import com.iflytek.sec.uap.client.core.dto.user.BindRoleDto;
import com.iflytek.sec.uap.client.core.dto.user.ListUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.sql.Connection;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;

/**
 * 用户同步任务服务
 * 将现有数据库中的人员同步到讯飞账号
 */
@Slf4j
@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "saas", matchIfMissing = true)
@RequiredArgsConstructor
public class UserSyncTask {

    private final UserDao userDao;
    private final IflytekAuthenticationServiceImpl authenticationService;
    private final RoleDao roleDao;
    private final TenantDao tenantDao;
    private final UserServiceImpl userService;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired(required = false)
    private DataSource dataSource;

    @Autowired(required = false)
    private Environment environment;

    // 同步任务执行锁的Redis key（用于防止并发执行）
    private static final String SYNC_TASK_LOCK_KEY = "auth:user_sync_task:lock";
    // 锁的过期时间（秒），设置为1小时
    private static final int LOCK_EXPIRE_TIME = 3600;

    /**
     * 同步失败信息
     */
    @Data
    public static class SyncFailureInfo {
        private String loginName;
        private String phone;
        private String reason;

        public SyncFailureInfo(String loginName, String phone, String reason) {
            this.loginName = loginName;
            this.phone = phone;
            this.reason = reason;
        }
    }

    /**
     * 同步结果统计
     */
    @Data
    public static class SyncResult {
        private int totalCount;
        private int successCount;
        private int failCount;
        private int skipCount;
        private String message;
        private List<SyncFailureInfo> failureList = new ArrayList<>();
    }

    /**
     * 执行用户同步任务
     *
     * @param force 是否强制执行（忽略锁）
     * @param loginNames 可选，指定要同步的用户登录名列表，为空则同步所有符合条件的用户
     * @return 同步结果
     */
    public SyncResult executeSync(boolean force, List<String> loginNames) {
        SyncResult result = new SyncResult();

        // 检查是否有任务正在执行（防止并发）
        if (!force) {
            Object lock = RedisUtils.get(SYNC_TASK_LOCK_KEY);
            if (lock != null) {
                result.setMessage("同步任务正在执行中，请稍后再试");
                log.warn("用户同步任务正在执行中，跳过本次请求");
                return result;
            }
        }

        // 设置分布式锁
        try {
            RedisUtils.set(SYNC_TASK_LOCK_KEY, "1", LOCK_EXPIRE_TIME);

            log.info("==================== 开始执行用户同步任务 ====================");
            if (CollectionUtil.isNotEmpty(loginNames)) {
                log.info("指定同步用户列表，数量：{}", loginNames.size());
            }

            // 查询需要同步的用户
            List<SyncUserInfo> usersToSync = userDao.queryUsersToSync(databaseName, loginNames);
            result.setTotalCount(usersToSync.size());
            log.info("查询到需要同步的用户数量：{}", usersToSync.size());

            if (usersToSync.isEmpty()) {
                result.setMessage("没有需要同步的用户");
                log.info("没有需要同步的用户");
                return result;
            }

            int successCount = 0;
            int failCount = 0;
            int skipCount = 0;
            int totalCount = usersToSync.size();
            int processedCount = 0;

            for (SyncUserInfo user : usersToSync) {
                processedCount++;
                // 每处理10个用户或处理完成时打印进度
                if (processedCount % 10 == 0 || processedCount == totalCount) {
                    log.info(
                            "用户同步进度：{}/{} ({}%)，成功：{}，失败：{}，跳过：{}",
                            processedCount,
                            totalCount,
                            String.format("%.1f", (processedCount * 100.0 / totalCount)),
                            successCount,
                            failCount,
                            skipCount);
                }

                try {
                    // 生成唯一的userid：RPA + 时间戳（精确到毫秒）+ 随机数确保唯一性
                    String userid = generateUserId();

                    // 构建登录账号信息
                    IflytekSyncUserInfoAccount account = new IflytekSyncUserInfoAccount(user.getPhone(), "86", 1);
                    List<IflytekSyncUserInfoAccount> loginAccounts = Arrays.asList(account);

                    // 构建用户详细信息
                    IflytekSyncUserInfoUserInfo userInfo = new IflytekSyncUserInfoUserInfo(
                            user.getName() != null ? user.getName() : "",
                            "", // headpic为空
                            "", // sign为空
                            "0", // sex固定为0
                            user.getAddress() != null ? user.getAddress() : "",
                            null // extras为空
                            );

                    // 调用同步接口
                    authenticationService.syncUserInfo(userid, "", loginAccounts, userInfo);

                    // 同步成功后，更新third_ext_info字段
                    userDao.updateThirdExtInfo(user.getLoginName(), userid, databaseName);
                    // 将 ext_info 标记为已同步
                    userDao.updateExtInfo(user.getPhone(), "1", databaseName);

                    successCount++;
                    log.info("用户同步成功，登录名：{}，手机号：{}，userid：{}", user.getLoginName(), user.getPhone(), userid);

                    // 避免请求过于频繁，添加短暂延迟
                    Thread.sleep(100);

                } catch (Exception e) {
                    String errorMessage = e.getMessage() != null
                            ? e.getMessage()
                            : e.getClass().getSimpleName();

                    // 记录失败账号信息
                    result.getFailureList()
                            .add(new SyncFailureInfo(user.getLoginName(), user.getPhone(), errorMessage));
                    // 如果是用户已存在或登录方式重复，跳过该用户
                    if (e.getMessage() != null
                            && (e.getMessage().contains("用户已存在")
                                    || e.getMessage().contains("登录方式重复"))) {
                        skipCount++;
                        log.warn("用户同步跳过，登录名：{}，手机号：{}，原因：{}", user.getLoginName(), user.getPhone(), errorMessage);
                    } else {
                        failCount++;

                        log.error("用户同步失败，登录名：{}，手机号：{}，原因：{}", user.getLoginName(), user.getPhone(), errorMessage, e);
                    }
                }
            }

            result.setSuccessCount(successCount);
            result.setFailCount(failCount);
            result.setSkipCount(skipCount);

            // 构建返回消息
            String messageBuilder = String.format(
                    "同步完成：成功 %d 个，失败 %d 个，跳过 %d 个，总计 %d 个", successCount, failCount, skipCount, usersToSync.size());

            result.setMessage(messageBuilder);

            log.info("==================== 用户同步任务执行完成 ====================");
            log.info(result.getMessage());

        } catch (Exception e) {
            log.error("用户同步任务执行异常", e);
            result.setMessage("同步任务执行异常：" + e.getMessage());
        } finally {
            // 释放锁
            RedisUtils.del(SYNC_TASK_LOCK_KEY);
        }

        return result;
    }

    /**
     * 生成唯一的userid：RPA + 时间戳（精确到毫秒）
     */
    private String generateUserId() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMddHHmmssSSS");
        String timestamp = sdf.format(new Date());
        // 添加随机数确保唯一性
        String random = String.format("%03d", new Random().nextInt(1000));
        return "RPA" + timestamp + random;
    }

    /**
     * 迁移结果
     */
    @Data
    public static class MigrateResult {
        private int successCount;
        private int failCount;
        private List<String> failedUsers = new ArrayList<>();
        private String message;
    }

    /**
     * 指定租户用户迁移到个人空间
     *
     * @param managementClient 管理客户端
     * @param tenantId 租户ID
     * @param loginNames 可选，指定要迁移的账号列表，为空则迁移该租户下所有用户
     * @return 迁移结果
     */
    public MigrateResult migrateTenantUsers(
            ManagementClient managementClient, String tenantId, List<String> loginNames) {
        MigrateResult result = new MigrateResult();
        try {
            if (StringUtils.isBlank(tenantId)) {
                result.setMessage("租户ID不能为空");
                return result;
            }

            log.info("开始执行租户用户迁移，租户ID：{}，指定账号列表：{}", tenantId, loginNames);

            List<UapUser> users = fetchAllTenantUsers(tenantId);

            // 如果指定了账号列表，则过滤
            if (CollectionUtil.isNotEmpty(loginNames)) {
                users = users.stream()
                        .filter(user -> user != null && loginNames.contains(user.getLoginName()))
                        .collect(Collectors.toList());
            }

            if (CollectionUtil.isEmpty(users)) {
                result.setMessage("未找到需要迁移的用户");
                return result;
            }

            List<String> userIds = users.stream()
                    .map(UapUser::getId)
                    .filter(StringUtils::isNotBlank)
                    .collect(Collectors.toList());
            if (CollectionUtil.isEmpty(userIds)) {
                result.setMessage("未获取到有效的用户ID");
                return result;
            }

            // 将用户标记为资源池用户
            userDao.batchUpdateUserType(userIds, 3, databaseName);

            // 如果name为空，则更新为login_name
            userDao.batchUpdateNameFromLoginName(userIds, databaseName);

            // 获取注册角色ID
            String registerRoleId = roleDao.getRoleIdByName(databaseName, "注册角色");
            if (StringUtils.isBlank(registerRoleId)) {
                log.warn("未找到【注册角色】，使用默认角色ID: 1");
                registerRoleId = "1";
            }

            int successCount = 0;
            List<String> failedUsers = new ArrayList<>();
            int totalCount = users.size();
            int processedCount = 0;

            log.info("开始迁移用户，总用户数：{}", totalCount);

            for (UapUser user : users) {
                processedCount++;
                // 每处理10个用户或处理完成时打印进度
                if (processedCount % 10 == 0 || processedCount == totalCount) {
                    log.info(
                            "用户迁移进度：{}/{} ({}%)，成功：{}，失败：{}",
                            processedCount,
                            totalCount,
                            String.format("%.1f", (processedCount * 100.0 / totalCount)),
                            successCount,
                            failedUsers.size());
                }

                if (user == null || StringUtils.isAnyBlank(user.getId(), user.getLoginName())) {
                    continue;
                }
                try {
                    unbindRegisterTenantByDb(tenantId, user.getId());
                    String personalTenantId = userService.createPersonalTenantAndBindRpa(
                            user.getId(), user.getLoginName(), managementClient);

                    // 确保 t_uap_tenant_role 表中有记录
                    ensureTenantRoleRelation(personalTenantId, registerRoleId);

                    // 租户绑定用户、角色
                    BindRoleDto bindRoleDto = new BindRoleDto();
                    bindRoleDto.setRoleIdList(Collections.singletonList(personalTenantId));
                    bindRoleDto.setUserId(user.getId());
                    ClientManagementAPI.bindUserRole(personalTenantId, bindRoleDto);

                    // 确保数据库表中有相关记录
                    ensureTenantAndUserRoleRelations(personalTenantId, user.getId(), registerRoleId);

                    // 刷新业务数据：更新相关表的 tenant_id
                    refreshBusinessData(tenantId, personalTenantId, user.getId());
                    successCount++;
                } catch (Exception ex) {
                    log.error("迁移用户失败，userId={}, loginName={}", user.getId(), user.getLoginName(), ex);
                    failedUsers.add(user.getLoginName());
                }
            }

            result.setSuccessCount(successCount);
            result.setFailCount(failedUsers.size());
            result.setFailedUsers(failedUsers);

            if (CollectionUtil.isNotEmpty(failedUsers)) {
                result.setMessage(String.format(
                        "迁移完成，成功%d个，失败%d个：%s", successCount, failedUsers.size(), String.join(",", failedUsers)));
            } else {
                result.setMessage(String.format("迁移完成，成功%d个用户", successCount));
            }

            log.info("历史注册账号租户迁移完成：{}", result.getMessage());
            return result;
        } catch (Exception e) {
            log.error("历史注册账号租户迁移失败", e);
            result.setMessage("迁移失败：" + e.getMessage());
            return result;
        }
    }

    private String findRegisterTenantId() {
        ListTenantDto listTenantDto = new ListTenantDto();
        listTenantDto.setName("注册租户");
        listTenantDto.setPageNum(1);
        listTenantDto.setPageSize(20);
        PageDto<UapTenant> tenantPage = ClientManagementAPI.queryTenantPageList(listTenantDto);
        if (tenantPage == null || CollectionUtil.isEmpty(tenantPage.getResult())) {
            log.warn("未在UAP中找到名称为【注册租户】的租户");
            return null;
        }
        return tenantPage.getResult().stream()
                .filter(tenant -> tenant != null && "注册租户".equals(tenant.getName()))
                .map(UapTenant::getId)
                .findFirst()
                .orElse(null);
    }

    private List<UapUser> fetchAllTenantUsers(String tenantId) {
        List<UapUser> result = new ArrayList<>();
        int pageNum = 1;
        int pageSize = 100;
        long totalCount = Long.MAX_VALUE;
        while ((long) (pageNum - 1) * pageSize < totalCount) {
            ListUserDto listUserDto = new ListUserDto();
            listUserDto.setPageNum(pageNum);
            listUserDto.setPageSize(pageSize);
            PageDto<UapUser> userPage = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);
            if (userPage == null || CollectionUtil.isEmpty(userPage.getResult())) {
                break;
            }
            result.addAll(userPage.getResult());
            totalCount = userPage.getTotalCount();
            pageNum++;
        }
        return result;
    }

    /**
     * 确保租户角色关联和用户角色关联在数据库中存在
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @param roleId 角色ID
     */
    private void ensureTenantAndUserRoleRelations(String tenantId, String userId, String roleId) {

        // 确保 t_uap_user_role 表中有记录
        ensureUserRoleRelation(tenantId, userId, roleId);
    }

    /**
     * 确保租户角色关联存在，不存在则插入
     * @param tenantId 租户ID
     * @param roleId 角色ID
     */
    private void ensureTenantRoleRelation(String tenantId, String roleId) {
        Integer existsCount = roleDao.checkTenantRoleExists(databaseName, tenantId, roleId);
        if (existsCount == null || existsCount == 0) {
            roleDao.insertTenantRole(databaseName, tenantId, roleId);
            log.info("已插入租户角色关联，租户ID: {}, 角色ID: {}", tenantId, roleId);
        } else {
            log.debug("租户角色关联已存在，租户ID: {}, 角色ID: {}", tenantId, roleId);
        }
    }

    /**
     * 确保用户角色关联存在
     * 由于数据库有 user_id 和 role_id 的唯一性约束：
     * - 如果存在 user_id 和 role_id 的记录，则更新 tenant_id
     * - 如果不存在，则插入新记录
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @param roleId 角色ID
     */
    private void ensureUserRoleRelation(String tenantId, String userId, String roleId) {
        // 检查是否存在 user_id 和 role_id 的记录（不考虑 tenant_id）
        Integer existsCount = roleDao.checkUserRoleExistsByUserAndRole(databaseName, userId, roleId);
        if (existsCount != null && existsCount > 0) {
            // 如果存在，更新 tenant_id
            int updated = roleDao.updateUserRoleTenant(databaseName, userId, roleId, tenantId);
            if (updated > 0) {
                log.info("已更新用户角色关联的租户ID，租户ID: {}, 用户ID: {}, 角色ID: {}", tenantId, userId, roleId);
            } else {
                log.warn("更新用户角色关联的租户ID失败，租户ID: {}, 用户ID: {}, 角色ID: {}", tenantId, userId, roleId);
            }
        } else {
            // 如果不存在，插入新记录
            roleDao.insertUserRole(databaseName, tenantId, userId, roleId);
            log.info("已插入用户角色关联，租户ID: {}, 用户ID: {}, 角色ID: {}", tenantId, userId, roleId);
        }
    }

    private void unbindRegisterTenantByDb(String tenantId, String userId) {
        Integer affected = tenantDao.deleteTenantUser(databaseName, tenantId, userId);
        if (affected == null || affected == 0) {
            throw new RuntimeException("解绑注册租户失败：未找到对应租户用户记录");
        }
    }

    /**
     * 刷新业务数据：更新相关表的 tenant_id
     * @param oldTenantId 旧租户ID（注册租户）
     * @param newTenantId 新租户ID（个人租户）
     * @param userId 用户ID
     */
    public void refreshBusinessData(String oldTenantId, String newTenantId, String userId) {
        try {
            // 获取业务数据库名称（优先使用配置，其次从DataSource URL解析，最后从JDBC连接获取）
            String dbName = getBusinessDatabaseName();
            if (StringUtils.isBlank(dbName)) {
                log.warn("无法获取业务数据库名称，跳过业务数据刷新");
                return;
            }

            // 查询同时包含 tenant_id 和 creator_id 字段的表（排除 t_uap 开头的表）
            List<String> tables = tenantDao.getTablesWithTenantId(dbName);
            if (CollectionUtil.isEmpty(tables)) {
                log.info("未找到同时包含 tenant_id 和 creator_id 字段的业务表");
                return;
            }

            log.info("开始刷新业务数据，数据库：{}，涉及表数量：{}", dbName, tables.size());
            int totalUpdated = 0;

            // 特殊处理 robot_execute_record 表：先查询id，再根据id更新（优化大数据量表的更新性能）
            String robotExecuteRecordTable = "robot_execute_record";
            boolean isRobotExecuteRecordProcessed = false;
            if (tables.contains(robotExecuteRecordTable)) {
                try {
                    // 先查询符合条件的记录ID
                    List<Long> recordIds = tenantDao.queryRobotExecuteRecordIds(dbName, oldTenantId, userId);
                    if (CollectionUtil.isNotEmpty(recordIds)) {
                        log.debug("表 {} 查询到 {} 条符合条件的记录，开始批量更新", robotExecuteRecordTable, recordIds.size());
                        // 根据ID列表批量更新
                        Integer updated =
                                tenantDao.updateRobotExecuteRecordTenantIdByIds(dbName, newTenantId, recordIds);
                        if (updated != null && updated > 0) {
                            totalUpdated += updated;
                            log.info("表 {} 更新了 {} 条记录（通过ID批量更新）", robotExecuteRecordTable, updated);
                        }
                    }
                    isRobotExecuteRecordProcessed = true;
                } catch (Exception e) {
                    log.warn("更新表 {} 的 tenant_id 失败：{}", robotExecuteRecordTable, e.getMessage());
                    isRobotExecuteRecordProcessed = true;
                }
            }

            // 处理其他表
            for (String tableName : tables) {
                // 跳过已处理的 robot_execute_record 表
                if (robotExecuteRecordTable.equals(tableName) && isRobotExecuteRecordProcessed) {
                    continue;
                }
                try {
                    Integer updated =
                            tenantDao.updateTableTenantId(dbName, tableName, oldTenantId, newTenantId, userId);
                    if (updated != null && updated > 0) {
                        totalUpdated += updated;
                        log.info("表 {} 更新了 {} 条记录", tableName, updated);
                    }
                } catch (Exception e) {
                    // 某些表可能没有 creator_id 字段，记录警告但不中断流程
                    log.warn("更新表 {} 的 tenant_id 失败：{}", tableName, e.getMessage());
                }
            }
            log.info("业务数据刷新完成，共更新 {} 条记录", totalUpdated);
        } catch (Exception e) {
            log.error("刷新业务数据失败", e);
            // 业务数据刷新失败不影响主流程，只记录日志
        }
    }

    /**
     * 获取业务数据库名称
     * 优先级：
     *         2. 从 DataSource URL 中解析
     *         3. 从 JDBC 连接中获取当前数据库名称
     * @return 业务数据库名称
     */
    private String getBusinessDatabaseName() {

        // 方式2：从 DataSource URL 中解析数据库名称
        String dbName = extractDatabaseNameFromUrl();
        if (StringUtils.isNotBlank(dbName)) {
            log.info("从 DataSource URL 解析出业务数据库名称：{}", dbName);
            return dbName;
        }

        // 方式3：从 JDBC 连接中获取当前数据库名称
        dbName = getDatabaseNameFromConnection();
        if (StringUtils.isNotBlank(dbName)) {
            log.info("从 JDBC 连接获取业务数据库名称：{}", dbName);
            return dbName;
        }

        return null;
    }

    /**
     * 从 DataSource URL 中解析数据库名称
     * 支持格式：jdbc:mysql://host:port/database?params
     */
    private String extractDatabaseNameFromUrl() {
        try {
            String url = null;

            // 尝试从 Environment 中获取
            if (environment != null) {
                url = environment.getProperty("spring.datasource.url");
            }

            // 如果 Environment 中没有，尝试从 DataSource 获取
            if (StringUtils.isBlank(url) && dataSource != null) {
                // 对于 DruidDataSource，可以通过 getUrl() 方法获取
                try {
                    java.lang.reflect.Method getUrlMethod =
                            dataSource.getClass().getMethod("getUrl");
                    url = (String) getUrlMethod.invoke(dataSource);
                } catch (Exception e) {
                    // 如果不是 DruidDataSource 或方法不存在，忽略
                }
            }

            if (StringUtils.isBlank(url)) {
                return null;
            }

            // 解析 MySQL JDBC URL: jdbc:mysql://host:port/database?params
            // 或者: jdbc:mysql://host:port/database
            Pattern pattern = Pattern.compile("jdbc:mysql://[^/]+/([^?]+)");
            Matcher matcher = pattern.matcher(url);
            if (matcher.find()) {
                return matcher.group(1);
            }
        } catch (Exception e) {
            log.warn("从 DataSource URL 解析数据库名称失败", e);
        }
        return null;
    }

    /**
     * 从 JDBC 连接中获取当前数据库名称
     */
    private String getDatabaseNameFromConnection() {
        if (dataSource == null) {
            return null;
        }

        try (Connection connection = dataSource.getConnection()) {
            // MySQL: SELECT DATABASE()
            try (java.sql.Statement stmt = connection.createStatement();
                    java.sql.ResultSet rs = stmt.executeQuery("SELECT DATABASE()")) {
                if (rs.next()) {
                    return rs.getString(1);
                }
            }
        } catch (Exception e) {
            log.warn("从 JDBC 连接获取数据库名称失败", e);
        }
        return null;
    }
}
