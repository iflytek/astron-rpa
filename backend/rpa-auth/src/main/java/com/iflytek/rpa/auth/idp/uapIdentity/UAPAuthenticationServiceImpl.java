package com.iflytek.rpa.auth.idp.uapIdentity;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.core.entity.ChangePasswordDto;
import com.iflytek.rpa.auth.core.entity.LoginDto;
import com.iflytek.rpa.auth.core.entity.RegisterDto;
import com.iflytek.rpa.auth.core.entity.Tenant;
import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.idp.AuthenticationService;
import com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant;
import com.iflytek.rpa.auth.sp.uap.constants.UAPConstant;
import com.iflytek.rpa.auth.sp.uap.dao.UserDao;
import com.iflytek.rpa.auth.sp.uap.mapper.TenantMapper;
import com.iflytek.rpa.auth.sp.uap.mapper.UserMapper;
import com.iflytek.rpa.auth.sp.uap.service.impl.UserServiceImpl;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.MenuPermissionValidator;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.rpa.auth.utils.SmsUtils;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.authentication.LoginResultDto;
import com.iflytek.sec.uap.client.core.dto.authentication.UapLoginByPasswordDto;
import com.iflytek.sec.uap.client.core.dto.pwd.UpdatePwdDto;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import com.iflytek.sec.uap.client.util.CommonValidateUtil;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.util.Base64Utils;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

/**
 * UAP认证服务实现
 * 用于私有化部署场景，企业没有自己的SSO时，使用内部UAP进行认证
 */
@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "private-uap")
public class UAPAuthenticationServiceImpl implements AuthenticationService {

    // 临时凭证缓存前缀和过期时间（10分钟）
    private static final String TEMP_TOKEN_PREFIX = "auth:temp_token:";
    private static final int TEMP_TOKEN_EXPIRE_SECONDS = 600;

    // 验证码缓存前缀和过期时间（10分钟）
    private static final String VERIFY_CODE_PREFIX = "auth:verify_code:";
    private static final int VERIFY_CODE_EXPIRE_SECONDS = 600;
    private final UserServiceImpl userServiceImpl;
    private final ObjectMapper objectMapper;
    private final TenantMapper tenantMapper;
    private final UserMapper userMapper;
    private final SmsUtils smsUtils;
    private final TenantService tenantService;

    private final UserDao userDao;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    /**
     * 构建UAP登录请求参数
     */
    private UapLoginByPasswordDto buildUapLoginByPasswordDto(LoginDto loginDto, String tenantId) {
        UapLoginByPasswordDto uapLoginByPasswordDto = new UapLoginByPasswordDto();
        uapLoginByPasswordDto.setAppCode(ClientConfigUtil.instance().getAppCode());
        uapLoginByPasswordDto.setService(ClientConfigUtil.instance().getRestServerUrl());
        uapLoginByPasswordDto.setRedirect(ClientConfigUtil.instance().getCasClientContext());
        uapLoginByPasswordDto.setLoginName(loginDto.getLoginName());
        uapLoginByPasswordDto.setPassword(loginDto.getPassword());
        uapLoginByPasswordDto.setReferer(ClientConfigUtil.instance().getRestServerUrl());
        if (StringUtils.hasText(tenantId)) {
            uapLoginByPasswordDto.setTenantId(tenantId);
        }
        return uapLoginByPasswordDto;
    }

