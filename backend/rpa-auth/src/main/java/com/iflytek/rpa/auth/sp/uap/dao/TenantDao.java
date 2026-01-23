package com.iflytek.rpa.auth.sp.uap.dao;

import com.iflytek.rpa.auth.core.entity.UserVo;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 租户相关数据访问
 */
@Mapper
public interface TenantDao {

    List<UserVo> getUserByTenantId(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("userName") String userName);

    List<String> getAllTenantId(@Param("databaseName") String databaseName);

    /**
     * 根据手机号查询用户所属的租户列表
     *
     * @param databaseName 数据库名称
     * @param phone 手机号
     * @return 租户列表
     */
    List<UapTenant> queryTenantListByPhone(@Param("databaseName") String databaseName, @Param("phone") String phone);

    String getTenantUserId(
            @Param("databaseName") String databaseName,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    Integer getTenantUserStatus(
            @Param("databaseName") String databaseName,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    Integer enableTenantUser(
            @Param("databaseName") String databaseName, @Param("id") String id, @Param("status") Integer status);

    Integer updateLoginTime(String databaseName, String id);

    List<String> getTenantUserIdsByType(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("tenantUserType") Integer tenantUserType);

    List<String> getNoClassifyTenantIds(@Param("databaseName") String databaseName);

    Integer updateTenantClassifyCompleted(
            @Param("databaseName") String databaseName, @Param("tenantIds") List<String> tenantIds);

    /**
     * 获取所有企业租户ID列表（租户代码以ep_或es_开头）
     * @param databaseName 数据库名
     * @return 企业租户ID列表
     */
    List<String> getAllEnterpriseTenantId(@Param("databaseName") String databaseName);

    /**
     * 获取租户用户类型（1表示租户管理员，其他表示普通用户）
     * @param databaseName 数据库名
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @return 租户用户类型（可能为null）
     */
    Integer getTenantUserType(
            @Param("databaseName") String databaseName,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    /**
     * 删除指定租户下的用户关联
     * @param databaseName 数据库名
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @return 受影响行数
     */
    Integer deleteTenantUser(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId);

    /**
     * 查询同时包含 tenant_id 和 creator_id 字段的表名（排除 t_uap 开头的表）
     * @param databaseName 数据库名
     * @return 表名列表
     */
    List<String> getTablesWithTenantId(@Param("databaseName") String databaseName);

    /**
     * 更新指定表的 tenant_id
     * @param databaseName 数据库名
     * @param tableName 表名
     * @param oldTenantId 旧租户ID
     * @param newTenantId 新租户ID
     * @param userId 用户ID（creator_id）
     * @return 受影响行数
     */
    Integer updateTableTenantId(
            @Param("databaseName") String databaseName,
            @Param("tableName") String tableName,
            @Param("oldTenantId") String oldTenantId,
            @Param("newTenantId") String newTenantId,
            @Param("userId") String userId);

    List<String> getAllTenantIdWithoutClassify(String databaseName);

    Integer updateTenantClassifyFlag(String databaseName, List<String> tenantIds);

    List<String> getManagerUserIds(String databaseName, String tenantId);

    List<String> getNormalUserIds(String databaseName, String tenantId);

    /**
     * 查询符合条件的租户用户（tenant_id不在指定列表中）
     * @param databaseName 数据库名
     * @param excludeTenantIds 排除的租户ID列表
     * @return 租户用户列表（包含userId和tenantId）
     */
    List<com.iflytek.rpa.auth.core.entity.TenantUser> queryTenantUsersForSync(
            @Param("databaseName") String databaseName, @Param("excludeTenantIds") List<String> excludeTenantIds);

    /**
     * 查询 robot_execute_record 表中符合条件的记录ID
     * @param databaseName 数据库名
     * @param oldTenantId 旧租户ID
     * @param userId 用户ID（creator_id）
     * @return 记录ID列表
     */
    List<Long> queryRobotExecuteRecordIds(
            @Param("databaseName") String databaseName,
            @Param("oldTenantId") String oldTenantId,
            @Param("userId") String userId);

    /**
     * 根据ID列表批量更新 robot_execute_record 表的 tenant_id
     * @param databaseName 数据库名
     * @param newTenantId 新租户ID
     * @param ids 记录ID列表
     * @return 受影响行数
     */
    Integer updateRobotExecuteRecordTenantIdByIds(
            @Param("databaseName") String databaseName,
            @Param("newTenantId") String newTenantId,
            @Param("ids") List<Long> ids);
}
