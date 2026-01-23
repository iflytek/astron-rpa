package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * 用户服务
 */
public interface UserService {

    /**
     * 注册
     * @param registerDto 注册信息
     * @param request HTTP请求
     * @return 租户ID
     */
    AppResponse<String> register(RegisterDto registerDto, HttpServletRequest request) throws IOException;

    /**
     * 按名称模糊搜索所有员工或部门
     * @param name 名称
     * @param request HTTP请求
     * @return 部门或用户信息
     */
    AppResponse<GetDeptOrUserDto> searchDeptOrUser(String name, HttpServletRequest request);

    /**
     * 编辑员工
     * @param updateUapUserDto 更新用户信息
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> editUser(UpdateUapUserDto updateUapUserDto, HttpServletRequest request) throws IOException;

    /**
     * 新增员工
     * @param createUapUserDto 创建用户信息
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> addUser(CreateUapUserDto createUapUserDto, HttpServletRequest request) throws IOException;

    /**
     * 分页查询当前机构的用户
     * @param listUserDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    AppResponse<PageDto<DeptUserDto>> queryUserListByOrgId(ListUserDto listUserDto, HttpServletRequest request)
            throws IOException;

    /**
     * 角色管理-根据部门id查询部门下的人员和子部门
     * @param id 部门ID
     * @param request HTTP请求
     * @return 部门用户列表
     */
    AppResponse<List<CurrentDeptUserDto>> queryUserAndDept(String id, HttpServletRequest request);

    /**
     * 角色管理-根据名字或手机号模糊查询员工
     * @param keyWord 关键字
     * @param request HTTP请求
     * @return 用户列表
     */
    AppResponse<List<CurrentDeptUserDto>> searchUserWithStatus(String keyWord, HttpServletRequest request)
            throws IOException;

    /**
     * 角色管理-添加成员
     * @param bindUserListDto 绑定用户列表DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> bindUserListRole(BindUserListDto bindUserListDto, HttpServletRequest request)
            throws IOException;

    /**
     * 人员解绑角色
     * @param bindRoleDto 绑定角色DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> unbindRole(BindRoleDto bindRoleDto, HttpServletRequest request) throws IOException;

    /**
     * 分页获取角色绑定的用户列表，可根据登录名或姓名模糊查询
     * @param listUserByRoleDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    AppResponse<PageDto<User>> queryBindListByRole(ListUserByRoleDto listUserByRoleDto, HttpServletRequest request)
            throws IOException;

    /**
     * 获取当前登录用户
     * @param request HTTP请求
     * @return 当前登录用户信息
     */
    AppResponse<User> getCurrentLoginUser(HttpServletRequest request);

    /**
     * 获取当前登录用户ID
     * @param request HTTP请求
     * @return 当前登录用户ID
     */
    AppResponse<String> getCurrentUserId(HttpServletRequest request);

    /**
     * 获取当前登录用户名
     * @param request HTTP请求
     * @return 当前登录用户名
     */
    AppResponse<String> getCurrentLoginUsername(HttpServletRequest request);

    /**
     * 根据用户ID查询登录名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 登录名
     */
    AppResponse<String> getLoginNameById(String id, HttpServletRequest request);

    /**
     * 根据用户ID查询姓名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户姓名
     */
    AppResponse<String> getRealNameById(String id, HttpServletRequest request);

    /**
     * 根据用户ID查询用户信息
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户信息
     */
    AppResponse<User> getUserInfoById(String id, HttpServletRequest request);

    /**
     * 根据手机号查询用户姓名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户姓名
     */
    AppResponse<String> getRealNameByPhone(String phone, HttpServletRequest request);

    /**
     * 根据手机号查询登录名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 登录名
     */
    AppResponse<String> getLoginNameByPhone(String phone, HttpServletRequest request);

    /**
     * 判断是否历史用户（ext_info = 1 表示历史用户）
     * @param phone 手机号
     * @return 是否历史用户
     */
    AppResponse<Boolean> isHistoryUser(String phone);

    /**
     * 根据手机号查询用户信息
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户信息
     */
    AppResponse<User> getUserInfoByPhone(String phone, HttpServletRequest request);

    /**
     * 根据用户ID列表查询用户信息列表（最多支持100个id）
     * @param userIdList 用户ID列表
     * @param request HTTP请求
     * @return 用户信息列表
     */
    AppResponse<List<User>> queryUserListByIds(List<String> userIdList, HttpServletRequest request);

    /**
     * 根据姓名模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    AppResponse<List<User>> searchUserByName(String keyword, String deptId, HttpServletRequest request);

    /**
     * 根据手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    AppResponse<List<User>> searchUserByPhone(String keyword, String deptId, HttpServletRequest request);

    /**
     * 根据姓名或手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    AppResponse<List<User>> searchUserByNameOrPhone(String keyword, String deptId, HttpServletRequest request);

    /**
     * 查询当前登录的用户信息
     * @param request HTTP请求
     * @return 用户信息
     */
    AppResponse<User> getUserInfo(HttpServletRequest request);

