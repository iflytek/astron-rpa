package com.iflytek.rpa.common.feign;

import com.iflytek.rpa.common.feign.entity.*;
import com.iflytek.rpa.common.feign.entity.dto.*;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import org.springframework.cloud.openfeign.FeignAutoConfiguration;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(
        name = "rpa-auth",
        url = "${auth.base-url:http://localhost:10251}",
        configuration = FeignAutoConfiguration.class)
public interface RpaAuthFeign {

    // ==================== UserController 用户相关接口 ====================

    /**
     * 获取当前登录用户信息
     * @return 用户信息
     */
    @GetMapping("/api/rpa-auth/user/info")
    AppResponse<User> getLoginUser();

    /**
     * 获取用户详细信息
     * @param tenantId
     * @param dto
     * @return
     */
    @PostMapping("/api/rpa-auth/user/getUserExtendInfo")
    AppResponse<UserExtendDto> getUserExtendInfo(
            @RequestParam("tenantId") String tenantId, @RequestBody GetUserDto dto);

    /**
     * 注册(Uap的注册接口，仅作兼容备用)
     * @param registerDto 注册DTO
     * @return 注册结果
     */
    @PostMapping("/api/rpa-auth/user/register")
    AppResponse<String> registerUap(@RequestBody Object registerDto);

    /**
     * 新增员工
     * @param createUapUserDto 创建用户DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/add")
    AppResponse<String> addUser(@RequestBody Object createUapUserDto);

    /**
     * 编辑员工
     * @param updateUapUserDto 更新用户DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/edit")
    AppResponse<String> editUser(@RequestBody Object updateUapUserDto);

    /**
     * 删除员工
     * @param userDto 用户删除DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/delete")
    AppResponse<String> deleteUser(@RequestBody Object userDto);

    /**
     * 启用/禁用员工
     * @param userDto 用户启用DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/enable")
    AppResponse<String> enableUser(@RequestBody Object userDto);

    /**
     * 变更部门
     * @param userDto 用户变更部门DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/changeDept")
    AppResponse<String> changeDept(@RequestBody Object userDto);

    /**
     * 查询当前机构的全部用户(部门新增，部门负责人下拉框)
     * @param orgId 部门ID
     * @return 用户列表
     */
    @GetMapping("/api/rpa-auth/user/queryAllListByOrgId")
    AppResponse<List<User>> queryUserDetailListByOrgId(@RequestParam("orgId") String orgId);

    /**
     * 分页查询当前机构的用户
     * @param listUserDto 查询用户DTO
     * @return 用户分页列表
     */
    @PostMapping("/api/rpa-auth/user/queryListByOrgId")
    AppResponse<PageDto<DeptUserDto>> queryUserListByOrgId(@RequestBody Object listUserDto);

    /**
     * 分页获取角色绑定的用户列表，可根据登录名或姓名模糊查询
     * @param listUserByRoleDto 查询用户DTO
     * @return 用户分页列表
     */
    @PostMapping("/api/rpa-auth/user/queryBindListByRole")
    AppResponse<PageDto<User>> queryBindListByRole(@RequestBody Object listUserByRoleDto);

    /**
     * 人员解绑角色
     * @param bindRoleDto 绑定角色DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/unbindRole")
    AppResponse<String> unbindRole(@RequestBody Object bindRoleDto);

    /**
     * 按名称模糊搜索所有员工或部门
     * @param name 名称
     * @return 搜索结果
     */
    @GetMapping("/api/rpa-auth/user/searchDeptOrUser")
    AppResponse<GetDeptOrUserDto> searchDeptOrUser(@RequestParam("name") String name);

    /**
     * 角色管理-根据部门id查询部门下的人员和子部门
     * @param id 部门ID
     * @return 部门和人员列表
     */
    @GetMapping("/api/rpa-auth/user/queryUserAndDept")
    AppResponse<List<CurrentDeptUserDto>> queryUserAndDept(@RequestParam("id") String id);

