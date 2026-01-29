package com.iflytek.rpa.auth.idp.casdoorIdentity;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.entity.enums.LoginTypeEnum;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.exception.ServiceException;
import com.iflytek.rpa.auth.idp.AuthenticationService;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorLoginDto;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorLoginResult;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorSignupDto;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorUserMapper;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorLoginExtendService;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorUserExtendService;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.RedisUtils;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor")
public class CasdoorAuthenticationServiceImpl implements AuthenticationService {

    private static final String TEMP_TOKEN_PREFIX = "auth:temp_token:";
    private static final int TEMP_TOKEN_EXPIRE_SECONDS = 600;

    @Value("${casdoor.endpoint}")
    private String endpoint;

    @Value("${casdoor.client-id}")
    private String clientId;

    @Value("${casdoor.client-secret}")
    private String clientSecret;

    @Value("${casdoor.organization-name}")
    private String organizationName;

    @Value("${casdoor.application-name}")
    private String applicationName;

    private final ObjectMapper objectMapper;
    private final CasdoorUserExtendService casdoorUserExtendService;
    private final CasdoorLoginExtendService casdoorLoginExtendService;
    private final CasdoorUserMapper casdoorUserMapper;
    private final TenantService tenantService;

    @Override
    public String preAuthenticate(LoginDto loginDto, HttpServletRequest request) {
        if (loginDto == null) {
            throw new ServiceException("登录参数不可为空");
        }

        String phone = loginDto.getPhone();
        String loginName = loginDto.getLoginName();

        if (!StringUtils.hasText(loginName) && !StringUtils.hasText(phone)) {
            throw new ServiceException("用户名或手机号不能为空");
        }
        if (!StringUtils.hasText(loginDto.getPassword())) {
            throw new ServiceException("密码不能为空");
        }

        try {
            log.info("Casdoor 预验证开始，用户名：{}，手机号：{}", loginName, phone);

            org.casbin.casdoor.entity.User casdoorUser;
            if (StringUtils.hasText(phone)) {
                casdoorUser = casdoorUserExtendService.getUserByPhone(phone);
            } else {
                casdoorUser = casdoorUserExtendService.getUser(loginName);
            }

            if (casdoorUser == null || !StringUtils.hasText(casdoorUser.name)) {
                log.warn("Casdoor 预验证失败：账号不存在，用户名：{}，手机号：{}", loginName, phone);
                throw new ServiceException("账号不存在，请先注册");
            }

            // 如果只传了手机号，用casdoor用户的name填充用户名
            if (!StringUtils.hasText(loginName)) {
                loginName = casdoorUser.name;
                loginDto.setLoginName(loginName);
            }
            // 补充手机号信息便于后续流程使用
            if (!StringUtils.hasText(phone) && StringUtils.hasText(casdoorUser.phone)) {
                phone = casdoorUser.phone;
                loginDto.setPhone(phone);
            }

            casdoorUser.password = loginDto.getPassword();
            boolean passwordValid = casdoorUserExtendService.checkUserPassword(casdoorUser);
            if (!passwordValid) {
                log.warn("Casdoor 预验证失败：密码错误，用户名：{}，手机号：{}", loginName, phone);
                throw new ServiceException("账号或密码错误");
            }

            String tempToken = UUID.randomUUID().toString().replace("-", "");
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

            // 缓存用户登录信息，后续正式登录时取出
            RedisUtils.set(cacheKey, objectMapper.writeValueAsString(loginDto), TEMP_TOKEN_EXPIRE_SECONDS);

            log.info("Casdoor 预验证成功，用户名：{}，手机号：{}，临时凭证已生成", loginName, phone);
            return tempToken;
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("Casdoor 预验证异常，参数：{}", loginDto, e);
            throw new ServiceException("Casdoor 预验证异常：" + e.getMessage());
        }
    }

