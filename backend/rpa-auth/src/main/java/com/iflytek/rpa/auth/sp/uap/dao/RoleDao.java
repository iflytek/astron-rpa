package com.iflytek.rpa.auth.sp.uap.dao;

import com.iflytek.rpa.auth.core.entity.AppInfoBo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface RoleDao {
    Integer getUnspecifiedRoleWithTenant(String databaseName, String tenantId);

    AppInfoBo selectAppInfo(String databaseName);

    Integer insertUnspecifiedRole(
            @Param("databaseName") String databaseName, @Param("appId") String appId, @Param("appName") String appName);

    void insertUnspecifiedTenantBind(@Param("databaseName") String databaseName, @Param("tenantId") String tenantId);

    Integer getUnspecifiedRole(@Param("databaseName") String databaseName);

    /**
     * 查询指定角色下的用户ID列表
     * @param databaseName 数据库名
     * @param roleId 角色ID
     * @param tenantId 租户ID
     * @return 用户ID列表
     */
    List<String> getUserIdsByRoleId(
            @Param("databaseName") String databaseName,
            @Param("roleId") String roleId,
            @Param("tenantId") String tenantId);

    /**
     * 将指定用户列表的角色迁移到"未指定"角色
     * @param databaseName 数据库名
     * @param userIds 用户ID列表
     * @param tenantId 租户ID
     */
    void migrateUsersToUnspecifiedRole(
            @Param("databaseName") String databaseName,
            @Param("userIds") List<String> userIds,
            @Param("tenantId") String tenantId);

    List<String> getBindUnspecifiedRoleIds(
            @Param("userIds") List<String> userIds,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    void batchDeleteUnspecifiedRoleBind(@Param("ids") List<String> ids, @Param("databaseName") String databaseName);

    /**
     * 根据角色名称查询角色ID
     * @param databaseName 数据库名
     * @param roleName 角色名称
     * @return 角色ID
     */
    String getRoleIdByName(@Param("databaseName") String databaseName, @Param("roleName") String roleName);

    /**
     * 检查租户角色关联是否存在
     * @param databaseName 数据库名
     * @param tenantId 租户ID
     * @param roleId 角色ID
     * @return 关联数量
     */
    Integer checkTenantRoleExists(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("roleId") String roleId);

    /**
     * 插入租户角色关联
     * @param databaseName 数据库名
     * @param tenantId 租户ID
     * @param roleId 角色ID
     */
    void insertTenantRole(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("roleId") String roleId);

    /**
     * 将用户角色记录的租户ID更新为指定租户
     * @param databaseName 数据库名
     * @param userId 用户ID
     * @param roleId 角色ID
     * @param tenantId 目标租户ID
     * @return 受影响行数
     */
    int updateUserRoleTenant(
            @Param("databaseName") String databaseName,
            @Param("userId") String userId,
            @Param("roleId") String roleId,
            @Param("tenantId") String tenantId);

    /**
     * 检查用户角色关联是否存在（检查 tenant_id、user_id、role_id）
     * @param databaseName 数据库名
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @param roleId 角色ID
     * @return 关联数量
     */
    Integer checkUserRoleExists(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("roleId") String roleId);

    /**
     * 检查用户角色关联是否存在（仅检查 user_id、role_id，不考虑 tenant_id）
     * @param databaseName 数据库名
     * @param userId 用户ID
     * @param roleId 角色ID
     * @return 关联数量
     */
    Integer checkUserRoleExistsByUserAndRole(
            @Param("databaseName") String databaseName, @Param("userId") String userId, @Param("roleId") String roleId);

    /**
     * 插入用户角色关联
     * @param databaseName 数据库名
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @param roleId 角色ID
     */
    void insertUserRole(
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("roleId") String roleId);
}