    /**
     * 退出登录
     * @param request HTTP请求
     * @param response HTTP响应
     * @return 操作结果
     */
    AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) throws IOException;

    /**
     * 变更部门
     * @param userChangeDeptDto 变更部门DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> changeDept(UserChangeDeptDto userChangeDeptDto, HttpServletRequest request);

    /**
     * 删除员工
     * @param userDeleteDto 删除员工DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> deleteUser(UserDeleteDto userDeleteDto, HttpServletRequest request) throws IOException;

    /**
     * 启用/禁用员工
     * @param userEnableDto 启用/禁用DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> enableUser(UserEnableDto userEnableDto, HttpServletRequest request);

    /**
     * 查询当前机构的全部用户(部门新增，部门负责人下拉框)
     * @param orgId 部门ID
     * @param request HTTP请求
     * @return 用户列表
     */
    AppResponse<List<User>> queryUserDetailListByOrgId(String orgId, HttpServletRequest request) throws IOException;

    /**
     * 按名称或手机号模糊搜索所有员工（用于机器人看板所有者下拉）
     * @param keyword 关键字（姓名或手机号）
     * @param deptId 部门ID
     * @return 用户搜索结果列表
     */
    AppResponse<List<UserSearchDto>> getUserByNameOrPhone(String keyword, String deptId, HttpServletRequest request);

    /**
     * 获取用户详细信息（包含扩展信息等）
     * @param tenantId 租户ID
     * @param getUserDto 查询参数
     * @param request HTTP请求
     * @return 用户扩展信息
     */
    AppResponse<UserExtendDto> queryUserExtendInfo(String tenantId, GetUserDto getUserDto, HttpServletRequest request)
            throws IOException;

    /**
     * 获取当前用户权限列表
     * @param request HTTP请求
     * @return 用户列表
     */
    AppResponse<List<Permission>> getCurrentUserPermissionList(HttpServletRequest request) throws IOException;

    /**
     * 获取Casdoor登录重定向URL（Casdoor专用）
     * @param request HTTP请求
     * @return 登录重定向URL
     */
    AppResponse<String> getRedirectUrl(HttpServletRequest request);

    /**
     * Casdoor OAuth登录（Casdoor专用）
     * @param code OAuth授权码
     * @param state OAuth state参数
     * @param request HTTP请求
     * @return 用户信息
     */
    AppResponse<User> signIn(String code, String state, HttpServletRequest request) throws IOException;

    /**
     * 检查用户登录状态（Casdoor专用）
     * @param request HTTP请求
     * @return 用户信息，如果未登录返回错误
     */
    AppResponse<User> checkLoginStatus(HttpServletRequest request);

    /**
     * 刷新服务端token（Casdoor专用，当accessToken过期时使用）
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> refreshToken(HttpServletRequest request);

    /**
     * 获取当前登录用户的权益
     * 根据session查询租户code，判断如果是企业租户，则查询数据库中权益
     * 如果没有数据，默认拥有所有权益
     *
     * @param request HTTP请求
     * @return 用户权益信息
     */
    AppResponse<UserEntitlementDto> getCurrentUserEntitlement(HttpServletRequest request);

    AppResponse<String> getNameById(String id, HttpServletRequest request);

    /**
     * 获取已部署用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 已部署用户分页列表
     */
    AppResponse<PageDto<RobotExecute>> getDeployedUserList(GetDeployedUserListDto dto, HttpServletRequest request);

    /**
     * 获取未部署用户列表
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 未部署用户列表
     */
    AppResponse<List<MarketDto>> getUserUnDeployed(GetUserUnDeployedDto dto, HttpServletRequest request);

    /**
     * 获取市场用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 市场用户分页列表
     */
    AppResponse<PageDto<MarketDto>> getMarketUserList(GetMarketUserListDto dto, HttpServletRequest request);

    /**
     * 获取公共市场用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 公共市场用户分页列表
     */
    AppResponse<PageDto<MarketDto>> getMarketUserListByPublic(
            GetMarketUserListByPublicDto dto, HttpServletRequest request);

    /**
     * 根据手机号查询市场用户（不在市场中的用户）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 用户列表
     */
    AppResponse<List<MarketDto>> getMarketUserByPhone(GetMarketUserByPhoneDto dto, HttpServletRequest request);

    /**
     * 根据手机号查询市场中的用户（用于市场所有者，排除自己）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 用户列表
     */
    AppResponse<List<MarketDto>> getMarketUserByPhoneForOwner(
            GetMarketUserByPhoneForOwnerDto dto, HttpServletRequest request);

    /**
     * 根据用户ID列表查询租户用户列表
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 租户用户列表
     */
    AppResponse<List<TenantUser>> getMarketTenantUserList(GetMarketTenantUserListDto dto, HttpServletRequest request);

    AppResponse<PageDto<RobotExecute>> getDeployedUserListWithoutTenantId(
            GetDeployedUserListDto dto, HttpServletRequest request);
}