    @Override
    public User loginWithTenant(String tempToken, String tenantId, HttpServletRequest servletRequest) {
        if (!StringUtils.hasText(tempToken)) {
            throw new ServiceException("临时凭证不能为空");
        }
        if (!StringUtils.hasText(tenantId)) {
            throw new ServiceException("租户ID不能为空");
        }

        try {
            log.info("开始Casdoor正式登录，临时凭证：{}，租户ID：{}", tempToken, tenantId);

            // 1. 从缓存中获取用户登录信息
            LoginDto loginDto = getLoginInfoByTempToken(tempToken);
            if (loginDto == null) {
                throw new ServiceException("临时凭证已过期或无效");
            }

            // 2. 构建Casdoor登录请求
            CasdoorLoginDto casdoorLoginDto = new CasdoorLoginDto();
            casdoorLoginDto.setApplication(applicationName);
            casdoorLoginDto.setOrganization(organizationName);
            casdoorLoginDto.setUsername(loginDto.getLoginName());
            casdoorLoginDto.setPassword(loginDto.getPassword());
            casdoorLoginDto.setType("login");
            casdoorLoginDto.setSigninMethod("Password");

            // 3. 调用Casdoor登录接口，获取用户ID和session cookie
            CasdoorLoginResult loginResult = casdoorLoginExtendService.login(casdoorLoginDto);
            if (loginResult == null || !StringUtils.hasText(loginResult.getUserId())) {
                throw new ServiceException("Casdoor登录失败：未获取到用户ID");
            }

            String userIdForCasdoor = loginResult.getUserId();
            String casdoorSessionId = loginResult.getSession();
            log.info("Casdoor登录成功，用户ID：{}，Session ID：{}", userIdForCasdoor, casdoorSessionId);

            // 4. 通过用户姓名获取用户详细信息
            String[] split = userIdForCasdoor.split("/");
            String name = split.length > 1 ? split[1] : "";
            org.casbin.casdoor.entity.User casdoorUser = casdoorUserExtendService.getUser(name);
            if (casdoorUser == null) {
                throw new ServiceException("获取用户信息失败：用户不存在");
            }

            // 5. 复用Casdoor返回的session，将用户信息设置到session中
            HttpSession session = servletRequest.getSession(true);
            session.setAttribute("user", casdoorUser);
            session.setAttribute("tenantId", tenantId);
            // 保存Casdoor的session ID，以便后续与Casdoor API交互时使用
            if (StringUtils.hasText(casdoorSessionId)) {
                session.setAttribute("casdoor_session_id", casdoorSessionId);
                log.info("Casdoor Session ID已保存到应用session中");
            }
            log.info("用户信息已设置到session，用户ID：{}，租户ID：{}", userIdForCasdoor, tenantId);

            // 6. 删除临时凭证
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            RedisUtils.del(cacheKey);

            // 7. 转换为通用User对象并返回
            User commonUser = casdoorUserMapper.toCommonUser(casdoorUser);
            log.info("Casdoor正式登录成功，用户ID：{}，租户ID：{}", userIdForCasdoor, tenantId);
            return commonUser;

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("Casdoor正式登录异常，临时凭证：{}，租户ID：{}", tempToken, tenantId, e);
            throw new ServiceException("Casdoor正式登录异常：" + e.getMessage());
        }
    }

    @Override
    public User login(LoginDto loginDto, HttpServletRequest servletRequest) {
        return null;
    }

    @Override
    public String getPhoneByTempToken(String tempToken) {
        return "";
    }

