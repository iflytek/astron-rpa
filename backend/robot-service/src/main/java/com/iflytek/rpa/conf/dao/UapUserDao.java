package com.iflytek.rpa.conf.dao;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * UAP用户数据访问层
 */
@Mapper
public interface UapUserDao {

    /**
     * 插入用户
     * @param databaseName 数据库名
     * @param userId 用户ID
     * @param loginName 登录名（手机号）
     * @param password 密码
     * @param phone 手机号
     * @return 影响行数
     */
    int insertUser(
            @Param("databaseName") String databaseName,
            @Param("userId") String userId,
            @Param("loginName") String loginName,
            @Param("password") String password,
            @Param("phone") String phone);

    /**
     * 插入租户用户关系
     * @param databaseName 数据库名
     * @param tenantUserId 租户用户关系ID
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @return 影响行数
     */
    int insertTenantUser(
            @Param("databaseName") String databaseName,
            @Param("tenantUserId") String tenantUserId,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId);

    int insertRoleUser(
            @Param("databaseName") String databaseName,
            @Param("roleUserId") String roleUserId,
            @Param("roleId") String roleId,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId);

    /**
     * 根据登录名或手机号查询用户是否存在
     * @param databaseName 数据库名
     * @param loginName 登录名（手机号）
     * @param phone 手机号
     * @return 用户数量
     */
    int countUserByLoginNameOrPhone(
            @Param("databaseName") String databaseName,
            @Param("loginName") String loginName,
            @Param("phone") String phone);

    /**
     * 根据配置字段名查询配置值
     * @param databaseName 数据库名
     * @param fieldName 配置字段名
     * @return 配置值
     */
    String getConfigValue(@Param("databaseName") String databaseName, @Param("fieldName") String fieldName);

    /**
     * 根据登录名或手机号查询用户ID
     * @param databaseName 数据库名
     * @param loginName 登录名（手机号）
     * @param phone 手机号
     * @return 用户ID
     */
    String getUserIdByLoginNameOrPhone(
            @Param("databaseName") String databaseName,
            @Param("loginName") String loginName,
            @Param("phone") String phone);
}
