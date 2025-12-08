package com.iflytek.rpa.auth.controller;

import com.iflytek.rpa.auth.entity.ApplicationExtend;
import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.auth.entity.Result;
import com.iflytek.rpa.auth.service.ApplicationExtendService;
import com.iflytek.rpa.auth.service.AuthExtendService;
import com.iflytek.rpa.auth.utils.TokenManager;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.apache.oltu.oauth2.client.response.OAuthJSONAccessTokenResponse;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.entity.Permission;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.web.bind.annotation.*;

/**
 * @desc: 认证用户控制器
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/11 15:10
 */
@RestController
@RequestMapping("/user")
public class UserController {
    private static final Logger logger = LoggerFactory.getLogger(UserController.class);

    private final AuthService authService;
    private final ApplicationExtendService applicationExtendService;
    private final AuthExtendService authExtendService;
    private final String redirectUrl;

    @Value("${casdoor.endpoint}")
    private String endPoint;

    // 用于外部访问的endpoint（返回给前端的登录地址）
    @Value("${casdoor.external-endpoint}")
    private String externalEndPoint;

    public UserController(
            AuthService authService,
            ApplicationExtendService applicationExtendService,
            AuthExtendService authExtendService,
            @Value("${casdoor.redirect-url}") String redirectUrl) {
        this.authService = authService;
        this.applicationExtendService = applicationExtendService;
        this.authExtendService = authExtendService;
        this.redirectUrl = redirectUrl;
    }

    @GetMapping("/redirect-url")
    public Result getRedirectUrl() {
        try {
            String signinUrl = authExtendService.getCustomSigninUrl(redirectUrl);
            // 使用外部endpoint返回给前端，确保前端能访问到正确的地址
            return Result.success(externalEndPoint + signinUrl);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        }
    }

    @PostMapping("/sign/in")
    public Result signIn(
            @RequestParam("code") String code, @RequestParam("state") String state, HttpServletRequest request) {
        try {
            OAuthJSONAccessTokenResponse oAuthTokenResponse = authExtendService.getOAuthTokenResponse(code, state);
            String accessToken = oAuthTokenResponse.getAccessToken();
            String refreshToken = oAuthTokenResponse.getRefreshToken();
            String idToken = accessToken;
            // 动态获取系统内置证书，在initDataNewOnly为true时，证书会被篡改
            ApplicationExtend applicationWithKey = applicationExtendService.getApplicationWithKey("app-built-in");
            // 使用idToken解析用户信息（这是OIDC的核心：从id_token获取用户身份）
            User user = authExtendService.parseJwtTokenWithCertificate(idToken, applicationWithKey.certPublicKey);

            // 1. 将用户信息存储到session中（Spring Session自动管理Redis存储）
            HttpSession session = request.getSession();
            session.setAttribute("user", user);

            // 2. 设置Spring Security认证上下文
            CustomUserDetails userDetails = new CustomUserDetails(user);
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                    userDetails, null, AuthorityUtils.createAuthorityList("ROLE_USER"));
            authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authentication);

            // 3. accessToken和refreshToken存储到Redis，供服务端调用Casdoor API使用
            long tokenExpireTime = 24 * 60 * 60; // 24小时过期时间（秒）
            TokenManager.storeTokens(user.name, accessToken, refreshToken, tokenExpireTime);