    /**
     * 角色管理-根据名字或手机号模糊查询员工
     * @param keyWord 关键字
     * @return 用户列表
     */
    @GetMapping("/api/rpa-auth/user/searchUserWithStatus")
    AppResponse<List<CurrentDeptUserDto>> searchUserWithStatus(@RequestParam("keyWord") String keyWord);

    /**
     * 角色管理-添加成员
     * @param bindUserListDto 绑定用户列表DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/user/batchBindRole")
    AppResponse<String> bindUserListRole(@RequestBody Object bindUserListDto);

    /**
     * 卓越中心-机器人看板-所有者下拉选择-查询接口
     * 根据输入的关键字（姓名或手机号）查询用户
     * @param keyword 关键字
     * @param deptId 部门ID
     * @return 用户列表
     */
    @PostMapping("/api/rpa-auth/user/getUserByNameOrPhone")
    AppResponse<List<User>> getUserByNameOrPhone(
            @RequestParam("keyword") String keyword, @RequestParam(value = "deptId", required = false) String deptId);

    /**
     * 获取当前登录用户
     * @return 当前登录用户信息
     */
    @GetMapping("/api/rpa-auth/user/current")
    AppResponse<User> getCurrentLoginUser();

    /**
     * 获取当前登录用户ID
     * @return 当前登录用户ID
     */
    @GetMapping("/api/rpa-auth/user/current/id")
    AppResponse<String> getCurrentUserId();

    /**
     * 获取当前登录用户名
     * @return 当前登录用户名
     */
    @GetMapping("/api/rpa-auth/user/current/username")
    AppResponse<String> getCurrentLoginUsername();

    /**
     * 根据用户ID查询登录名
     * @param id 用户ID
     * @return 登录名
     */
    @GetMapping("/api/rpa-auth/user/loginName")
    AppResponse<String> getLoginNameById(@RequestParam("id") String id);

    /**
     * 根据用户ID查询姓名
     * @param id 用户ID
     * @return 用户姓名
     */
    @GetMapping("/api/rpa-auth/user/realName")
    AppResponse<String> getRealNameById(@RequestParam("id") String id);

    /**
     * 根据ID获取用户姓名（无需租户信息）
     * @param id
     * @return
     */
    @GetMapping("/api/rpa-auth/user/getNameById")
    AppResponse<String> getNameById(@RequestParam("id") String id);

    /**
     * 获取已部署用户列表（分页）
     * @param dto 查询条件
     * @return 已部署用户分页列表
     */
    @PostMapping("/api/rpa-auth/user/getDeployedUserList")
    AppResponse<PageDto<RobotExecute>> getDeployedUserList(@RequestBody GetDeployedUserListDto dto);

    @PostMapping("/api/rpa-auth/user/getDeployedUserListWithoutTenantId")
    AppResponse<PageDto<RobotExecute>> getDeployedUserListWithoutTenantId(@RequestBody GetDeployedUserListDto dto);

    /**
     * 获取未部署用户列表
     * @param dto 查询条件
     * @return 未部署用户列表
     */
    @PostMapping("/api/rpa-auth/user/getUserUnDeployed")
    AppResponse<List<MarketDto>> getUserUnDeployed(@RequestBody GetUserUnDeployedDto dto);

    /**
     * 获取市场用户列表（分页）
     * @param dto 查询条件
     * @return 市场用户分页列表
     */
    @PostMapping("/api/rpa-auth/user/getMarketUserList")
    AppResponse<PageDto<MarketDto>> getMarketUserList(@RequestBody GetMarketUserListDto dto);

    /**
     * 获取公共市场用户列表（分页）
     * @param dto 查询条件
     * @return 公共市场用户分页列表
     */
    @PostMapping("/api/rpa-auth/user/getMarketUserListByPublic")
    AppResponse<PageDto<MarketDto>> getMarketUserListByPublic(@RequestBody GetMarketUserListByPublicDto dto);

