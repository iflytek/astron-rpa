package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.auditRecord.constants.AuditLog;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.entity.CreateUapUserDto;
import com.iflytek.rpa.auth.core.entity.UpdateUapUserDto;
import com.iflytek.rpa.auth.core.service.UserService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 员工
 */
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 注册
     * @param request
     * @return
     */
    @PostMapping("/register")
    public AppResponse<String> register(@RequestBody @Valid RegisterDto registerDto, HttpServletRequest request)
            throws IOException {

        return userService.register(registerDto, request);
    }

    /**
     * 查询当前登录的用户信息
     * @param request
     * @return
     */
    @GetMapping("/info")
    public AppResponse<User> getUserInfo(HttpServletRequest request) {

        return userService.getUserInfo(request);
    }

    /**
     * 新增员工
     * @param createUapUserDto
     * @param request
     * @return
     */
    @AuditLog(moduleName = "管理员权限", typeName = "添加成员")
    @PostMapping("/add")
    public AppResponse<String> addUser(@RequestBody CreateUapUserDto createUapUserDto, HttpServletRequest request)
            throws IOException {
        return userService.addUser(createUapUserDto, request);
    }

    /**
     * 编辑员工
     * @param
     * @param request
     * @return
     */
    @PostMapping("/edit")
    public AppResponse<String> editUser(@RequestBody UpdateUapUserDto updateUapUserDto, HttpServletRequest request)
            throws IOException {
        return userService.editUser(updateUapUserDto, request);
    }

    /**
     * 删除员工
     * @param
     * @param request
     * @return
     */
    @AuditLog(moduleName = "管理员权限", typeName = "移除成员")
    @PostMapping("/delete")
    public AppResponse<String> deleteUser(@RequestBody UserDeleteDto userDto, HttpServletRequest request)
            throws IOException {
        return userService.deleteUser(userDto, request);
    }

    /**
     * 启用/禁用员工
     * @param
     * @param request
     * @return
     */
    @PostMapping("/enable")
    public AppResponse<String> enableUser(@RequestBody UserEnableDto userDto, HttpServletRequest request) {
        return userService.enableUser(userDto, request);
    }

    /**
     * 变更部门
     * @param
     * @param request
     * @return
     */
    @PostMapping("/changeDept")
    public AppResponse<String> changeDept(@RequestBody UserChangeDeptDto userDto, HttpServletRequest request) {
        return userService.changeDept(userDto, request);
    }

    /**
     * 查询当前机构的全部用户(部门新增，部门负责人下拉框)
     * @param
     * @param request
     * @return
     */
    @GetMapping("/queryAllListByOrgId")
    public AppResponse<List<User>> queryUserDetailListByOrgId(
            @RequestParam("orgId") String orgId, HttpServletRequest request) throws IOException {
        return userService.queryUserDetailListByOrgId(orgId, request);
    }

    /**
     * 分页查询当前机构的用户
     * @param
     * @param request
     * @return
     */
    @PostMapping("/queryListByOrgId")
    public AppResponse<PageDto<DeptUserDto>> queryUserListByOrgId(
            @RequestBody ListUserDto listUserDto, HttpServletRequest request) throws IOException { //

        return userService.queryUserListByOrgId(listUserDto, request);
    }

    /**
     * 分页获取角色绑定的用户列表，可根据登录名或姓名模糊查询
     * @param
     * @param request
     * @return
     */
    @PostMapping("/queryBindListByRole")
    public AppResponse<PageDto<User>> queryBindListByRole(
            @RequestBody ListUserByRoleDto listUserByRoleDto, HttpServletRequest request) throws IOException {
        return userService.queryBindListByRole(listUserByRoleDto, request);
    }

    /**
     * 人员解绑角色
     * @param bindRoleDto
     * @param request
     * @return
     */
    @PostMapping("/unbindRole")
    public AppResponse<String> unbindRole(@RequestBody BindRoleDto bindRoleDto, HttpServletRequest request)
            throws IOException {
        return userService.unbindRole(bindRoleDto, request);
    }

    /**
     * 按名称模糊搜索所有员工或部门
     * @param
     * @param request
     * @return
     */
    @GetMapping("/searchDeptOrUser")
    public AppResponse<GetDeptOrUserDto> searchDeptOrUser(
            @RequestParam("name") String name, HttpServletRequest request) {
        return userService.searchDeptOrUser(name, request);
    }

    /**
     * 角色管理-根据部门id查询部门下的人员和子部门
     * @param id
     * @param request
     * @return
     */
    @GetMapping("/queryUserAndDept")
    public AppResponse<List<CurrentDeptUserDto>> queryUserAndDept(
            @RequestParam("id") String id, HttpServletRequest request) {

        return userService.queryUserAndDept(id, request);
    }

    /**
     * 角色管理-根据名字或手机号模糊查询员工
     * @param keyWord
     * @param request
     * @return
     */
    @GetMapping("/searchUserWithStatus")
    public AppResponse<List<CurrentDeptUserDto>> searchUserWithStatus(
            @RequestParam("keyWord") String keyWord, HttpServletRequest request) throws IOException {

        return userService.searchUserWithStatus(keyWord, request);
    }

    /**
     * 角色管理-添加成员
     * @param bindUserListDto
     * @param request
     * @return
     */
    @PostMapping("/batchBindRole")
    AppResponse<String> bindUserListRole(@RequestBody BindUserListDto bindUserListDto, HttpServletRequest request)
            throws IOException {

        return userService.bindUserListRole(bindUserListDto, request);
    }

    /**
     * 卓越中心-机器人看板-所有者下拉选择-查询接口
     * 跟据输入的关键字（姓名或手机号）查询用户
     * @param keyword
     * @param deptId
     * @return
     */
    @PostMapping("/getUserByNameOrPhone")
    AppResponse<List<UserSearchDto>> getUserByNameOrPhone(String keyword, String deptId, HttpServletRequest request) {
        return userService.getUserByNameOrPhone(keyword, deptId, request);
    }

    /**
     * 获取用户详细信息
     * @param tenantId
     * @param getUserDto
     * @param request
     * @return
     */
    @PostMapping("/getUserExtendInfo")
    public AppResponse<UserExtendDto> queryUserExtendInfo(
            @RequestParam("tenantId") String tenantId, @RequestBody GetUserDto getUserDto, HttpServletRequest request)
            throws IOException {
        return userService.queryUserExtendInfo(tenantId, getUserDto, request);
    }

    /**
     * 获取当前登录用户
     * @param request HTTP请求
     * @return 当前登录用户信息
     */
    @GetMapping("/current")
    public AppResponse<User> getCurrentLoginUser(HttpServletRequest request) {
        return userService.getCurrentLoginUser(request);
    }

    /**
     * 获取当前登录用户ID
     * @param request HTTP请求
     * @return 当前登录用户ID
     */
    @GetMapping("/current/id")
    public AppResponse<String> getCurrentUserId(HttpServletRequest request) {
        return userService.getCurrentUserId(request);
    }

    /**
     * 获取当前登录用户名
     * @param request HTTP请求
     * @return 当前登录用户名
     */
    @GetMapping("/current/username")
    public AppResponse<String> getCurrentLoginUsername(HttpServletRequest request) {
        return userService.getCurrentLoginUsername(request);
    }

    /**
     * 根据用户ID查询登录名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 登录名
     */
    @GetMapping("/loginName")
    public AppResponse<String> getLoginNameById(@RequestParam("id") String id, HttpServletRequest request) {
        return userService.getLoginNameById(id, request);
    }

    /**
     * 根据用户ID查询姓名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户姓名
     */
    @GetMapping("/realName")
    public AppResponse<String> getRealNameById(@RequestParam("id") String id, HttpServletRequest request) {
        return userService.getRealNameById(id, request);
    }

    /**
     * 根据用户ID查询用户信息
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户信息
     */
    @GetMapping("/infoById")
    public AppResponse<User> getUserInfoById(@RequestParam("id") String id, HttpServletRequest request) {
        return userService.getUserInfoById(id, request);
    }

    /**
     * 根据手机号查询用户姓名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户姓名
     */
    @GetMapping("/phone/realName")
    public AppResponse<String> getRealNameByPhone(@RequestParam("phone") String phone, HttpServletRequest request) {
        return userService.getRealNameByPhone(phone, request);
    }

    /**
     * 根据手机号查询登录名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 登录名
     */
    @GetMapping("/phone/loginName")
    public AppResponse<String> getLoginNameByPhone(@RequestParam("phone") String phone, HttpServletRequest request) {
        return userService.getLoginNameByPhone(phone, request);
    }

    /**
     * 判断是否历史用户（ext_info = 1 表示历史用户）
     * @param phone 手机号
     * @return 是否历史用户
     */
    @GetMapping("/history")
    public AppResponse<Boolean> isHistoryUser(@RequestParam(required = false) String phone) {
        return userService.isHistoryUser(phone);
    }

    /**
     * 根据手机号查询用户信息
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户信息
     */
    @GetMapping("/phone/info")
    public AppResponse<User> getUserInfoByPhone(@RequestParam("phone") String phone, HttpServletRequest request) {
        return userService.getUserInfoByPhone(phone, request);
    }

    /**
     * 根据用户ID列表查询用户信息列表（最多支持100个id）
     * @param userIdList 用户ID列表
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @PostMapping("/queryByIds")
    public AppResponse<List<User>> queryUserListByIds(
            @RequestBody List<String> userIdList, HttpServletRequest request) {
        return userService.queryUserListByIds(userIdList, request);
    }

    /**
     * 根据姓名模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @GetMapping("/search/name")
    public AppResponse<List<User>> searchUserByName(
            @RequestParam("keyword") String keyword,
            @RequestParam(value = "deptId", required = false) String deptId,
            HttpServletRequest request) {
        return userService.searchUserByName(keyword, deptId, request);
    }

    /**
     * 根据手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @GetMapping("/search/phone")
    public AppResponse<List<User>> searchUserByPhone(
            @RequestParam("keyword") String keyword,
            @RequestParam(value = "deptId", required = false) String deptId,
            HttpServletRequest request) {
        return userService.searchUserByPhone(keyword, deptId, request);
    }

    /**
     * 根据姓名或手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @GetMapping("/search")
    public AppResponse<List<User>> searchUserByNameOrPhone(
            @RequestParam("keyword") String keyword,
            @RequestParam(value = "deptId", required = false) String deptId,
            HttpServletRequest request) {
        return userService.searchUserByNameOrPhone(keyword, deptId, request);
    }

    /**
     * 获取当前用户权限列表
     * @param request HTTP请求
     * @return 用户权限列表
     */
    @GetMapping("/current/permissions")
    public AppResponse<List<Permission>> getCurrentUserPermissionList(HttpServletRequest request) throws IOException {
        return userService.getCurrentUserPermissionList(request);
    }

    /**
     * 获取Casdoor登录重定向URL（Casdoor专用）
     * @param request HTTP请求
     * @return 登录重定向URL
     */
    @GetMapping("/redirect-url")
    public AppResponse<String> getRedirectUrl(HttpServletRequest request) {
        return userService.getRedirectUrl(request);
    }

    /**
     * Casdoor OAuth登录（Casdoor专用）
     * @param code OAuth授权码
     * @param state OAuth state参数
     * @param request HTTP请求
     * @return 用户信息
     */
    @PostMapping("/sign/in")
    public AppResponse<User> signIn(
            @RequestParam("code") String code, @RequestParam("state") String state, HttpServletRequest request)
            throws IOException {
        return userService.signIn(code, state, request);
    }

    /**
     * 检查用户登录状态（Casdoor专用）
     * @param request HTTP请求
     * @return 用户信息，如果未登录返回错误
     */
    @GetMapping("/login-check")
    public AppResponse<User> checkLoginStatus(HttpServletRequest request) {
        return userService.checkLoginStatus(request);
    }

    /**
     * 刷新服务端token（Casdoor专用，当accessToken过期时使用）
     * @param request HTTP请求
     * @return 操作结果
     */
    @PostMapping("/refresh-token")
    public AppResponse<String> refreshToken(HttpServletRequest request) {
        return userService.refreshToken(request);
    }

    /**
     * 获取当前登录用户的权益
     * 客户端启动时调用此接口
     * 根据session查询租户code，判断如果是企业租户，则查询数据库中权益
     * 如果没有数据，默认拥有所有权益
     *
     * @param request HTTP请求
     * @return 用户权益信息
     */
    @GetMapping("/entitlement")
    public AppResponse<UserEntitlementDto> getCurrentUserEntitlement(HttpServletRequest request) {
        return userService.getCurrentUserEntitlement(request);
    }

    /**
     * 根据用户ID查询用户信息
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户信息
     */
    @GetMapping("/getNameById")
    public AppResponse<String> getNameById(@RequestParam("id") String id, HttpServletRequest request) {
        return userService.getNameById(id, request);
    }

    /**
     * 获取已部署用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 已部署用户分页列表
     */
    @PostMapping("/getDeployedUserList")
    public AppResponse<PageDto<RobotExecute>> getDeployedUserList(
            @RequestBody GetDeployedUserListDto dto, HttpServletRequest request) {
        return userService.getDeployedUserList(dto, request);
    }

    /**
     * 获取已部署用户列表 没有租户id
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 已部署用户分页列表
     */
    @PostMapping("/getDeployedUserListWithoutTenantId")
    public AppResponse<PageDto<RobotExecute>> getDeployedUserListWithoutTenantId(
            @RequestBody GetDeployedUserListDto dto, HttpServletRequest request) {
        return userService.getDeployedUserListWithoutTenantId(dto, request);
    }

    /**
     * 获取未部署用户列表
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 未部署用户列表
     */
    @PostMapping("/getUserUnDeployed")
    public AppResponse<List<MarketDto>> getUserUnDeployed(
            @RequestBody GetUserUnDeployedDto dto, HttpServletRequest request) {
        return userService.getUserUnDeployed(dto, request);
    }

    /**
     * 获取市场用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 市场用户分页列表
     */
    @PostMapping("/getMarketUserList")
    public AppResponse<PageDto<MarketDto>> getMarketUserList(
            @RequestBody GetMarketUserListDto dto, HttpServletRequest request) {
        return userService.getMarketUserList(dto, request);
    }

    /**
     * 获取公共市场用户列表（分页）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 公共市场用户分页列表
     */
    @PostMapping("/getMarketUserListByPublic")
    public AppResponse<PageDto<MarketDto>> getMarketUserListByPublic(
            @RequestBody GetMarketUserListByPublicDto dto, HttpServletRequest request) {
        return userService.getMarketUserListByPublic(dto, request);
    }

    /**
     * 根据手机号查询市场用户（不在市场中的用户）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 用户列表
     */
    @PostMapping("/getMarketUserByPhone")
    public AppResponse<List<MarketDto>> getMarketUserByPhone(
            @RequestBody GetMarketUserByPhoneDto dto, HttpServletRequest request) {
        return userService.getMarketUserByPhone(dto, request);
    }

    /**
     * 根据手机号查询市场中的用户（用于市场所有者，排除自己）
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 用户列表
     */
    @PostMapping("/getMarketUserByPhoneForOwner")
    public AppResponse<List<MarketDto>> getMarketUserByPhoneForOwner(
            @RequestBody GetMarketUserByPhoneForOwnerDto dto, HttpServletRequest request) {
        return userService.getMarketUserByPhoneForOwner(dto, request);
    }

    /**
     * 根据用户ID列表查询租户用户列表
     * @param dto 查询条件
     * @param request HTTP请求
     * @return 租户用户列表
     */
    @PostMapping("/getMarketTenantUserList")
    public AppResponse<List<TenantUser>> getMarketTenantUserList(
            @RequestBody GetMarketTenantUserListDto dto, HttpServletRequest request) {
        return userService.getMarketTenantUserList(dto, request);
    }
}