            logger.info("用户 {} 登录成功，session和认证上下文已设置，服务端token已存储", user.name);
            return Result.success(user);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        } catch (IOException e) {
            logger.error("解析token异常", e);
            return Result.failure("解析token失败: " + e.getMessage());
        }
    }

    /**
     * Casdoor token登出接口
     * @param accessToken Casdoor颁发的accessToken
     * @return 登出结果
     */
    @PostMapping("/logout")
    public Result logout(@RequestParam("accessToken") String accessToken) {
        try {
            if (accessToken == null || accessToken.trim().isEmpty()) {
                return Result.failure("accessToken不能为空");
            }

            // 调用Casdoor的logout接口使token失效
            CasdoorResponse<String, Object> casdoorResponse = authExtendService.logout(accessToken);

            if (casdoorResponse != null && casdoorResponse.getStatus().equals("ok")) {
                logger.info("Token登出成功: {}", accessToken);
                return Result.success("登出成功");
            } else {
                logger.warn("Token登出失败: {}", casdoorResponse != null ? casdoorResponse.getMsg() : "未知错误");
                return Result.failure("登出失败: " + (casdoorResponse != null ? casdoorResponse.getMsg() : "未知错误"));
            }
        } catch (Exception exception) {
            logger.error("Token登出异常", exception);
            return Result.failure("登出失败: " + exception.getMessage());
        }
    }

    /**
     * 检查用户登录状态
     */
    @GetMapping("/login-check")
    public Result checkLoginStatus(HttpServletRequest request) {
        try {
            HttpSession session = request.getSession(false);
            if (session == null) {
                return Result.failure("未登录");
            }

            User user = (User) session.getAttribute("user");
            if (user == null) {
                return Result.failure("用户信息不存在");
            }

            // 检查服务端token是否还有效
            boolean hasToken = TokenManager.hasToken(user.name);
            if (!hasToken) {
                return Result.failure("服务端token已过期，请重新登录");
            }

            return Result.success(user);
        } catch (Exception exception) {
            logger.error("检查登录状态异常", exception);
            return Result.failure("检查登录状态失败: " + exception.getMessage());
        }
    }

    /**
     * 刷新服务端token（当accessToken过期时使用）
     */
    @PostMapping("/refresh-token")
    public Result refreshToken(HttpServletRequest request) {
        try {
            User user = (User) request.getSession().getAttribute("user");
            if (user == null) {
                return Result.failure("未登录");
            }

            String refreshToken = TokenManager.getRefreshToken(user.name);
            if (refreshToken == null) {
                return Result.failure("RefreshToken不存在，请重新登录");
            }

            // 使用refreshToken获取新的token
            OAuthJSONAccessTokenResponse newTokenResponse = authExtendService.refreshToken(refreshToken, "read");
            String newAccessToken = newTokenResponse.getAccessToken();
            String newRefreshToken = newTokenResponse.getRefreshToken();

            // 更新Redis中的token
            long tokenExpireTime = 24 * 60 * 60; // 24小时过期时间（秒）
            TokenManager.storeTokens(user.name, newAccessToken, newRefreshToken, tokenExpireTime);

            logger.info("用户 {} 的服务端token已刷新", user.name);
            return Result.success("Token刷新成功");
        } catch (Exception exception) {
            logger.error("刷新token异常", exception);
            return Result.failure("刷新token失败: " + exception.getMessage());
        }
    }

    @GetMapping("/now/userinfo")
    public Result nowUserinfo() throws NoLoginException {
        try {
            User casdoorUser = UserUtils.nowLoginUser();
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("登录出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/userinfo/{id}")
    public Result userinfo(@PathVariable("id") String id) {
        try {
            User casdoorUser = UserUtils.getUserInfoById(id);
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/login-status")
    public Result loginStatus() {
        try {
            boolean currentUserLogin = UserUtils.isCurrentUserLogin();
            return Result.success(currentUserLogin);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @PostMapping("/userinfo/page-list")
    public Result userPageList(@RequestBody List<String> userIdList) {
        try {
            if (userIdList == null || userIdList.isEmpty()) {
                return Result.failure("用户ID列表不能为空");
            }
            List<User> users = UserUtils.queryUserPageList(userIdList);
            return Result.success(users);
        } catch (Exception e) {
            logger.error("分页查询用户列表出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/now/permissions")
    public Result getCurrentUserPermissions() {
        try {
            List<Permission> permissions = UserUtils.getCurrentUserPermissionList();
            return Result.success(permissions);
        } catch (NoLoginException e) {
            logger.error("未登录，无法获取权限列表", e);
            return Result.failure("未登录，无法获取权限列表");
        } catch (Exception e) {
            logger.error("获取当前用户权限列表出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/userinfo/phone")
    public Result userinfoByPhone(@RequestParam("phone") String phone) {
        try {
            User casdoorUser = UserUtils.getUserInfoByPhone(phone);
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    /**
     * 获取当前用户的租户ID
     */
    @GetMapping("/now/tenant")
    public Result getCurrentTenantId() {
        try {
            String tenantId = TenantUtils.getTenantId();
            if (tenantId != null) {
                return Result.success(tenantId);
            } else {
                return Result.failure("无法获取租户ID，用户可能未登录");
            }
        } catch (Exception e) {
            logger.error("获取租户ID出错", e);
            return Result.failure("获取租户ID失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前用户的群组ID
     */
    @GetMapping("/now/group-id")
    public Result getCurrentGroupId() {
        try {
            String groupId = TenantUtils.getGroupId();
            if (groupId != null) {
                return Result.success(groupId);
            } else {
                return Result.failure("无法获取群组ID，用户可能未登录或未分配群组");
            }
        } catch (Exception e) {
            logger.error("获取群组ID出错", e);
            return Result.failure("获取群组ID失败: " + e.getMessage());
        }
    }

    /**
     * 根据用户名获取群组信息
     */
    @GetMapping("/group-info/username")
    public Result getGroupInfoByName(@RequestParam("username") String username) {
        try {
            if (username == null || username.trim().isEmpty()) {
                return Result.failure("用户名不能为空");
            }

            Group groupInfo = TenantUtils.getGroupInfoByName(username);
            if (groupInfo != null) {
                return Result.success(groupInfo);
            } else {
                return Result.failure("未找到用户 " + username + " 的群组信息");
            }
        } catch (Exception e) {
            logger.error("根据用户名获取群组信息出错: {}", username, e);
            return Result.failure("获取群组信息失败: " + e.getMessage());
        }
    }
}