    /**
     * 根据手机号查询市场用户（不在市场中的用户）
     * @param dto 查询条件
     * @return 用户列表
     */
    @PostMapping("/api/rpa-auth/user/getMarketUserByPhone")
    AppResponse<List<MarketDto>> getMarketUserByPhone(@RequestBody GetMarketUserByPhoneDto dto);

    /**
     * 根据手机号查询市场中的用户（用于市场所有者，排除自己）
     * @param dto 查询条件
     * @return 用户列表
     */
    @PostMapping("/api/rpa-auth/user/getMarketUserByPhoneForOwner")
    AppResponse<List<MarketDto>> getMarketUserByPhoneForOwner(@RequestBody GetMarketUserByPhoneForOwnerDto dto);

    /**
     * 根据用户ID列表查询租户用户列表
     * @param dto 查询条件
     * @return 租户用户列表
     */
    @PostMapping("/api/rpa-auth/user/getMarketTenantUserList")
    AppResponse<List<TenantUser>> getMarketTenantUserList(@RequestBody GetMarketTenantUserListDto dto);

    /**
     * 根据用户ID查询用户信息
     * @param id 用户ID
     * @return 用户信息
     */
    @GetMapping("/api/rpa-auth/user/infoById")
    AppResponse<User> getUserInfoById(@RequestParam("id") String id);

    /**
     * 根据手机号查询用户姓名
     * @param phone 手机号
     * @return 用户姓名
     */
    @GetMapping("/api/rpa-auth/user/phone/realName")
    AppResponse<String> getRealNameByPhone(@RequestParam("phone") String phone);

    /**
     * 根据手机号查询登录名
     * @param phone 手机号
     * @return 登录名
     */
    @GetMapping("/api/rpa-auth/user/phone/loginName")
    AppResponse<String> getLoginNameByPhone(@RequestParam("phone") String phone);

    /**
     * 根据手机号查询用户信息
     * @param phone 手机号
     * @return 用户信息
     */
    @GetMapping("/api/rpa-auth/user/phone/info")
    AppResponse<User> getUserInfoByPhone(@RequestParam("phone") String phone);

    /**
     * 根据用户ID列表查询用户信息列表（最多支持100个id）
     * @param userIdList 用户ID列表
     * @return 用户信息列表
     */
    @PostMapping("/api/rpa-auth/user/queryByIds")
    AppResponse<List<User>> queryUserListByIds(@RequestBody List<String> userIdList);

    /**
     * 根据姓名模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @return 用户信息列表
     */
    @GetMapping("/api/rpa-auth/user/search/name")
    AppResponse<List<User>> searchUserByName(
            @RequestParam("keyword") String keyword, @RequestParam(value = "deptId", required = false) String deptId);

    /**
     * 根据手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @return 用户信息列表
     */
    @GetMapping("/api/rpa-auth/user/search/phone")
    AppResponse<List<User>> searchUserByPhone(
            @RequestParam("keyword") String keyword, @RequestParam(value = "deptId", required = false) String deptId);

    /**
     * 根据姓名或手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @return 用户信息列表
     */
    @GetMapping("/api/rpa-auth/user/search")
    AppResponse<List<User>> searchUserByNameOrPhone(
            @RequestParam("keyword") String keyword, @RequestParam(value = "deptId", required = false) String deptId);

    // ==================== TenantController 租户相关接口 ====================
    /**
     * 获取租户ID
     * @return
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantId")
    AppResponse<String> getTenantId();

    /**
     * 根据租户id获取所有组织列表
     * @param tenantId
     * @return
     */
    @GetMapping("/api/rpa-auth/tenant/getAllOrgList")
    AppResponse<List<Org>> queryAllOrgList(@RequestParam("tenantId") String tenantId);

    /**
     * 当前登录用户在此应用的租户列表
     * @return 租户列表
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantListInApp")
    AppResponse<List<Tenant>> getTenantListInApp();

    /**
     * 企业信息查询
     * @return 企业信息
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantInfo")
    AppResponse<TenantInfoDto> getTenantInfo();

    /**
     * 更改企业管理员（暂不支持）
     * @param id 管理员ID
     * @return 操作结果
     */
    @GetMapping("/api/rpa-auth/tenant/changeManager")
    AppResponse<String> changeManager(@RequestParam("id") String id);

