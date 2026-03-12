package com.iflytek.rpa.auth.sp.casdoor.dao;

import com.iflytek.rpa.auth.core.entity.GetMarketTenantUserListDto;
import com.iflytek.rpa.auth.core.entity.TenantUser;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.casbin.casdoor.entity.User;

/**
 * Casdoor 用户数据访问接口
 *
 * @author Auto Generated
 * @create 2025/12/11
 */
@Mapper
public interface CasdoorUserDao {

    /**
     * 根据姓名模糊查询用户
     *
     * @param keyword 关键字（姓名）
     * @param owner 租户ID（organization name）
     * @param databaseName 数据库名称
     * @return 用户列表
     */
    List<User> searchUserByName(
            @Param("keyword") String keyword, @Param("owner") String owner, @Param("databaseName") String databaseName);

    /**
     * 根据手机号模糊查询用户
     *
     * @param keyword 关键字（手机号）
     * @param owner 租户ID（organization name）
     * @param databaseName 数据库名称
     * @return 用户列表
     */
    List<User> searchUserByPhone(
            @Param("keyword") String keyword, @Param("owner") String owner, @Param("databaseName") String databaseName);

    /**
     * 根据姓名或手机号模糊查询用户
     *
     * @param keyword 关键字（姓名或手机号）
     * @param owner 租户ID（organization name）
     * @param databaseName 数据库名称
     * @return 用户列表
     */
    List<User> searchUserByNameOrPhone(
            @Param("keyword") String keyword, @Param("owner") String owner, @Param("databaseName") String databaseName);

    /**
     * 根据用户ID列表查询租户用户列表
     *
     * @param dto 查询条件（包含租户ID和用户ID列表）
     * @param databaseName 数据库名称
     * @return 租户用户列表
     */
    List<TenantUser> getMarketTenantUserList(
            @Param("dto") GetMarketTenantUserListDto dto, @Param("databaseName") String databaseName);
}
