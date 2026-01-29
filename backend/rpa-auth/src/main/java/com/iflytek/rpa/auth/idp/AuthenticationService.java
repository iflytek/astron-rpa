package com.iflytek.rpa.auth.idp;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.entity.LoginDto;
import com.iflytek.rpa.auth.core.entity.RegisterDto;
import com.iflytek.rpa.auth.core.entity.Tenant;
import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public interface AuthenticationService {

    String SCENE_LOGIN = "login";
    String SCENE_REGISTER = "register";
    String SCENE_SET_PASSWORD = "set_password";

    /**
     * 预验证（第一步）
     * 验证用户身份，但不建立 session
     * 返回临时凭证，用于后续获取租户列表
     * 如果用户在UAP不存在，会自动注册用户
     *
     * @param loginDto 登录请求DTO
     * @param request HTTP请求（用于注册UAP用户）
     * @return 临时凭证（可以是 token 或其他标识）
     */
    String preAuthenticate(LoginDto loginDto, HttpServletRequest request);

    /**
     * 正式登录（第二步）
     * 用户选择租户后，使用临时凭证完成登录，建立 session
     *
     * @param tempToken 临时凭证
     * @param tenantId 选择的租户ID
     * @param servletRequest HTTP请求
     * @return 登录用户信息
     */
    User loginWithTenant(String tempToken, String tenantId, HttpServletRequest servletRequest);

    /**
     * 获取租户列表（第二步前置）
     * 不同认证实现可自行决定如何解析临时凭证
     *
     * @param tempToken 临时凭证
     * @param request   HTTP请求
     * @return 租户列表
     */
    AppResponse<List<Tenant>> getTenantList(String tempToken, HttpServletRequest request);

    /**
     * 【已废弃】原登录方法，保留用于兼容
     * 建议使用 preAuthenticate + loginWithTenant 两步登录
     *
     * @param loginDto 登录请求DTO
     * @return 登录结果
     */
    @Deprecated
    User login(LoginDto loginDto, HttpServletRequest servletRequest);

    /**
     * 根据临时凭证获取用户手机号
     * 用于在未建立 session 时查询租户列表
     *
     * @param tempToken 临时凭证
     * @return 用户手机号
     */
    String getPhoneByTempToken(String tempToken);

    /**
     * 根据临时凭证获取用户手机号
     * 用于在未建立 session 时查询租户列表
     *
     * @param tempToken 临时凭证
     * @return 用户手机号
     */
    LoginDto getLoginInfoByTempToken(String tempToken);

    /**
     * 注册（第一步）
     * 只需要手机号和验证码，不需要密码
     * 在讯飞账号和UAP创建用户（使用默认密码）
     *
     * @param registerDto 注册请求DTO
     * @return 临时凭证（用于后续设置密码）
     */
    String register(RegisterDto registerDto, HttpServletRequest request);

    /**
     * 设置密码并自动登录（注册第二步）
     * 用户设置密码后，更新讯飞账号和UAP密码，并自动登录
     *
     * @param tempToken 临时凭证
     * @param password 新密码
     * @param tenantId 选择的租户ID
     * @param request HTTP请求
     * @return 登录用户信息
     */
    User setPasswordAndLogin(String tempToken, String password, String tenantId, HttpServletRequest request);

    /**
     * 查询用户信息
     *
     * @param loginName 登录名
     * @return 用户信息
     */
    boolean queryUserExist(String loginName);

    boolean setPassword(String tempToken, String password, String tenantId, HttpServletRequest request);

    AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response);

    /**
     * 刷新Token
     * 使用 refreshToken 刷新 accessToken
     *
     * @param request     HTTP请求
     * @param accessToken
     * @return 刷新结果
     */
    AppResponse<Boolean> refreshToken(HttpServletRequest request, String accessToken);

    /**
     * 获取验证码
     * 生成验证码，存储到Redis，并发送短信
     * 增加场景维度，防止不同业务场景的验证码交叉使用
     *
     * @param phone 手机号
     * @param scene 业务场景（如 register/login/set_password）
     * @return 发送结果
     */
    String getVerificationCode(String phone, String scene);

    /**
     * 获取验证码（默认登录场景）
     *
     * @param phone 手机号
     * @return 发送结果
     */
    default String getVerificationCode(String phone) {
        return getVerificationCode(phone, SCENE_LOGIN);
    }

    /**
     * 检查session是否有效
     * 同时校验空间是否到期，如果空间到期则强制退出登录
     *
     * @param request HTTP请求
     * @param response HTTP响应
     * @return 检查结果，如果空间到期会返回错误响应
     */
    AppResponse<Boolean> checkSession(HttpServletRequest request, HttpServletResponse response);

    /**
     * 检查登录状态
     * 验证当前请求是否已登录
     *
     * @param request HTTP请求
     * @return 是否已登录
     */
    boolean checkLoginStatus(HttpServletRequest request);

    /**
     * 修改密码
     * 验证旧密码后，更新为新密码，并生成临时凭证用于后续登录
     *
     * @param changePasswordDto 修改密码请求参数（包含账号、手机号、旧密码、新密码、确认密码）
     * @return 临时凭证（tempToken），用于后续获取租户列表和登录
     */
    AppResponse<String> changePassword(ChangePasswordDto changePasswordDto);

    AppResponse<String> addUser(AddUserDto user, HttpServletRequest request);
}