    /**
     * 获取所有用户
     * @param userName 用户名
     * @return 用户列表
     */
    @PostMapping("/api/rpa-auth/tenant/all-user")
    AppResponse<List<UserVo>> getAllUser(@RequestParam("userName") String userName);

    /**
     * 获取当前登录的租户ID
     * @return 当前登录的租户ID
     */
    @GetMapping("/api/rpa-auth/tenant/current/id")
    AppResponse<String> getCurrentTenantId();

    /**
     * 获取当前登录的租户名称
     * @return 当前登录的租户名称
     */
    @GetMapping("/api/rpa-auth/tenant/current/name")
    AppResponse<String> getCurrentTenantName();

    /**
     * 根据租户ID查询租户信息
     * @param tenantId 租户ID
     * @return 租户信息
     */
    @GetMapping("/api/rpa-auth/tenant/info")
    AppResponse<Tenant> queryTenantInfoById(@RequestParam("tenantId") String tenantId);

    /**
     * 切换租户
     * @param tenantId 切换租户id
     * @return 切换结果
     */
    @PostMapping("/api/rpa-auth/tenant/switch")
    AppResponse<String> switchTenant(@RequestParam("tenantId") String tenantId);

    /**
     * 获取未分类的租户ID列表
     * @return 未分类的租户ID列表
     */
    @GetMapping("/api/rpa-auth/tenant/getNoClassifyTenantIds")
    AppResponse<List<String>> getNoClassifyTenantIds();

    /**
     * 更新租户分类完成标志
     * @param tenantIds 租户ID列表
     * @return 更新的记录数
     */
    @PostMapping("/api/rpa-auth/tenant/updateTenantClassifyCompleted")
    AppResponse<Integer> updateTenantClassifyCompleted(@RequestBody List<String> tenantIds);

    /**
     * 获取所有企业租户ID列表（租户代码以ep_或es_开头）
     * @return 企业租户ID列表
     */
    @GetMapping("/api/rpa-auth/tenant/getAllEnterpriseTenantId")
    AppResponse<List<String>> getAllEnterpriseTenantId();

    /**
     * 获取所有租户ID列表（排除default-tenant）
     * @return 租户ID列表
     */
    @GetMapping("/api/rpa-auth/tenant/getAllTenantId")
    AppResponse<List<String>> getAllTenantId();

    /**
     * 获取租户管理员ID列表
     * @param tenantId 租户ID
     * @return 租户管理员ID列表
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantManagerIds")
    AppResponse<List<String>> getTenantManagerIds(@RequestParam("tenantId") String tenantId);

    /**
     * 获取租户普通用户ID列表
     * @param tenantId 租户ID
     * @return 租户普通用户ID列表
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantNormalUserIds")
    AppResponse<List<String>> getTenantNormalUserIds(@RequestParam("tenantId") String tenantId);

    /**
     * 获取租户用户类型（1表示租户管理员，其他表示普通用户）
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @return 租户用户类型（可能为null）
     */
    @GetMapping("/api/rpa-auth/tenant/getTenantUserType")
    AppResponse<Integer> getTenantUserType(
            @RequestParam("userId") String userId, @RequestParam("tenantId") String tenantId);

    // ==================== RoleController 角色相关接口 ====================

    /**
     * 获取用户角色列表
     * @return 角色列表
     */
    @GetMapping("/api/rpa-auth/role/getUserRoleList")
    AppResponse<List<Role>> getUserRoleList();

    /**
     * 查询角色详情
     * @param tenantId
     * @param dto
     * @return
     */
    @PostMapping("/api/rpa-auth/role/queryDetail")
    AppResponse<Role> queryRoleDetail(@RequestParam("tenantId") String tenantId, @RequestBody GetRoleDto dto);

