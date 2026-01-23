package com.iflytek.rpa.auth.sp.uap.dao;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.auth.core.entity.GetDeployedUserListDto;
import com.iflytek.rpa.auth.core.entity.RobotExecute;
import com.iflytek.rpa.auth.sp.uap.entity.SyncUserInfo;
import com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserDao {
    List<UapUser> queryUapUserByIds(
            @Param("userIds") List<String> userIds,
            @Param("databaseName") String databaseName,
            @Param("tenantId") String tenantId);

    IPage<String> queryUserIdsByRole(
            IPage page,
            @Param("listUserByRoleDto") ListUserByRoleDto listUserByRoleDto,
            @Param("databaseName") String databaseName);

    List<UapUser> queryUapUserByName(
            @Param("userName") String userName,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    /**
     * 更新用户的第三方扩展信息
     * @param loginName 登录名
     * @param thirdExtInfo 第三方扩展信息
     * @param databaseName 数据库名
     */
    void updateThirdExtInfo(
            @Param("loginName") String loginName,
            @Param("thirdExtInfo") String thirdExtInfo,
            @Param("databaseName") String databaseName);

    /**
     * 更新用户的扩展标识字段 ext_info
     * @param phone 手机号
     * @param extInfo 扩展标识
     * @param databaseName 数据库名
     */
    void updateExtInfo(
            @Param("phone") String phone, @Param("extInfo") String extInfo, @Param("databaseName") String databaseName);

    /**
     * 根据手机号查询用户的第三方扩展信息
     * @param phone 手机号
     * @param databaseName 数据库名
     * @return 第三方扩展信息
     */
    String queryThirdExtInfoByPhone(@Param("phone") String phone, @Param("databaseName") String databaseName);

    /**
     * 根据手机号查询用户的扩展标识 ext_info
     * @param phone 手机号
     * @param databaseName 数据库名
     * @return 扩展标识
     */
    String queryExtInfoByPhone(@Param("phone") String phone, @Param("databaseName") String databaseName);

    /**
     * 根据手机号查询用户的登录名
     * @param phone 手机号
     * @param databaseName 数据库名
     * @return 登录名
     */
    String queryLoginNameByPhone(@Param("phone") String phone, @Param("databaseName") String databaseName);

    /**
     * 根据登录名查询手机号
     * @param loginName 登录名
     * @param databaseName 数据库名
     * @return 手机号
     */
    String queryPhoneByLoginName(@Param("loginName") String loginName, @Param("databaseName") String databaseName);

    /**
     * 查询需要同步到讯飞账号的用户（手机号不为空且third_ext_info为空）
     * @param databaseName 数据库名
     * @param loginNames 可选，指定要同步的用户登录名列表，为空则查询所有符合条件的用户
     * @return 用户列表
     */
    List<SyncUserInfo> queryUsersToSync(
            @Param("databaseName") String databaseName, @Param("loginNames") List<String> loginNames);

    /**
     * 根据手机号查询用户ID
     * @param phone 手机号
     * @param databaseName 数据库名
     * @return 用户ID
     */
    String getUserIdByPhone(@Param("phone") String phone, @Param("databaseName") String databaseName);

    /**
     * 批量更新用户类型
     * @param userIds 用户ID列表
     * @param userType 用户类型
     * @param databaseName 数据库名
     */
    void batchUpdateUserType(
            @Param("userIds") List<String> userIds,
            @Param("userType") Integer userType,
            @Param("databaseName") String databaseName);

    /**
     * 批量更新用户名称：如果name为空，则更新为login_name
     * @param userIds 用户ID列表
     * @param databaseName 数据库名
     */
    void batchUpdateNameFromLoginName(
            @Param("userIds") List<String> userIds, @Param("databaseName") String databaseName);

    String getNameById(String id, String databaseName);

    /**
     * 获取已部署用户列表（分页）
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 已部署用户分页列表
     */
    IPage<RobotExecute> getDeployedUserList(
            IPage page, @Param("dto") GetDeployedUserListDto dto, @Param("databaseName") String databaseName);

    /**
     * 获取未部署用户列表
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 未部署用户列表
     */
    List<com.iflytek.rpa.auth.core.entity.MarketDto> getUserUnDeployed(
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetUserUnDeployedDto dto,
            @Param("databaseName") String databaseName);

    /**
     * 获取市场用户列表（分页）
     * @param page 分页对象
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 市场用户分页列表
     */
    IPage<com.iflytek.rpa.auth.core.entity.MarketDto> getMarketUserList(
            IPage page,
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetMarketUserListDto dto,
            @Param("databaseName") String databaseName);

    /**
     * 获取公共市场用户列表（分页）
     * @param page 分页对象
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 公共市场用户分页列表
     */
    IPage<com.iflytek.rpa.auth.core.entity.MarketDto> getMarketUserListByPublic(
            IPage page,
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetMarketUserListByPublicDto dto,
            @Param("databaseName") String databaseName);

    /**
     * 根据手机号查询市场用户（不在市场中的用户）
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 用户列表
     */
    List<com.iflytek.rpa.auth.core.entity.MarketDto> getMarketUserByPhone(
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetMarketUserByPhoneDto dto,
            @Param("databaseName") String databaseName);

    /**
     * 根据手机号查询市场中的用户（用于市场所有者，排除自己）
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 用户列表
     */
    List<com.iflytek.rpa.auth.core.entity.MarketDto> getMarketUserByPhoneForOwner(
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetMarketUserByPhoneForOwnerDto dto,
            @Param("databaseName") String databaseName);

    /**
     * 根据用户ID列表查询租户用户列表
     * @param dto 查询条件
     * @param databaseName 数据库名
     * @return 租户用户列表
     */
    List<com.iflytek.rpa.auth.core.entity.TenantUser> getMarketTenantUserList(
            @Param("dto") com.iflytek.rpa.auth.core.entity.GetMarketTenantUserListDto dto,
            @Param("databaseName") String databaseName);

    UapUser getUserById(String id, String databaseName);

    IPage<RobotExecute> getDeployedUserListWithoutTenantId(
            Page<RobotExecute> page, GetDeployedUserListDto dto, String databaseName);
}
