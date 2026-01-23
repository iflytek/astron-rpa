package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.dataPreheater.entity.InitDataEvent;
import com.iflytek.rpa.auth.idp.AuthenticationService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 登陆登出相关
 */
@RestController
@Slf4j
@RequiredArgsConstructor
public class LoginController {

    @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private ApplicationEventPublisher eventPublisher;
    /**
     * 检查session是否过期
     * 同时校验空间是否到期，如果空间到期则强制退出登录
     * @param request
     * @param response
     * @return
     */
    @GetMapping("/check-session")
    public AppResponse<Boolean> checkSession(HttpServletRequest request, HttpServletResponse response) {
        return authenticationService.checkSession(request, response);
    }

    /**
     * 查询登录状态
     *
     * @param request
     * @return
     */
    @GetMapping("/login-status")
    public AppResponse<Boolean> loginStatus(HttpServletRequest request) {
        try {
            boolean isLoggedIn = authenticationService.checkLoginStatus(request);
            log.debug("查询登录状态：{}", isLoggedIn);
            return AppResponse.success(isLoggedIn);
        } catch (Exception e) {
            log.error("查询登录状态异常", e);
            return AppResponse.success(false);
        }
    }

    /**
     * 获取token
     *
     * @param request
     * @return
     */
    @GetMapping("/token")
    public String getToken(HttpServletRequest request) {
        return "Not supported in SaaS";
        //        return UapManagementClientUtil.getToken(request);
    }