    /**
     * 查询应用内全部角色列表
     * @return 角色列表
     */
    @GetMapping("/api/rpa-auth/role/getUserRoleListInApp")
    AppResponse<List<Role>> queryRoleTreeList();

    /**
     * 新增角色
     * @param createRoleDto 创建角色DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/role/add")
    AppResponse<String> addRole(@RequestBody Object createRoleDto);

    /**
     * 编辑角色
     * @param updateRoleDto 更新角色DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/role/update")
    AppResponse<String> updateRole(@RequestBody Object updateRoleDto);

    /**
     * 删除角色
     * @param deleteCommonDto 删除角色DTO
     * @return 删除结果
     */
    @PostMapping("/api/rpa-auth/role/delete")
    AppResponse<String> deleteRole(@RequestBody Object deleteCommonDto);

    /**
     * 根据名称模糊查询角色
     * @param listRoleDto 查询角色DTO
     * @return 角色分页列表
     */
    @PostMapping("/api/rpa-auth/role/search")
    AppResponse<PageDto<Role>> searchRole(@RequestBody Object listRoleDto);

    // ==================== ResourceController 资源权限相关接口 ====================

    /**
     * 当前登录用户在应用中的资源信息
     * @return 资源列表
     */
    @GetMapping("/api/rpa-auth/resource/currentResourceList")
    AppResponse<List<Resource>> getUserResourceList();

    // ==================== LoginController 登录登出相关接口 ====================

    /**
     * 退出登录
     * @return 登出结果
     */
    @PostMapping("/api/rpa-auth/logout")
    AppResponse<String> logout();

    /**
     * 查询登录状态
     * @return 登录状态
     */
    @GetMapping("/api/rpa-auth/login-status")
    AppResponse<Boolean> loginStatus();

    /**
     * 获取token
     * @return token
     */
    @GetMapping("/api/rpa-auth/token")
    String getToken();

    /**
     * 第一步：预验证
     * 验证用户身份（手机号+密码 或 手机号+验证码）
     * 返回临时凭证，用于后续获取租户列表
     * @param loginDto 登录请求参数
     * @return 临时凭证
     */
    @PostMapping("/api/rpa-auth/pre-authenticate")
    AppResponse<String> preAuthenticate(@RequestBody Object loginDto);

    /**
     * 第二步：获取租户列表
     * 使用临时凭证获取用户的租户列表
     * 此时还未建立 session
     * @param tempToken 临时凭证
     * @return 租户列表
     */
    @GetMapping("/api/rpa-auth/tenant/list")
    AppResponse<List<Tenant>> getTenantList(@RequestParam(value = "tempToken", required = false) String tempToken);

    @GetMapping("/api/rpa-auth/tenant/expiration")
    AppResponse<TenantExpirationDto> getExpiration();

    /**
     * 第三步：正式登录
     * 用户选择租户后，使用临时凭证和租户ID完成登录
     * 此时会建立 session
     * @param tempToken 临时凭证
     * @param tenantId 选择的租户ID
     * @return 登录成功返回用户信息
     */
    @PostMapping("/api/rpa-auth/login")
    AppResponse<User> login(@RequestParam("tempToken") String tempToken, @RequestParam("tenantId") String tenantId);

    /**
     * 发送短信验证码
     * 用于免密登录和注册
     * @param phone 手机号
     * @return 发送结果
     */
    @PostMapping("/api/rpa-auth/verification-code/send")
    AppResponse<String> sendVerificationCode(@RequestParam("phone") String phone);

    /**
     * 设置密码
     * 用户设置密码后，更新讯飞账号和UAP密码
     * @param setPasswordDto 设置密码请求参数
     * @return 是否成功
     */
    @PostMapping("/api/rpa-auth/password/set")
    AppResponse<Boolean> setPasswordAndLogin(@RequestBody Object setPasswordDto);

