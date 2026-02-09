package com.iflytek.rpa.auth.sp.casdoor.dao;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.auth.core.entity.GetMarketUserByPhoneDto;
import com.iflytek.rpa.auth.core.entity.GetMarketUserListDto;
import com.iflytek.rpa.auth.core.entity.MarketDto;
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
     * 获取市场用户列表（分页）
     *
     * @param page 分页对象
     * @param dto 查询条件
     * @param databaseName 数据库名称
     * @return 市场用户分页列表
     */
    IPage<MarketDto> getMarketUserList(
            IPage<MarketDto> page, @Param("dto") GetMarketUserListDto dto, @Param("databaseName") String databaseName);

    /**
     * 根据手机号或姓名查询市场用户（排除已在团队内的用户）
     *
     * @param dto 查询条件（包含marketId和keyword）
     * @param databaseName 数据库名称
     * @return 市场用户列表
     */
    List<MarketDto> getMarketUserByPhone(
            @Param("dto") GetMarketUserByPhoneDto dto, @Param("databaseName") String databaseName);
}