    /**
     * 从临时凭证中获取LoginDto
     */
    private LoginDto getLoginDtoByTempToken(String tempToken) {
        if (!StringUtils.hasText(tempToken)) {
            return null;
        }

        try {
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedData = RedisUtils.get(cacheKey);

            if (cachedData == null) {
                log.warn("临时凭证已过期或无效，临时凭证：{}", tempToken);
                return null;
            }

            Map<String, Object> dataMap = objectMapper.readValue(
                    cachedData.toString(),
                    objectMapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class));

            if (dataMap.containsKey("loginDto")) {
                LoginDto loginDto = objectMapper.convertValue(dataMap.get("loginDto"), LoginDto.class);
                if (loginDto != null) {
                    return loginDto;
                }
            }

            log.warn("临时凭证中未找到登录信息，临时凭证：{}", tempToken);
            return null;

        } catch (Exception e) {
            log.error("获取登录信息异常，临时凭证：{}", tempToken, e);
            return null;
        }
    }

    @Override
    public String preAuthenticate(LoginDto loginDto, HttpServletRequest request) {
        try {
            // 判断是密码登录还是验证码登录
            boolean isCodeLogin =
                    StringUtils.hasText(loginDto.getCaptcha()) && StringUtils.hasText(loginDto.getPhone());
            String phone = loginDto.getPhone();
            String loginName = StringUtils.hasText(loginDto.getLoginName()) ? loginDto.getLoginName() : phone;

            // 如果前端使用手机号作为登录名，则根据手机号查询真实的登录名
            if (StringUtils.hasText(phone) && phone.equals(loginName)) {
                String loginNameByPhone = userDao.queryLoginNameByPhone(phone, databaseName);
                if (StringUtils.hasText(loginNameByPhone)) {
                    loginName = loginNameByPhone;
                }
            }
            // 将最终的登录名写回，确保后续流程使用一致的登录名
            loginDto.setLoginName(loginName);
            String scene = resolveScene(loginDto.getScene(), AuthenticationService.SCENE_LOGIN);

            if (isCodeLogin) {
                log.info("第一步：UAP预验证（验证码登录），手机号：{}", loginDto.getPhone());

                // 验证码登录：验证验证码
                if (!verifyCode(loginDto.getPhone(), loginDto.getCaptcha(), scene)) {
                    throw new RuntimeException("验证码错误或已失效");
                }

                // 验证码验证通过，需要根据手机号查找登录名
                // 如果loginDto中没有loginName，需要通过手机号查询UAP用户获取loginName
                if (!StringUtils.hasText(loginDto.getLoginName())) {
                    // 通过手机号查询用户登录名（这里需要调用UAP API查询）
                    // 暂时使用手机号作为登录名，实际应该查询UAP用户信息
                    loginDto.setLoginName(loginDto.getPhone());
                }

                log.info("验证码验证通过，手机号：{}，登录名：{}", loginDto.getPhone(), loginDto.getLoginName());
            } else {
                log.info("第一步：UAP预验证（密码登录），登录名：{}", loginName);

                // 密码登录：验证账号密码
                if (!StringUtils.hasText(loginDto.getPassword())) {
                    throw new RuntimeException("密码不能为空");
                }

                // 1. 查询租户列表，根据租户数量决定是否传入tenantId
                List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
                String tenantId = null;

                if (CollectionUtils.isEmpty(tenantList)) {
                    // 租户列表为空，账号异常
                    log.error("账号异常：根据登录名未找到租户信息，登录名：{}", loginName);
                    throw new RuntimeException("该账号异常，请联系系统管理员");
                } else if (tenantList.size() == 1) {
                    // 租户列表只有一个，传入租户ID
                    tenantId = tenantList.get(0).getId();
                    log.info("查询到单个租户，登录名：{}，租户ID：{}", loginName, tenantId);
                } else {
                    // 租户列表有多个，不传入tenantId
                    log.info("查询到多个租户，登录名：{}，租户数量：{}", loginName, tenantList.size());
                }

                // 2. 构建UAP登录请求参数
                UapLoginByPasswordDto uapLoginByPasswordDto = buildUapLoginByPasswordDto(loginDto, tenantId);

                // 3. 调用UAP登录接口验证账号密码
                ResponseDto<LoginResultDto> uapLoginByPasswordResponse =
                        ClientAuthenticationAPI.loginUapByPassword(uapLoginByPasswordDto);
                log.info(
                        "UAP登录响应：flag={}, message={}",
                        uapLoginByPasswordResponse != null ? uapLoginByPasswordResponse.isFlag() : false,
                        uapLoginByPasswordResponse != null ? uapLoginByPasswordResponse.getMessage() : "响应为空");

                // 4. 检查登录响应（成功即表示账号密码正确）
                if (uapLoginByPasswordResponse == null || !uapLoginByPasswordResponse.isFlag()) {
                    String errorMsg =
                            uapLoginByPasswordResponse != null ? uapLoginByPasswordResponse.getMessage() : "UAP登录响应为空";
                    log.error("UAP登录失败：{}", errorMsg);
                    throw new RuntimeException("登录失败：" + errorMsg);
                }

                log.info("账号密码验证通过，登录名：{}", loginName);
            }

            // 4. 生成临时凭证
            String tempToken = UUID.randomUUID().toString().replace("-", "");
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

            // 5. 构建缓存数据
            Map<String, Object> cacheData = new HashMap<>();
            cacheData.put("loginDto", loginDto); // 保存登录信息（验证码登录时密码为空）

            // 6. 将数据序列化为JSON并存储到Redis
            String cacheDataJson = objectMapper.writeValueAsString(cacheData);
            RedisUtils.set(cacheKey, cacheDataJson, TEMP_TOKEN_EXPIRE_SECONDS);

            log.info("第一步预验证成功，登录名：{}，临时凭证已生成，过期时间：{}秒", loginName, TEMP_TOKEN_EXPIRE_SECONDS);

            return tempToken;

        } catch (Exception e) {
            log.error("第一步预验证异常，登录名：{}", loginDto != null ? loginDto.getLoginName() : "未知", e);
            throw new RuntimeException("UAP预验证失败：" + e.getMessage(), e);
        }
    }

    @Override
    public User loginWithTenant(String tempToken, String tenantId, HttpServletRequest servletRequest) {
        try {
            log.info("第三步：UAP正式登录，临时凭证：{}，租户ID：{}", tempToken, tenantId);

            // 1. 验证参数
            if (!StringUtils.hasText(tempToken)) {
                throw new RuntimeException("临时凭证不能为空");
            }
            if (!StringUtils.hasText(tenantId)) {
                throw new RuntimeException("租户ID不能为空");
            }

            // 2. 从临时凭证中获取登录信息
            LoginDto loginDto = getLoginDtoByTempToken(tempToken);
            if (loginDto == null) {
                throw new RuntimeException("临时凭证已过期或无效");
            }
            loginDto.setTenantId(tenantId);

            // 从缓存中获取platform，如果为空则默认使用client
            String platform = loginDto.getPlatform();
            if (!StringUtils.hasText(platform)) {
                platform = (String) servletRequest.getSession().getAttribute(UAPConstant.SESSION_KEY_PLATFORM);
                if (!StringUtils.hasText(platform)) {
                    platform = "client";
                }
            }
            log.info("从缓存获取登录信息，登录名：{}，手机号：{}，平台：{}", loginDto.getLoginName(), loginDto.getPhone(), platform);

            // 3. 判断是密码登录还是验证码登录（无密码登录）
            UapUser uapUser;
            if (StringUtils.hasText(loginDto.getPassword())) {
                // 密码登录
                uapUser = userServiceImpl.loginUapByPasswordWithTenant(
                        loginDto.getLoginName(), loginDto.getPassword(), tenantId, servletRequest);
            } else if (StringUtils.hasText(loginDto.getPhone())) {
                // 验证码登录（无密码登录）
                log.info("使用验证码登录（无密码），手机号：{}", loginDto.getPhone());
                AppResponse<UapUser> loginResponse =
                        userServiceImpl.loginNoPasswordByPhone(loginDto.getPhone(), tenantId, servletRequest);

                if (loginResponse == null || !loginResponse.ok() || loginResponse.getData() == null) {
                    String errorMsg = loginResponse != null ? loginResponse.getMessage() : "无密码登录响应为空";
                    log.error("无密码登录失败：{}", errorMsg);
                    throw new RuntimeException("UAP登录失败：" + errorMsg);
                }

                uapUser = loginResponse.getData();
            } else {
                throw new RuntimeException("登录信息不完整：缺少密码或手机号");
            }

            if (uapUser == null) {
                throw new RuntimeException("UAP登录失败：未返回用户信息");
            }

            // 4. 将platform存储到session
            if (StringUtils.hasText(platform)) {
                servletRequest.getSession().setAttribute(UAPConstant.SESSION_KEY_PLATFORM, platform);
                log.debug("已存储登录平台到session，平台：{}", platform);
            }

            // 5. 处理单点登录：只有客户端登录才执行单点登录逻辑
            if (UAPConstant.PLATFORM_CLIENT.equals(platform)) {
                handleSingleSignOn(uapUser.getId(), servletRequest);
            } else {
                log.debug("非客户端登录（platform：{}），跳过单点登录处理，用户ID：{}", platform, uapUser.getId());
            }

            // 6. 删除临时凭证
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            RedisUtils.del(cacheKey);
            log.info("已删除临时凭证，cacheKey：{}", cacheKey);

            // 6. 转换为业务实体并返回
            User user = userMapper.fromUapUser(uapUser);

            log.info("第三步正式登录成功，用户ID：{}，登录名：{}，租户ID：{}", uapUser.getId(), uapUser.getLoginName(), tenantId);

            return user;

        } catch (Exception e) {
            log.error("第三步正式登录异常，临时凭证：{}，租户ID：{}", tempToken, tenantId, e);
            throw new RuntimeException("UAP正式登录失败：" + e.getMessage(), e);
        }
    }

    @Override
    @Deprecated
    public User login(LoginDto loginDto, HttpServletRequest servletRequest) {
        // 已废弃，使用两步登录
        return null;
    }

    @Override
    public LoginDto getLoginInfoByTempToken(String tempToken) {
        // TODO: 从缓存中获取用户登录信息
        throw new UnsupportedOperationException("获取登录信息功能待实现");
    }

    @Override
    public String getPhoneByTempToken(String tempToken) {
        try {
            LoginDto loginDto = getLoginDtoByTempToken(tempToken);
            if (loginDto == null) {
                throw new RuntimeException("临时凭证已过期或无效");
            }
            if (StringUtils.hasText(loginDto.getPhone())) {
                return loginDto.getPhone();
            }
            throw new RuntimeException("临时凭证中未找到手机号信息");
        } catch (Exception e) {
            log.error("获取手机号异常，临时凭证：{}", tempToken, e);
            throw new RuntimeException("获取手机号异常：" + e.getMessage(), e);
        }
    }

    @Override
    public AppResponse<List<Tenant>> getTenantList(String tempToken, HttpServletRequest request) {
        try {
            log.info("获取租户列表，临时凭证：{}", tempToken);

            String phone = null;
            String platform = null;

            // 从临时凭证中获取LoginDto，包含platform信息
            LoginDto loginDto = getLoginDtoByTempToken(tempToken);

            if (loginDto != null) {
                phone = loginDto.getPhone();
                platform = loginDto.getPlatform();
            }

            // 如果platform为空，默认使用client
            if (!StringUtils.hasText(platform)) {
                platform = (String) request.getSession().getAttribute(UAPConstant.SESSION_KEY_PLATFORM);
                if (!StringUtils.hasText(platform)) {
                    platform = "client";
                }
            }

            log.info("从临时凭证获取手机号：{}，平台：{}", phone, platform);

            // 调用租户服务获取租户列表
            AppResponse<List<Tenant>> response = tenantService.getTenantList(phone, request);

            if (!response.ok() || response.getData() == null) {
                return response;
            }

            List<Tenant> tenantList = response.getData();

            // 根据platform过滤租户列表
            // 如果platform是admin，过滤掉个人租户（tenantCode以PERSONAL_TENANT_CODE开头的）
            if (UAPConstant.PLATFORM_ADMIN.equals(platform)) {
                tenantList = tenantList.stream()
                        .filter(tenant -> {
                            if (tenant == null || tenant.getTenantCode() == null) {
                                return false;
                            }
                            // 过滤掉个人租户
                            return !tenant.getTenantCode().startsWith(UAPConstant.PERSONAL_TENANT_CODE);
                        })
                        .collect(java.util.stream.Collectors.toList());
                log.info("平台为admin，已过滤个人租户，剩余租户数量：{}", tenantList.size());
            }
            // 如果platform是client或invite，返回全部租户列表（不需要过滤）

            return AppResponse.success(tenantList);

        } catch (Exception e) {
            log.error("获取租户列表失败，临时凭证：{}", tempToken, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        }
    }

    @Override
    public String register(RegisterDto registerDto, HttpServletRequest request) {
        // TODO: 实现UAP注册逻辑
        throw new UnsupportedOperationException("UAP注册功能待实现");
    }

    @Override
    public User setPasswordAndLogin(String tempToken, String password, String tenantId, HttpServletRequest request) {
        // TODO: 实现UAP设置密码并登录逻辑
        throw new UnsupportedOperationException("UAP设置密码功能待实现");
    }

    @Override
    public boolean setPassword(String tempToken, String password, String tenantId, HttpServletRequest request) {
        // 企业SSO不支持设置密码
        throw new UnsupportedOperationException("UAP设置密码功能待实现");
    }

    @Override
    public boolean queryUserExist(String loginName) {
        String loginNameByPhone = userDao.queryLoginNameByPhone(loginName, databaseName);
        return StringUtils.hasText(loginNameByPhone);
    }

    @Override
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) {
        return userServiceImpl.logout(request, response);
    }

    @Override
    public AppResponse<Boolean> refreshToken(HttpServletRequest request, String accessToken) {
        return null;
    }

    /**
     * 获取验证码
     * 生成6位验证码，存储到Redis，并发送短信
     *
     * @param phone 手机号
     * @return 发送结果
     */
    @Override
    public String getVerificationCode(String phone, String scene) {
        try {
            if (!StringUtils.hasText(phone)) {
                throw new RuntimeException("手机号不能为空");
            }

            log.info("开始生成验证码，手机号：{}", phone);

            // 1. 生成6位随机验证码
            String code = String.format("%06d", (int) (Math.random() * 1000000));

            // 2. 存储到Redis（直接存储验证码字符串）
            String cacheKey = buildVerifyCodeKey(phone, scene);
            RedisUtils.set(cacheKey, code, VERIFY_CODE_EXPIRE_SECONDS);

            log.info("验证码已生成并存储到Redis，手机号：{}，验证码：{}，场景：{}，过期时间：{}秒", phone, code, scene, VERIFY_CODE_EXPIRE_SECONDS);

            // 4. 构建短信模板参数
            Map<String, Object> tpMap = new HashMap<>();
            tpMap.put("code", code);
            tpMap.put("time", VERIFY_CODE_EXPIRE_SECONDS);

            // 5. 发送短信
            AppResponse<?> smsResponse = smsUtils.sendSms(phone, smsUtils.tid, tpMap);
            if (smsResponse == null || !smsResponse.ok()) {
                log.error("发送验证码短信失败，手机号：{}，响应：{}", phone, smsResponse);
                throw new RuntimeException("发送验证码短信失败");
            }

            log.info("验证码发送成功，手机号：{}", phone);
            return "验证码已发送";

        } catch (Exception e) {
            log.error("获取验证码异常，手机号：{}", phone, e);
            throw new RuntimeException("获取验证码异常：" + e.getMessage(), e);
        }
    }

    @Override
    public String getVerificationCode(String phone) {
        return getVerificationCode(phone, AuthenticationService.SCENE_LOGIN);
    }

    /**
     * 验证验证码
     *
     * @param phone 手机号
     * @param code  验证码
     * @return 校验是否成功
     */
    public boolean verifyCode(String phone, String code, String scene) {
        if (!StringUtils.hasText(phone)) {
            throw new RuntimeException("手机号不能为空");
        }
        if (!StringUtils.hasText(code)) {
            throw new RuntimeException("验证码不能为空");
        }

        try {
            String cacheKey = buildVerifyCodeKey(phone, scene);

            // 1. 检查Redis中是否存在验证码
            if (!RedisUtils.hasKey(cacheKey)) {
                log.warn("验证码不存在或已过期，手机号：{}，场景：{}", phone, scene);
                return false;
            }

            // 2. 从Redis中获取验证码
            Object storedCode = RedisUtils.get(cacheKey);
            if (storedCode == null) {
                log.warn("验证码数据异常，手机号：{}，场景：{}", phone, scene);
                return false;
            }

            // 3. 比较验证码
            if (!code.equals(storedCode.toString())) {
                log.warn("验证码错误，手机号：{}，场景：{}", phone, scene);
                return false;
            }

            // 4. 验证成功，删除Redis中的验证码（确保只能使用一次）
            RedisUtils.del(cacheKey);
            log.info("验证码验证成功并已删除，手机号：{}，场景：{}", phone, scene);
            return true;

        } catch (Exception e) {
            log.error("验证验证码异常，手机号：{}", phone, e);
            throw new RuntimeException("验证验证码异常：" + e.getMessage(), e);
        }
    }

    private String buildVerifyCodeKey(String phone, String scene) {
        String normalizedScene = resolveScene(scene, AuthenticationService.SCENE_LOGIN);
        return VERIFY_CODE_PREFIX + normalizedScene + ":" + phone;
    }

    private String resolveScene(String scene, String defaultScene) {
        if (!StringUtils.hasText(scene)) {
            return defaultScene;
        }
        String normalized = scene.trim().toLowerCase();
        if (!AuthenticationService.SCENE_LOGIN.equals(normalized)
                && !AuthenticationService.SCENE_REGISTER.equals(normalized)
                && !AuthenticationService.SCENE_SET_PASSWORD.equals(normalized)) {
            return defaultScene;
        }
        return normalized;
    }

    @Override
    public AppResponse<Boolean> checkSession(HttpServletRequest request, HttpServletResponse response) {
        try {
            // 1. 先校验session是否有效（UAP的AuthenticationFilter已经校验了）
            // 这里只需要校验空间是否到期

            // 2. 从session中获取platform，只有客户端登录才校验单点登录
            String platform = (String) request.getSession().getAttribute(UAPConstant.SESSION_KEY_PLATFORM);
            boolean isClient = UAPConstant.PLATFORM_CLIENT.equals(platform);

            if (isClient) {
                // 校验单点登录：检查当前sessionId是否与Redis中存储的一致
                UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
                if (loginUser != null && StringUtils.hasText(loginUser.getId())) {
                    String userId = loginUser.getId();
                    String currentSessionId = request.getSession().getId();

                    if (StringUtils.hasText(currentSessionId)) {
                        String redisKey = RedisKeyConstant.REDIS_KEY_USER_SESSION_PREFIX + userId;
                        Object storedSessionIdObj = RedisUtils.get(redisKey);

                        if (storedSessionIdObj != null && StringUtils.hasText(storedSessionIdObj.toString())) {
                            String storedSessionId = storedSessionIdObj.toString();

                            // 如果当前sessionId与Redis中存储的不一致，说明在其他地方登录了
                            if (!storedSessionId.equals(currentSessionId)) {
                                log.warn(
                                        "检测到账号在其他地方登录，当前sessionId：{}，存储的sessionId：{}，用户ID：{}",
                                        currentSessionId,
                                        storedSessionId,
                                        userId);

                                // 清除当前session，强制退出登录
                                try {
                                    logout(request, response);
                                } catch (Exception e) {
                                    log.error("清除session失败", e);
                                }

                                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "账号已在其他地方登录，当前会话已失效");
                            }
                        }
                    }
                }
            } else {
                log.debug("非客户端登录（platform：{}），跳过单点登录校验", platform);
            }

            // 3. 校验空间是否到期
            boolean spaceExpired = tenantService.checkSpaceExpired(request);
            if (spaceExpired) {
                String tenantId = UapUserInfoAPI.getTenantId(request);
                log.warn("空间已到期，租户ID：{}，强制退出登录", tenantId);
                // 清除session，强制退出登录
                try {
                    logout(request, response);
                } catch (Exception e) {
                    log.error("清除session失败", e);
                }
                return AppResponse.error(ErrorCodeEnum.E_SPACE_EXPIRED, "空间已到期，请重新登录");
            }

            // 4. 如果是admin平台，校验菜单权限
            boolean isAdmin = UAPConstant.PLATFORM_ADMIN.equals(platform);
            if (isAdmin) {
                AppResponse<Boolean> menuPermissionResult = MenuPermissionValidator.checkMenuPermission(request);
                if (!menuPermissionResult.ok()) {
                    // 菜单权限验证失败，返回错误响应
                    return menuPermissionResult;
                }
            }

            // 5. session有效、单点登录校验通过、空间未到期且菜单权限验证通过，返回成功
            return AppResponse.success(true);
        } catch (Exception e) {
            log.error("检查session失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "检查session失败：" + e.getMessage());
        }
    }

    @Override
    public boolean checkLoginStatus(HttpServletRequest request) {
        try {
            // 使用UAP的API检查登录状态
            UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
            boolean tokenCheckResult = CommonValidateUtil.casCheckToken(request);
            boolean isLoggedIn = loginUser != null && tokenCheckResult;

            if (isLoggedIn) {
                log.debug("检查登录状态：已登录，用户名：{}", loginUser.getLoginName());
            } else {
                log.debug("检查登录状态：未登录");
            }

            return isLoggedIn;
        } catch (Exception e) {
            log.warn("检查登录状态异常：{}", e.getMessage());
            return false;
        }
    }

    @Override
    public AppResponse<String> changePassword(ChangePasswordDto changePasswordDto) {
        try {
            log.info("修改密码请求，账号：{}，手机号：{}", changePasswordDto.getLoginName(), changePasswordDto.getPhone());

            String phone = changePasswordDto.getPhone();
            String loginName = changePasswordDto.getLoginName();

            // 如果loginName为空或loginName等于phone，则根据phone查询真实的loginName
            if (!StringUtils.hasText(loginName) || (StringUtils.hasText(phone) && phone.equals(loginName))) {
                if (StringUtils.hasText(phone)) {
                    String loginNameByPhone = userDao.queryLoginNameByPhone(phone, databaseName);
                    if (StringUtils.hasText(loginNameByPhone)) {
                        loginName = loginNameByPhone;
                        log.info("根据手机号查询到登录名：{}，手机号：{}", loginName, phone);
                    } else {
                        log.warn("根据手机号未找到登录名，使用手机号作为登录名，手机号：{}", phone);
                        loginName = phone;
                    }
                } else {
                    throw new RuntimeException("登录名和手机号不能同时为空");
                }
            }

            // 直接调用UAP更新密码接口，UAP会校验旧密码是否正确
            UpdatePwdDto updatePwdDto = new UpdatePwdDto();
            updatePwdDto.setLoginName(loginName);
            updatePwdDto.setOldPwd(Base64Utils.encodeToString(
                    changePasswordDto.getOldPassword().getBytes(StandardCharsets.UTF_8)));
            updatePwdDto.setNewPwd(Base64Utils.encodeToString(
                    changePasswordDto.getNewPassword().getBytes(StandardCharsets.UTF_8)));

            ResponseDto<String> updatePwdResponse = ClientAuthenticationAPI.updateUserPwd(updatePwdDto);
            if (updatePwdResponse == null || !updatePwdResponse.isFlag()) {
                String errorMsg = updatePwdResponse != null ? updatePwdResponse.getMessage() : "更新密码响应为空";
                log.error("更新UAP密码失败：{}", errorMsg);
                throw new RuntimeException("更新密码失败：" + errorMsg);
            }

            log.info("修改密码成功，账号：{}，开始生成临时凭证", loginName);

            // 生成临时凭证，保存登录信息（包含新密码）
            String tempToken = UUID.randomUUID().toString().replace("-", "");
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

            // 构建LoginDto，包含登录名、手机号和新密码
            LoginDto loginDto = new LoginDto();
            loginDto.setLoginName(loginName);
            loginDto.setPhone(phone);
            loginDto.setPassword(changePasswordDto.getNewPassword());
            // platform可以从session中获取，如果没有则默认为client
            loginDto.setPlatform("client");

            // 构建缓存数据
            Map<String, Object> cacheData = new HashMap<>();
            cacheData.put("loginDto", loginDto);

            // 将数据序列化为JSON并存储到Redis
            String cacheDataJson = objectMapper.writeValueAsString(cacheData);
            RedisUtils.set(cacheKey, cacheDataJson, TEMP_TOKEN_EXPIRE_SECONDS);

            log.info("临时凭证已生成，账号：{}，过期时间：{}秒", loginName, TEMP_TOKEN_EXPIRE_SECONDS);
            return AppResponse.success(tempToken);

        } catch (Exception e) {
            log.error("修改密码异常，账号：{}", changePasswordDto != null ? changePasswordDto.getLoginName() : "未知", e);
            throw new RuntimeException("修改密码失败：" + e.getMessage(), e);
        }
    }

    /**
     * 处理单点登录：清除旧session，存储新sessionId
     *
     * @param userId 用户ID
     * @param request HTTP请求
     */
    private void handleSingleSignOn(String userId, HttpServletRequest request) {
        try {
            if (!StringUtils.hasText(userId)) {
                return;
            }

            // 获取当前sessionId
            String currentSessionId = request.getSession().getId();
            if (!StringUtils.hasText(currentSessionId)) {
                log.warn("无法获取sessionId，用户ID：{}", userId);
                return;
            }

            // Redis key: user:session:{userId}
            String redisKey = RedisKeyConstant.REDIS_KEY_USER_SESSION_PREFIX + userId;

            // 检查是否已有旧的sessionId
            Object oldSessionIdObj = RedisUtils.get(redisKey);
            if (oldSessionIdObj != null && StringUtils.hasText(oldSessionIdObj.toString())) {
                String oldSessionId = oldSessionIdObj.toString();

                // 如果旧sessionId与当前sessionId不同，清除旧session
                if (!oldSessionId.equals(currentSessionId)) {
                    log.info(
                            "检测到用户在其他地方登录，清除旧session，用户ID：{}，旧sessionId：{}，新sessionId：{}",
                            userId,
                            oldSessionId,
                            currentSessionId);

                    // 清除旧session（Spring Session在Redis中的key格式：uap:session:sessions:{sessionId}）
                    String oldSessionRedisKey = "uap:session:sessions:" + oldSessionId;
                    RedisUtils.del(oldSessionRedisKey);

                    // 清除旧session的过期key（Spring Session还会存储过期时间）
                    String oldSessionExpiresKey = "uap:session:sessions:expires:" + oldSessionId;
                    RedisUtils.del(oldSessionExpiresKey);
                }
            }

            // 存储新的sessionId映射（TTL设置为30天，与session过期时间保持一致或稍长）
            RedisUtils.set(redisKey, currentSessionId, 2592000); // 30天

            log.debug("单点登录session映射已更新，用户ID：{}，sessionId：{}", userId, currentSessionId);

        } catch (Exception e) {
            log.error("处理单点登录失败，用户ID：{}", userId, e);
            // 不抛出异常，避免影响登录流程
        }
    }
}