    /**
     * 检查用户是否已注册
     * @param phone 手机号或登录名
     * @return 是否已注册
     */
    @GetMapping("/api/rpa-auth/user/exist")
    AppResponse<Boolean> checkUserExist(@RequestParam("phone") String phone);

    /**
     * 删除讯飞账号
     * @param phone 手机号
     * @return 删除结果
     */
    @PostMapping("/api/rpa-auth/iflytek-account/delete")
    AppResponse<String> deleteIflytekAccount(@RequestParam("phone") String phone);

    /**
     * 用户注册（第一步）
     * 输入手机号、验证码、用户名
     * 在讯飞账号和UAP创建用户（使用默认密码）
     * 返回临时凭证用于后续设置密码
     * @param registerDto 注册请求参数
     * @return 临时凭证
     */
    @PostMapping("/api/rpa-auth/register")
    AppResponse<String> register(@RequestBody Object registerDto);

    /**
     * 刷新Token
     * 使用 refreshToken 刷新 accessToken
     *
     * @param accessToken accessToken
     * @return 刷新结果
     */
    @PostMapping("/api/rpa-auth/refresh-token")
    AppResponse<Boolean> refreshToken(@RequestParam("accessToken") String accessToken);

    // ==================== DeptController 部门相关接口 ====================

    /**
     * 获取部门树
     * @return 部门树
     */
    @GetMapping("/api/rpa-auth/dept/queryTreeList")
    AppResponse<Object> queryDeptTreeList();

    /**
     * 通过部门父节点的id查询所有部门子节点
     * @param dto 查询部门节点DTO
     * @return 部门树节点列表
     */
    @PostMapping("/api/rpa-auth/dept/queryDeptNodeByPid")
    AppResponse<List<DeptTreeNodeVo>> queryDeptTreeByPid(@RequestBody Object dto);

    /**
     * 获取租户名
     * @return 租户名
     */
    @GetMapping("/api/rpa-auth/dept/queryTenantName")
    AppResponse<String> queryTenantName();

    /**
     * 通过deptId查询部门名
     * @param dto 查询部门ID DTO
     * @return 部门名
     */
    @PostMapping("/api/rpa-auth/dept/queryDeptNameByDeptId")
    AppResponse<DeptNameVo> queryDeptNameByDeptId(@RequestBody Object dto);

    /**
     * 新增部门
     * @param createUapOrgDto 创建部门DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/dept/add")
    AppResponse<String> addDept(@RequestBody Object createUapOrgDto);

    /**
     * 编辑部门
     * @param editOrgDto 编辑部门DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/dept/edit")
    AppResponse<String> editDept(@RequestBody Object editOrgDto);

    /**
     * 删除部门
     * @param deleteCommonDto 删除部门DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/dept/delete")
    AppResponse<String> deleteDept(@RequestBody Object deleteCommonDto);

    /**
     * 查询部门树、人数、负责人
     * @return 部门树和人员信息
     */
    @GetMapping("/api/rpa-auth/dept/treeAndPerson")
    AppResponse<java.util.Map<String, Object>> treeAndPerson();

    /**
     * 部门人数信息查询
     * @param dto 查询部门节点DTO
     * @return 部门人员树节点列表
     */
    @PostMapping("/api/rpa-auth/dept/queryDeptPersonNodeByPid")
    AppResponse<List<DeptPersonTreeNodeVo>> queryDeptPersonNodeByPid(@RequestBody Object dto);

    /**
     * 查询当前机构的所有用户
     * @param dto 查询部门ID DTO
     * @return 用户列表
     */
    @PostMapping("/api/rpa-auth/dept/queryUserListByDeptId")
    AppResponse<List<UserVo>> queryAllUserByDeptId(@RequestBody Object dto);

    /**
     * 获取当前登录用户的部门levelCode，即deptIdPath
     * @return 部门levelCode
     */
    @GetMapping("/api/rpa-auth/dept/current/levelCode")
    AppResponse<String> getCurrentLevelCode();