    @Override
    public LoginDto getLoginInfoByTempToken(String tempToken) {
        if (!StringUtils.hasText(tempToken)) {
            throw new ServiceException("临时凭证不能为空");
        }
        try {
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedUserInfo = RedisUtils.get(cacheKey);
            if (cachedUserInfo == null) {
                throw new ServiceException("临时凭证已过期或无效");
            }
            LoginDto loginDto = objectMapper.readValue(cachedUserInfo.toString(), LoginDto.class);
            return loginDto;
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取登录信息异常，临时凭证：{}", tempToken, e);
            throw new ServiceException("获取登录信息异常：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<Tenant>> getTenantList(String tempToken, HttpServletRequest request) {
        try {
            log.info("获取租户列表，临时凭证：{}", tempToken);

            // 从临时凭证中获取LoginDto
            //            LoginDto loginDto = getLoginInfoByTempToken(tempToken);

            return tenantService.getTenantList(organizationName, request);
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取租户列表失败，临时凭证：{}", tempToken, e);
            throw new ServiceException("获取租户列表失败：" + e.getMessage());
        }
    }

    @Override
    public String register(RegisterDto registerDto, HttpServletRequest request) {
        if (registerDto == null) {
            throw new ServiceException("注册参数不可为空");
        }

        if (!StringUtils.hasText(registerDto.getPassword())) {
            throw new ServiceException("密码不能为空");
        }

        // 验证两次密码是否一致
        if (!registerDto.getPassword().equals(registerDto.getConfirmPassword())) {
            throw new ServiceException("两次输入的密码不一致");
        }

        try {
            log.info("开始Casdoor注册，手机号：{}，用户名：{}", registerDto.getPhone(), registerDto.getLoginName());

            // 1. 构建Casdoor注册请求
            CasdoorSignupDto signupDto = new CasdoorSignupDto();
            signupDto.setApplication(applicationName);
            signupDto.setOrganization(organizationName);
            // 如果没有提供登录名，使用手机号作为登录名
            String username = StringUtils.hasText(registerDto.getLoginName())
                    ? registerDto.getLoginName()
                    : registerDto.getPhone();
            signupDto.setUsername(username);
            signupDto.setName(username); // name字段也使用用户名
            signupDto.setPassword(registerDto.getPassword());
            if (!StringUtils.isEmpty(registerDto.getPhone())) {
                signupDto.setPhone(registerDto.getPhone());
                // 默认手机号区域为CN
                signupDto.setCountryCode("CN");
            }

            // 2. 调用Casdoor注册接口
            CasdoorLoginResult signupResult = casdoorLoginExtendService.signup(signupDto);
            if (signupResult == null || !StringUtils.hasText(signupResult.getUserId())) {
                throw new ServiceException("Casdoor注册失败：未获取到用户ID");
            }

            // 3. 生成临时凭证并缓存注册信息
            String tempToken = UUID.randomUUID().toString().replace("-", "");
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

            // 从注册信息中提取登录信息，然后将登录信息和租户ID缓存，用于后续登入。(开源版租户只有一个)
            LoginDto loginDto = new LoginDto();
            loginDto.setLoginName(registerDto.getLoginName());
            loginDto.setPassword(registerDto.getPassword());
            loginDto.setLoginType(LoginTypeEnum.PASSWORD);
            loginDto.setTenantId(organizationName);
            loginDto.setScene("login");
            loginDto.setPlatform("client");

            RedisUtils.set(cacheKey, objectMapper.writeValueAsString(loginDto), TEMP_TOKEN_EXPIRE_SECONDS);

            String userId = signupResult.getUserId();
            log.info("Casdoor注册成功，用户ID：{}，手机号：{}，租户ID：{}", userId, registerDto.getPhone(), organizationName);
            return tempToken;

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("Casdoor注册异常，手机号：{}", registerDto.getPhone(), e);
            throw new ServiceException("Casdoor注册异常：" + e.getMessage());
        }
    }

    @Override
    public User setPasswordAndLogin(String tempToken, String password, String tenantId, HttpServletRequest request) {
        return null;
    }

    @Override
    public boolean queryUserExist(String loginName) {
        if (!StringUtils.hasText(loginName)) {
            return false;
        }

        try {
            log.debug("查询用户是否存在，登录名：{}", loginName);

            // 调用getUser查询用户是否存在
            org.casbin.casdoor.entity.User user = casdoorUserExtendService.getUser(loginName);
            boolean exists = user != null && StringUtils.hasText(user.name);

            log.debug("用户存在性查询结果，登录名：{}，存在：{}", loginName, exists);
            return exists;

        } catch (Exception e) {
            log.warn("查询用户是否存在异常，登录名：{}，异常：{}", loginName, e.getMessage());
            return false;
        }
    }

    @Override
    public boolean setPassword(String tempToken, String password, String tenantId, HttpServletRequest request) {
        return false;
    }

    @Override
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) {
        try {
            log.info("开始Casdoor登出");

            // 1. 从session中获取Casdoor session ID
            HttpSession session = request.getSession(false);
            String casdoorSessionId = null;
            if (session != null) {
                casdoorSessionId = (String) session.getAttribute("casdoor_session_id");
                if (StringUtils.hasText(casdoorSessionId)) {
                    log.info("从session中获取到Casdoor Session ID");
                }
            }
            //            //1.1 获取用户的access token
            //            String accessToken = null;
            //            if (session != null) {
            //                org.casbin.casdoor.entity.User user = (org.casbin.casdoor.entity.User)
            // session.getAttribute("user");
            //                if (user != null && StringUtils.hasText(user.name)) {
            //                    accessToken = TokenManager.getAccessToken(user.name);
            //                    if (StringUtils.hasText(accessToken)) {
            //                        log.info("从TokenManager获取到用户access token，username: {}", user.name);
            //                        // 清除Redis中的token
            //                        TokenManager.clearTokens(user.name);
            //                    } else {
            //                        log.warn("获取用户access token为空，可能token已过期或不存在，username: {}", user.name);
            //                    }
            //                }
            //            }

            // 2. 调用Casdoor登出接口
            if (StringUtils.hasText(casdoorSessionId)) {
                try {
                    casdoorLoginExtendService.logout(casdoorSessionId);
                    log.info("Casdoor登出接口调用成功");
                } catch (Exception e) {
                    log.warn("调用Casdoor登出接口失败，继续清除本地session: {}", e.getMessage());
                }
            } else {
                log.warn("未找到Casdoor Session ID，跳过Casdoor登出接口调用");
            }

            // 3. 清除应用自己的session
            if (session != null) {
                session.invalidate();
                log.info("应用session已清除");
            }

            log.info("Casdoor登出成功");
            return AppResponse.success("登出成功");

        } catch (Exception e) {
            log.error("Casdoor登出异常", e);
            // 即使出错也尝试清除session
            try {
                HttpSession session = request.getSession(false);
                if (session != null) {
                    session.invalidate();
                }
            } catch (Exception ex) {
                log.error("清除session失败", ex);
            }
            return AppResponse.error("登出异常：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<Boolean> refreshToken(HttpServletRequest request, String accessToken) {
        return null;
    }

    @Override
    public String getVerificationCode(String phone, String scene) {
        return "";
    }

    @Override
    public String getVerificationCode(String phone) {
        return getVerificationCode(phone, "login");
    }

    @Override
    public AppResponse<Boolean> checkSession(HttpServletRequest request, HttpServletResponse response) {
        // 从session中获取用户信息
        HttpSession session = request.getSession(false);
        if (Objects.isNull(session)) {
            return AppResponse.success(false);
        }

        org.casbin.casdoor.entity.User user = (org.casbin.casdoor.entity.User) session.getAttribute("user");
        if (Objects.isNull(user)) {
            return AppResponse.success(false);
        }

        return AppResponse.success(true);
    }

    @Override
    public boolean checkLoginStatus(HttpServletRequest request) {
        try {
            // 从session中获取用户信息
            HttpSession session = request.getSession(false);
            if (session == null) {
                log.debug("检查登录状态：session不存在");
                return false;
            }

            org.casbin.casdoor.entity.User user = (org.casbin.casdoor.entity.User) session.getAttribute("user");
            boolean isLoggedIn = user != null && StringUtils.hasText(user.name);

            log.debug("检查登录状态：{}", isLoggedIn);
            return isLoggedIn;

        } catch (Exception e) {
            log.warn("检查登录状态异常：{}", e.getMessage());
            return false;
        }
    }

    @Override
    public AppResponse<String> changePassword(ChangePasswordDto changePasswordDto) {
        return null;
    }

    @Override
    public AppResponse<String> addUser(AddUserDto user, HttpServletRequest request) {
        return null;
    }
}