    /**
     * 退出登录
     *
     * @param request
     * @param response
     * @throws IOException
     */
    @PostMapping(value = "/logout")
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) throws IOException {
        return authenticationService.logout(request, response);
    }

    /**
     * 第一步：预验证
     * 验证用户身份（手机号+密码 或 手机号+验证码）
     * 返回临时凭证，用于后续获取租户列表
     * platform字段会在验证通过后存储到缓存中，用于后续获取租户列表时过滤
     *
     * @param loginDto 登录请求参数（包含platform字段：client-客户端, admin-运营后台, invite-邀请链接）
     * @return 临时凭证
     */
    @PostMapping("/pre-authenticate")
    public AppResponse<String> preAuthenticate(@RequestBody @Validated LoginDto loginDto, HttpServletRequest request) {
        try {
            log.info("预验证请求，手机号：{}", loginDto.getPhone());
            String tempToken = authenticationService.preAuthenticate(loginDto, request);
            log.info("预验证成功，手机号：{}", loginDto.getPhone());
            return AppResponse.success(tempToken);
        } catch (com.iflytek.rpa.auth.blacklist.exception.ShouldBeBlackException e) {
            // 封禁异常向上抛出，让全局异常处理器处理
            throw e;
        } catch (Exception e) {
            log.error("预验证失败", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, e.getMessage());
        }
    }

    /**
     * 第二步：获取租户列表
     * 使用临时凭证获取用户的租户列表
     * 此时还未建立 session
     * 根据预验证时传入的platform字段过滤租户列表：
     * - platform为client时，返回全部租户列表
     * - platform为admin时，返回非个人租户的列表（过滤掉个人租户）
     * - platform为invite时，返回全部租户列表（不过滤）
     *
     * @param tempToken 临时凭证
     * @return 租户列表
     */
    @GetMapping("/tenant/list")
    public AppResponse<List<Tenant>> getTenantList(
            @RequestParam(required = false) String tempToken, HttpServletRequest request) {
        try {
            log.info("获取租户列表，临时凭证：{}", tempToken);
            return authenticationService.getTenantList(tempToken, request);
        } catch (Exception e) {
            log.error("获取租户列表失败", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        }
    }

    /**
     * 第三步：正式登录
     * 用户选择租户后，使用临时凭证和租户ID完成登录
     * 此时会建立 session
     *
     * @param tempToken 临时凭证
     * @param tenantId  选择的租户ID
     * @param request   HTTP请求
     * @return 登录成功返回用户信息
     */
    @PostMapping("/login")
    public AppResponse<User> login(
            @RequestParam @NotBlank(message = "临时凭证不能为空") String tempToken,
            @RequestParam @NotBlank(message = "租户ID不能为空") String tenantId,
            HttpServletRequest request) {
        try {
            log.info("正式登录请求，临时凭证：{}，租户ID：{}", tempToken, tenantId);
            User user = authenticationService.loginWithTenant(tempToken, tenantId, request);
            log.info("正式登录成功，用户ID：{}，租户ID：{}", user.getId(), tenantId);
            // 初始化团队市场分类 企业团队市场
            eventPublisher.publishEvent(new InitDataEvent(this, tenantId));
            return AppResponse.success(user);
        } catch (Exception e) {
            log.error("正式登录失败", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, e.getMessage());
        }
    }

    /**
     * 发送短信验证码
     * 用于免密登录和注册
     *
     * @param phone 手机号
     * @return 发送结果
     */
    @PostMapping("/verification-code/send")
    public AppResponse<String> sendVerificationCode(
            @RequestParam @NotBlank(message = "手机号不能为空") String phone, @RequestParam(required = false) String scene) {
        try {
            log.info("发送验证码，手机号：{}", phone);

            // 使用接口方法，由具体实现类处理
            String result = authenticationService.getVerificationCode(phone, scene);
            log.info("验证码发送成功，手机号：{}", phone);
            return AppResponse.success(result);
        } catch (UnsupportedOperationException e) {
            log.warn("当前部署模式不支持验证码登录，手机号：{}", phone);
            return AppResponse.error("当前部署模式不支持验证码登录");
        } catch (Exception e) {
            log.error("发送验证码失败，手机号：{}", phone, e);
            return AppResponse.error("发送验证码失败：" + e.getMessage());
        }
    }

    /**
     * 用户注册（第一步）
     * 输入手机号、验证码、用户名
     * 在讯飞账号和UAP创建用户（使用默认密码）
     * 返回临时凭证用于后续设置密码
     *
     * @param registerDto 注册请求参数
     * @param request     HTTP请求
     * @return 临时凭证
     */
    @PostMapping("/register")
    public AppResponse<String> register(@RequestBody @Validated RegisterDto registerDto, HttpServletRequest request) {
        try {
            log.info("用户注册请求，手机号：{}", registerDto.getPhone());

            // 调用注册服务，返回临时凭证
            String tempToken = authenticationService.register(registerDto, request);
            log.info("用户注册成功，手机号：{}，临时凭证已生成", registerDto.getPhone());

            return AppResponse.success(tempToken);
        } catch (Exception e) {
            log.error("用户注册失败", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "注册失败：" + e.getMessage());
        }
    }

    /**
     * 设置密码
     * 用户设置密码后，更新讯飞账号和UAP密码
     *
     * @param setPasswordDto 设置密码请求参数
     * @param request        HTTP请求
     * @return 是否成功
     */
    @PostMapping("/password/set")
    public AppResponse<Boolean> setPasswordAndLogin(
            @RequestBody @Validated SetPasswordDto setPasswordDto, HttpServletRequest request) {
        try {
            log.info("设置密码并登录请求，临时凭证：{}", setPasswordDto.getTempToken());

            // 验证两次密码是否一致
            if (!setPasswordDto.getPassword().equals(setPasswordDto.getConfirmPassword())) {
                return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_PARAM, "两次输入的密码不一致");
            }

            // 设置密码并自动登录
            boolean res = authenticationService.setPassword(
                    setPasswordDto.getTempToken(), setPasswordDto.getPassword(), setPasswordDto.getTenantId(), request);

            log.info("设置密码成功");
            return AppResponse.success(res);

        } catch (Exception e) {
            log.error("设置密码并登录失败", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, e.getMessage());
        }
    }

    /**
     * 检查用户是否已注册
     *
     * @param phone 手机号或登录名
     * @return 是否已注册
     */
    @GetMapping("/user/exist")
    public AppResponse<Boolean> checkUserExist(@RequestParam @NotBlank(message = "手机号不能为空") String phone) {
        try {
            boolean exist = authenticationService.queryUserExist(phone);
            return AppResponse.success(exist);
        } catch (Exception e) {
            log.error("查询用户是否存在失败，手机号：{}", phone, e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "查询失败：" + e.getMessage());
        }
    }

    /**
     * 删除讯飞账号
     *
     * @param phone 手机号
     * @return 删除结果
     */
    @PostMapping("/iflytek-account/delete")
    public AppResponse<String> deleteIflytekAccount(@RequestParam @NotBlank(message = "手机号不能为空") String phone) {
        return AppResponse.error("当前部署模式不支持删除用户");
    }

    /**
     * 刷新Token
     * 使用 refreshToken 刷新 accessToken
     *
     * @param request HTTP请求
     * @return 刷新结果
     */
    @PostMapping("/refresh-token")
    public AppResponse<Boolean> refreshToken(
            @RequestParam("accessToken") String accessToken, HttpServletRequest request) {
        try {
            log.info("刷新Token请求");
            AppResponse<Boolean> response = authenticationService.refreshToken(request, accessToken);
            if (response.ok()) {
                log.info("刷新Token成功");
            } else {
                log.warn("刷新Token失败：{}", response.getMessage());
            }
            return response;
        } catch (Exception e) {
            log.error("刷新Token异常", e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "刷新Token异常：" + e.getMessage());
        }
    }

    /**
     * 修改密码
     * 验证旧密码后，更新为新密码
     *
     * @param changePasswordDto 修改密码请求参数（包含账号、手机号、旧密码、新密码、确认密码）
     * @return 修改结果
     */
    @PostMapping("/password/change")
    public AppResponse<String> changePassword(@RequestBody @Validated ChangePasswordDto changePasswordDto) {
        try {
            log.info("修改密码请求，账号：{}，手机号：{}", changePasswordDto.getLoginName(), changePasswordDto.getPhone());

            AppResponse<String> response = authenticationService.changePassword(changePasswordDto);
            if (response.ok()) {
                log.info("修改密码成功，账号：{}，临时凭证：{}", changePasswordDto.getLoginName(), response.getData());
            } else {
                log.warn("修改密码失败，账号：{}，错误：{}", changePasswordDto.getLoginName(), response.getMessage());
            }
            return response;
        } catch (UnsupportedOperationException e) {
            log.warn("当前部署模式不支持修改密码，账号：{}", changePasswordDto.getLoginName());
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "当前部署模式不支持修改密码");
        } catch (Exception e) {
            log.error("修改密码异常，账号：{}", changePasswordDto.getLoginName(), e);
            return AppResponse.error(com.iflytek.rpa.auth.utils.ErrorCodeEnum.E_SERVICE, "修改密码失败：" + e.getMessage());
        }
    }
}