    /**
     * 获取当前登录用户的部门ID
     * @return 部门ID
     */
    @GetMapping("/api/rpa-auth/dept/current/id")
    AppResponse<String> getCurrentDeptId();

    /**
     * 获取当前登录用户的部门详细信息
     * @return 部门信息
     */
    @GetMapping("/api/rpa-auth/dept/current")
    AppResponse<Org> getCurrentDeptInfo();

    /**
     * 根据部门ID查询部门详细信息
     * @param id 部门ID
     * @return 部门信息
     */
    @GetMapping("/api/rpa-auth/dept/info")
    AppResponse<Org> getDeptInfoByDeptId(@RequestParam("id") String id);

    /**
     * 查询部门ID对应的levelCode
     * @param id 部门ID
     * @return levelCode
     */
    @GetMapping("/api/rpa-auth/dept/levelCode")
    AppResponse<String> getLevelCodeByDeptId(@RequestParam("id") String id);

    /**
     * 查询指定机构及所有子机构的用户数量
     * @param id 部门ID
     * @return 用户数量
     */
    @GetMapping("/api/rpa-auth/dept/userNum")
    AppResponse<Long> getUserNumByDeptId(@RequestParam("id") String id);

    /**
     * 根据部门ID列表获取部门信息列表
     * @param orgIdList 部门ID列表
     * @return 部门信息列表
     */
    @PostMapping("/api/rpa-auth/dept/queryByIds")
    AppResponse<List<Org>> queryOrgListByIds(@RequestBody List<String> orgIdList);

    /**
     * 根据用户ID获取部门ID
     * @param userId 用户ID
     * @return 部门ID
     */
    @GetMapping("/api/rpa-auth/dept/user/deptId")
    AppResponse<String> getDeptIdByUserId(
            @RequestParam("userId") String userId, @RequestParam("tenantId") String tenantId);

    /**
     * 查询数据权限，是一个部门列表
     * @return 数据权限详情
     */
    @GetMapping("/api/rpa-auth/dept/dataAuth")
    AppResponse<DataAuthDetailDo> getDataAuthWithDeptList();

    // ==================== DataAuthController 数据权限相关接口 ====================

    /**
     * 根据角色ID查询权限列表
     * @param tenantId
     * @param roleId
     * @return
     */
    @GetMapping("/api/rpa-auth/dataAuth/getAuthorityListByRoleId")
    AppResponse<List<Authority>> queryAuthorityListByRoleId(
            @RequestParam("tenantId") String tenantId, @RequestParam("roleId") String roleId);

    /**
     * 查询勾选的数据权限
     * @param roleId 角色ID
     * @return 数据权限列表
     */
    @GetMapping("/api/rpa-auth/dataAuth/queryCheckedDataAuth")
    AppResponse<List<DataAuthorityWithDimDictDto>> getCheckedDataAuth(@RequestParam("roleId") String roleId);

    /**
     * 角色绑定数据权限
     * @param bindRoleDataAuthDto 绑定角色数据权限DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/dataAuth/bindDataAuth")
    AppResponse<String> bindDataAuth(@RequestBody Object bindRoleDataAuthDto);

    // ==================== AuthController 菜单权限相关接口 ====================

    /**
     * 当前登录用户在应用中的菜单信息
     * @return 菜单树
     */
    @GetMapping("/api/rpa-auth/menu/getUserAuthTreeInApp")
    AppResponse<List<TreeNode>> getUserAuthTreeInApp();

    /**
     * 查询菜单、权限树
     * @param roleId 角色ID
     * @return 菜单权限树
     */
    @GetMapping("/api/rpa-auth/menu/getAuthResourceTreeInApp")
    AppResponse<TreeNode> getAuthResourceTreeInApp(@RequestParam("roleId") String roleId);

    /**
     * 保存菜单、资源树
     * @param roleAuthResourceDto 角色权限资源DTO
     * @return 操作结果
     */
    @PostMapping("/api/rpa-auth/menu/save")
    AppResponse<String> saveRoleAuth(@RequestBody Object roleAuthResourceDto);
}
