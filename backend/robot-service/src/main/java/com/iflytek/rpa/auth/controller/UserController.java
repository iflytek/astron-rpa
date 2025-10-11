package com.iflytek.rpa.auth.controller;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.auth.entity.Result;
import com.iflytek.rpa.auth.service.AuthExtendService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.List;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.entity.Permission;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
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
    private final AuthExtendService authExtendService;
    private final String redirectUrl;

    public UserController(
            AuthService authService,
            AuthExtendService authExtendService,
            @Value("${casdoor.redirect-url}") String redirectUrl) {
        this.authService = authService;
        this.authExtendService = authExtendService;
        this.redirectUrl = redirectUrl;
    }

    @GetMapping("/api/redirect-url")
    public Result getRedirectUrl() {
        try {
            String signinUrl = authExtendService.getCustomSigninUrl(redirectUrl);
            return Result.success(signinUrl);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        }
    }

    @PostMapping("/api/signin")
    public Result signin(@RequestParam("code") String code, @RequestParam("state") String state) {
        try {
            String token = authService.getOAuthToken(code, state);
            return Result.success(token);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        }
    }

    @GetMapping("/api/userinfo")
    public Result userinfo(Authentication authentication) {
        CustomUserDetails customUserDetails = (CustomUserDetails) authentication.getPrincipal();
        User user = customUserDetails.getUser();
        return Result.success(user);
    }

    @GetMapping("/api/now/userinfo")
    public Result nowUserinfo() throws NoLoginException {
        try {
            User casdoorUser = UserUtils.nowLoginUser();
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("登录出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/api/userinfobyid")
    public Result userinfo(@RequestParam("id") String id) {
        try {
            User casdoorUser = UserUtils.getUserInfoById(id);
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/api/login-status")
    public Result loginStatus() {
        try {
            boolean currentUserLogin = UserUtils.isCurrentUserLogin();
            return Result.success(currentUserLogin);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @PostMapping("/api/user/page-list")
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

    @GetMapping("/api/user/permissions")
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

    @GetMapping("/api/userinfo/phone")
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
    @GetMapping("/api/tenant/id")
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
    @GetMapping("/api/tenant/group-id")
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
    @GetMapping("/api/tenant/group-info")
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
