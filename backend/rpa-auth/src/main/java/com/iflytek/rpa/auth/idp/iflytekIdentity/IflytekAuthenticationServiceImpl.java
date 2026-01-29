package com.iflytek.rpa.auth.idp.iflytekIdentity;

import static com.iflytek.rpa.auth.sp.uap.constants.UAPConstant.DEFAULT_INITIAL_PASSWORD;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.acount.sdk.CAccountClient;
import com.iflytek.acount.sdk.CAccountResponse;
import com.iflytek.rpa.auth.blacklist.exception.ShouldBeBlackException;
import com.iflytek.rpa.auth.blacklist.service.PasswordErrorService;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.entity.ChangePasswordDto;
import com.iflytek.rpa.auth.core.entity.LoginDto;
import com.iflytek.rpa.auth.core.entity.RegisterDto;
import com.iflytek.rpa.auth.core.entity.Tenant;
import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.rpa.auth.core.entity.enums.LoginTypeEnum;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.exception.ServiceException;
import com.iflytek.rpa.auth.idp.AuthenticationService;
import com.iflytek.rpa.auth.idp.iflytekIdentity.dto.*;
import com.iflytek.rpa.auth.idp.iflytekIdentity.enums.IflytekLoginModeEnum;
import com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant;
import com.iflytek.rpa.auth.sp.uap.constants.UAPConstant;
import com.iflytek.rpa.auth.sp.uap.dao.TenantDao;
import com.iflytek.rpa.auth.sp.uap.dao.UserDao;
import com.iflytek.rpa.auth.sp.uap.mapper.UserMapper;
import com.iflytek.rpa.auth.sp.uap.service.impl.UserServiceImpl;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.MenuPermissionValidator;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.authentication.LoginTokenResponseDto;
import com.iflytek.sec.uap.client.core.dto.pwd.UpdatePwdDto;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import com.iflytek.sec.uap.client.util.CommonValidateUtil;
import com.iflytek.sec.uap.client.util.Oauth2Util;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.util.Base64Utils;
import org.springframework.util.CollectionUtils;
import org.springframework.util.DigestUtils;
import org.springframework.util.StringUtils;

@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "saas", matchIfMissing = true)
public class IflytekAuthenticationServiceImpl implements AuthenticationService {

    private final UserServiceImpl userService;

    private final UserMapper userMapper;

    private final UserDao userDao;

    private final PasswordErrorService passwordErrorService;

    @Value("${iflytek.account.host}")
    private String accountHost;

    @Value("${iflytek.account.appid}")
    private String appid;

    @Value("${iflytek.account.accessKey}")
    private String accessKey;

    @Value("${iflytek.account.accessSecret}")
    private String accessSecret;

    @Value("${rpa.auth.local-debug:false}")
    private boolean localDebug;

    @Value("${rpa.auth.local-ip:172.31.114.36}")
    private String localDebugIp;

    // 服务器IP地址，支持从环境变量或配置文件读取（K8s环境使用）
    @Value("${rpa.auth.server-ip:#{null}}")
    private String serverIp;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    private TenantDao tenantDao;

    @Autowired
    private TenantService tenantService;

    private static final int TIME_OUT = 10000;
    private static final boolean USE_AES_ENCRYPT = true;
    private static final String CHECK_LOGIN_ID_PATH = "/register/svr/checkLoginID";
    private static final String SEND_MSG_CODE_PATH = "/login/svr/sendMsgCode";
    private static final String REGISTER_SUBMIT_PATH = "/register/svr/submit";
    private static final String LOGIN_PATH = "/login/svr/aggrLogin";
    private static final String VERIFY_CODE_PATH = "/login/svr/checkCode";
    private static final String UPDATE_PASSWORD_PATH = "/userinfo/svr/update/pwd";
    private static final String DELETE_USER_PATH = "/logout/svr/delete";
    private static final String SYNC_USER_INFO_PATH = "/general/svr/syncUserInfo";
    private static final int DEFAULT_SMS_EXPIRE_SECONDS = 600;
    private static final String DEFAULT_COUNTRY_CODE = "86";
    private static final int DEFAULT_LOGIN_TYPE = 1;
    private static final String DEFAULT_PASSWORD_TYPE = "md5";

    // 临时凭证缓存前缀和过期时间（10分钟）
    private static final String TEMP_TOKEN_PREFIX = "auth:temp_token:";
    private static final int TEMP_TOKEN_EXPIRE_SECONDS = 600;

    // 验证码缓存前缀和过期时间（10分钟，与短信验证码过期时间一致）
    private static final String VERIFY_CODE_PREFIX = "auth:verify_code:";
    private final ObjectMapper objectMapper;
    private final IflytekAccountClientFactory accountClientFactory;

    // 讯飞账号客户端实例（单例复用，避免重复创建）
    private CAccountClient accountClient;

    @Override
    public String preAuthenticate(LoginDto loginDto, HttpServletRequest request) {
        if (loginDto == null) {
            throw new ServiceException("登录参数不可为空");
        }
        try {
            log.info("开始预验证，手机号：{}", loginDto.getPhone());

            // 1. 调用讯飞账号验证用户身份
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            IflytekLoginModeEnum loginMode = resolveLoginMode(loginDto);
            String scene = resolveScene(loginDto.getScene(), AuthenticationService.SCENE_LOGIN);

            if (loginMode == IflytekLoginModeEnum.FREE) {
                if (!verifyCode(loginDto.getPhone(), loginDto.getCaptcha(), scene)) {
                    throw new ServiceException("验证码错误或已失效");
                }
            }

            byte[] requestBody = buildLoginRequest(loginDto, traceId, loginMode);
            byte[] responseBytes = executePost(client, LOGIN_PATH, requestBody, "预验证");
            IflytekAccountResponse<IflytekLoginData> responseDto = parseResponse(responseBytes, IflytekLoginData.class);
            String respCode = responseDto.getCode();

            if ("000000".equals(respCode)) {
                IflytekLoginData data = responseDto.getData();
                if (data == null || !StringUtils.hasText(data.getUserid())) {
                    log.error("预验证失败，响应未返回有效用户信息");
                    throw new ServiceException("预验证失败：未返回用户信息");
                }

                // 2. 根据手机号验证用户是否在UAP存在，如果不存在则立即注册
                ensureUapUserExistsAndRegister(loginDto, data.getUserid(), request);

                // 3. 生成临时凭证并缓存用户信息
                String tempToken = UUID.randomUUID().toString().replace("-", "");
                String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

                // 缓存用户手机号和其他必要信息（JSON格式）
                String userInfo = objectMapper.writeValueAsString(loginDto);
                RedisUtils.set(cacheKey, userInfo, TEMP_TOKEN_EXPIRE_SECONDS);

                log.info("预验证成功，手机号：{}，临时凭证已生成", loginDto.getPhone());
                return tempToken;

            } else if ("720101".equals(respCode)) {
                log.warn("预验证失败：账号不存在，手机号 {}", loginDto.getPhone());
                throw new ServiceException("账号不存在，请先注册");
            } else if ("720102".equals(respCode)) {
                log.warn("预验证失败：密码错误，手机号 {}", loginDto.getPhone());

                // 记录密码错误，如果达到阈值会抛出 ShouldBeBlackException
                try {
                    String userId = getUserIdByPhone(loginDto.getPhone());
                    if (StringUtils.hasText(userId)) {
                        // 如果抛出 ShouldBeBlackException，直接向上传播，不会被 catch
                        passwordErrorService.recordPasswordError(userId, loginDto.getPhone());
                    }
                } catch (ShouldBeBlackException e) {
                    // 封禁异常直接向上抛出，让全局异常处理器处理
                    throw e;
                } catch (Exception e) {
                    // 其他异常（如获取userId失败）不影响主流程，记录日志即可
                    log.error("记录密码错误失败", e);
                }

                // 如果没有抛出 ShouldBeBlackException，说明未达到阈值，返回普通错误
                throw new ServiceException("账号或密码错误");
            }

            log.error("预验证失败，错误码：{}，错误信息：{}", respCode, responseDto.getDesc());
            throw new ServiceException("预验证失败：" + responseDto.getDesc());

        } catch (ShouldBeBlackException e) {
            // 封禁异常直接向上抛出，让全局异常处理器处理
            throw e;
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("预验证异常，参数：{}", loginDto, e);
            throw new ServiceException("预验证异常：" + e.getMessage());
        }
    }

    /**
     * 删除讯飞账号
     *
     * @param phone 手机号
     */
    public void deleteUser(String phone) {
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("手机号不能为空");
        }

        try {
            log.info("开始删除讯飞账号，手机号：{}", phone);

            // 1. 根据手机号获取讯飞账号的 userid（从 UAP 用户的 third_ext_info 字段获取）
            String iflytekUserId = getIflytekUserIdByPhone(phone);
            if (!StringUtils.hasText(iflytekUserId)) {
                throw new ServiceException("未找到该手机号对应的讯飞账号ID");
            }

            // 2. 调用讯飞账号删除接口
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildDeleteUserRequest(iflytekUserId, traceId);
            byte[] responseBytes = executePost(client, DELETE_USER_PATH, requestBody, "删除用户");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);
            String code = responseDto.getCode();

            if (isSuccessCode(code)) {
                log.info("删除讯飞账号成功，手机号：{}，userid：{}", phone, iflytekUserId);
                return;
            }

            if ("750101".equals(code)) {
                throw new ServiceException("用户不存在");
            }

            throw new ServiceException("删除用户失败：" + responseDto.getDesc());

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("删除讯飞账号异常，手机号：{}", phone, e);
            throw new ServiceException("删除讯飞账号异常：" + e.getMessage());
        }
    }

    /**
     * 根据手机号获取讯飞账号的 userid（从 UAP 用户的 third_ext_info 字段获取）
     *
     * @param phone 手机号
     * @return 讯飞账号的 userid
     */
    private String getIflytekUserIdByPhone(String phone) {
        try {
            // 直接查询数据库获取 third_ext_info
            String thirdExtInfo = userDao.queryThirdExtInfoByPhone(phone, databaseName);

            if (!StringUtils.hasText(thirdExtInfo)) {
                log.warn("用户未绑定讯飞账号ID，手机号：{}", phone);
                return null;
            }

            return thirdExtInfo;

        } catch (Exception e) {
            log.error("获取讯飞账号ID失败，手机号：{}", phone, e);
            return null;
        }
    }

    /**
     * 根据手机号获取用户ID
     *
     * @param phone 手机号
     * @return 用户ID
     */
    private String getUserIdByPhone(String phone) {
        try {
            String userId = userDao.getUserIdByPhone(phone, databaseName);
            if (!StringUtils.hasText(userId)) {
                log.warn("未找到用户，手机号：{}", phone);
                return null;
            }
            return userId;
        } catch (Exception e) {
            log.error("获取用户ID失败，手机号：{}", phone, e);
            return null;
        }
    }

    /**
     * 同步存量用户数据
     *
     * @param userid        用户ID
     * @param password      密码（可为空）
     * @param loginAccounts 登录账号列表
     * @param userInfo      用户详细信息
     */
    public void syncUserInfo(
            String userid,
            String password,
            List<IflytekSyncUserInfoAccount> loginAccounts,
            IflytekSyncUserInfoUserInfo userInfo) {
        if (!StringUtils.hasText(userid)) {
            throw new ServiceException("用户ID不能为空");
        }
        if (loginAccounts == null || loginAccounts.isEmpty()) {
            throw new ServiceException("登录账号列表不能为空");
        }

        try {
            log.info("开始同步用户信息，用户ID：{}", userid);

            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildSyncUserInfoRequest(userid, password, loginAccounts, userInfo, traceId);
            byte[] responseBytes = executePost(client, SYNC_USER_INFO_PATH, requestBody, "同步用户信息");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);
            String code = responseDto.getCode();

            if ("000000".equals(code)) {
                log.info("同步用户信息成功，用户ID：{}", userid);
                return;
            }

            if ("740103".equals(code)) {
                log.warn("同步用户信息失败：用户已存在，用户ID {}", userid);
                throw new ServiceException("用户已存在");
            }

            if ("740101".equals(code)) {
                log.warn("同步用户信息失败：登录方式重复，用户ID {}", userid);
                throw new ServiceException("登录方式重复");
            }

            log.error("同步用户信息失败，错误码：{}，错误信息：{}", code, responseDto.getDesc());
            throw new ServiceException("同步用户信息失败：" + responseDto.getDesc());

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("同步用户信息异常，用户ID：{}", userid, e);
            throw new ServiceException("同步用户信息异常：" + e.getMessage());
        }
    }

    /**
     * 修改密码
     *
     * @param changePasswordDto 修改密码请求参数
     */
    public void updatePassword(ChangePasswordDto changePasswordDto) {
        if (changePasswordDto == null) {
            throw new ServiceException("修改密码参数不可为空");
        }
        String phone = changePasswordDto.getPhone();
        String oldPassword = changePasswordDto.getOldPassword();
        String newPassword = changePasswordDto.getNewPassword();
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("手机号不能为空");
        }
        if (!StringUtils.hasText(oldPassword) || !StringUtils.hasText(newPassword)) {
            throw new ServiceException("密码不能为空");
        }
        if (oldPassword.equals(newPassword)) {
            throw new ServiceException("新密码不能与原密码一致");
        }
        try {
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            String oldPwdMd5 = toMd5Hex(oldPassword);
            String newPwdMd5 = toMd5Hex(newPassword);
            byte[] requestBody = buildUpdatePasswordRequest(phone, traceId, oldPwdMd5, newPwdMd5);
            byte[] responseBytes = executePost(client, UPDATE_PASSWORD_PATH, requestBody, "修改密码");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);
            String code = responseDto.getCode();
            if (isSuccessCode(code)) {
                log.info("修改密码成功，手机号：{}", phone);
                return;
            }
            if ("0100100".equals(code)) {
                throw new ServiceException("修改密码失败：参数错误");
            }
            if ("0402200".equals(code)) {
                throw new ServiceException("账号不存在");
            }
            throw new ServiceException("修改密码失败：" + responseDto.getDesc());
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("修改密码异常，手机号：{}", changePasswordDto.getPhone(), e);
            throw new ServiceException("修改密码异常：" + e.getMessage());
        }
    }

    /**
     * 管理端根据登录名更新用户密码
     *
     * @param loginName   登录名
     * @param oldPassword 旧密码
     * @param newPassword 新密码
     */
    public void updateUserPassword(String loginName, String oldPassword, String newPassword) {
        if (!StringUtils.hasText(loginName)) {
            throw new ServiceException("用户名不能为空");
        }
        String phone = userDao.queryPhoneByLoginName(loginName, databaseName);
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("未找到该用户或手机号为空");
        }

        // 更新讯飞账号密码
        updateIflytekPassword(phone, newPassword);

        // 更新 UAP 密码
        UpdatePwdDto updatePwdDto = new UpdatePwdDto();
        updatePwdDto.setLoginName(loginName);
        updatePwdDto.setOldPwd(Base64Utils.encodeToString(oldPassword.getBytes(StandardCharsets.UTF_8)));
        updatePwdDto.setNewPwd(Base64Utils.encodeToString(newPassword.getBytes(StandardCharsets.UTF_8)));

        ResponseDto<String> response = ClientAuthenticationAPI.updateUserPwd(updatePwdDto);
        if (!response.isFlag()) {
            throw new ServiceException("更新UAP密码失败：" + response.getMessage());
        }

        // 更新 ext_info 为 null
        try {
            userDao.updateExtInfo(phone, null, databaseName);
            log.info("已更新用户 ext_info 为 null，登录名：{}", loginName);
        } catch (Exception e) {
            log.error("更新用户 ext_info 失败，登录名：{}", loginName, e);
            // 不抛出异常，因为密码更新已经成功，只是扩展信息更新失败
        }

        log.info("管理员更新用户密码成功，登录名：{}", loginName);
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
            log.info("开始正式登录，临时凭证：{}，租户ID：{}", tempToken, tenantId);

            // 1. 从缓存中获取用户信息
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

            LoginDto loginDto = getLoginInfoByTempToken(tempToken);
            loginDto.setTenantId(tenantId);

            // 从缓存中获取platform，如果为空则默认使用client
            String platform = loginDto.getPlatform();
            if (!StringUtils.hasText(platform)) {
                platform = "client";
            }
            log.info("从缓存获取平台：{}", platform);

            // 2. 同步到UAP并建立session（用户已在预验证阶段注册）
            UapUser uapUser = syncAndLoginUap(loginDto, servletRequest);
            // 更新租户用户的最后登录时间
            String tenantUserId = tenantDao.getTenantUserId(databaseName, uapUser.getId(), tenantId);
            tenantDao.updateLoginTime(databaseName, tenantUserId);

            // 3. 将platform存储到session
            if (StringUtils.hasText(platform)) {
                servletRequest.getSession().setAttribute(UAPConstant.SESSION_KEY_PLATFORM, platform);
                log.debug("已存储登录平台到session，平台：{}", platform);
            }

            // 4. 登录成功，清除密码错误计数
            try {
                passwordErrorService.clearPasswordError(uapUser.getId());
            } catch (Exception e) {
                log.error("清除密码错误计数失败", e);
            }

            // 5. 处理单点登录：只有客户端登录才执行单点登录逻辑
            if (UAPConstant.PLATFORM_CLIENT.equals(platform)) {
                handleSingleSignOn(uapUser.getId(), servletRequest);
            } else {
                log.debug("非客户端登录（platform：{}），跳过单点登录处理，用户ID：{}", platform, uapUser.getId());
            }

            // 6. 删除临时凭证
            RedisUtils.del(cacheKey);

            log.info("正式登录成功，用户ID：{}，租户ID：{}", uapUser.getId(), tenantId);
            return userMapper.fromUapUser(uapUser);

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("正式登录异常，临时凭证：{}", tempToken, e);
            throw new ServiceException("正式登录异常：" + e.getMessage());
        }
    }

    private LoginDto getLoginDtoByTempToken(String tempToken) {
        // 委托给公共接口方法
        return getLoginInfoByTempToken(tempToken);
    }

    @Override
    public LoginDto getLoginInfoByTempToken(String tempToken) {
        if (!StringUtils.hasText(tempToken)) {
            return null;
        }

        try {
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedUserInfo = RedisUtils.get(cacheKey);

            if (cachedUserInfo == null) {
                throw new ServiceException("临时凭证已过期或无效");
            }

            LoginDto loginDto = objectMapper.readValue(cachedUserInfo.toString(), LoginDto.class);
            if (loginDto.getPhone() == null) {
                Map<String, Object> dataMap = objectMapper.readValue(
                        cachedUserInfo.toString(),
                        objectMapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class));

                RegisterDto registerDto = objectMapper.convertValue(dataMap.get("registerDto"), RegisterDto.class);
                loginDto.setPhone(registerDto.getPhone());
            }

            return loginDto;

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取登录信息异常，临时凭证：{}", tempToken, e);
            throw new ServiceException("获取登录信息异常：" + e.getMessage());
        }
    }

    @Override
    public String getPhoneByTempToken(String tempToken) {
        if (!StringUtils.hasText(tempToken)) {
            return null;
        }

        try {
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedUserInfo = RedisUtils.get(cacheKey);

            if (cachedUserInfo == null) {
                throw new ServiceException("临时凭证已过期或无效");
            }

            LoginDto loginDto = objectMapper.readValue(cachedUserInfo.toString(), LoginDto.class);
            if (loginDto.getPhone() == null) {
                Map<String, Object> dataMap = objectMapper.readValue(
                        cachedUserInfo.toString(),
                        objectMapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class));

                RegisterDto registerDto = objectMapper.convertValue(dataMap.get("registerDto"), RegisterDto.class);
                loginDto.setPhone(registerDto.getPhone());
            }

            return loginDto.getPhone();

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取手机号异常，临时凭证：{}", tempToken, e);
            throw new ServiceException("获取手机号异常：" + e.getMessage());
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

        } catch (ServiceException e) {
            log.error("获取租户列表失败，临时凭证：{}", tempToken, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        } catch (Exception e) {
            log.error("获取租户列表异常，临时凭证：{}", tempToken, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        }
    }

    @Override
    @Deprecated
    public User login(LoginDto loginDto, HttpServletRequest servletRequest) {
        if (loginDto == null) {
            throw new ServiceException("登录参数不可为空");
        }
        try {
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            IflytekLoginModeEnum loginMode = resolveLoginMode(loginDto);
            if (loginMode == IflytekLoginModeEnum.FREE) {
                String scene = resolveScene(loginDto.getScene(), AuthenticationService.SCENE_LOGIN);
                if (!verifyCode(loginDto.getPhone(), loginDto.getCaptcha(), scene)) {
                    throw new ServiceException("验证码错误或已失效");
                }
                // ensurePhoneRegistered(loginDto.getPhone());
            }
            byte[] requestBody = buildLoginRequest(loginDto, traceId, loginMode);
            byte[] responseBytes = executePost(client, LOGIN_PATH, requestBody, "账号登录");
            IflytekAccountResponse<IflytekLoginData> responseDto = parseResponse(responseBytes, IflytekLoginData.class);
            String respCode = responseDto.getCode();
            if ("000000".equals(respCode)) {
                IflytekLoginData data = responseDto.getData();
                if (data == null || !StringUtils.hasText(data.getUserid())) {
                    log.error("账号登录失败，响应未返回有效用户信息");
                    throw new ServiceException("账号登录失败：未返回用户信息");
                }

                UapUser uapUser = syncAndLoginUap(loginDto, servletRequest);

                return userMapper.fromUapUser(uapUser);
            } else if ("720101".equals(respCode)) {
                log.warn("账号登录失败：账号不存在，手机号 {}", loginDto.getPhone());
                throw new ServiceException("账号不存在，请先注册");
            } else if ("720102".equals(respCode)) {
                log.warn("账号登录失败：密码错误，手机号 {}", loginDto.getPhone());
                throw new ServiceException("账号或密码错误");
            }
            log.error("账号登录失败，错误码：{}，错误信息：{}", respCode, responseDto.getDesc());
            throw new ServiceException("账号登录失败：" + responseDto.getDesc());
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("账号登录异常，参数：{}", loginDto, e);
            throw new ServiceException("账号登录异常：" + e.getMessage());
        }
    }

    private UapUser syncAndLoginUap(LoginDto loginDto, HttpServletRequest servletRequest) {
        ensureUapTenant(loginDto, servletRequest);
        // 验证用户是否拥有该租户
        validateTenantPermission(loginDto);
        return loginUapByPhone(loginDto, servletRequest);
    }

    /**
     * 验证用户是否拥有该租户权限
     * 根据手机号查询登录账号，根据登录账号查询租户列表，验证当前登录的租户id是否在所属列表
     *
     * @param loginDto 登录信息
     * @throws ServiceException 如果验证失败则抛出异常
     */
    private void validateTenantPermission(LoginDto loginDto) {
        String phone = loginDto.getPhone();
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("手机号不能为空");
        }
        if (!StringUtils.hasText(loginDto.getTenantId())) {
            throw new ServiceException("租户ID不能为空");
        }

        // 根据手机号查询登录账号
        String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
        if (!StringUtils.hasText(loginName)) {
            log.warn("根据手机号未找到用户登录名，手机号：{}", phone);
            loginName = phone;
        }

        // 根据登录账号查询租户列表
        List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
        if (CollectionUtils.isEmpty(tenantList)) {
            log.warn("根据登录名未找到租户信息，登录名：{}", loginName);
            throw new ServiceException("当前空间权限校验失败，请重新登录");
        }

        // 验证当前登录的租户id是否在所属列表
        boolean hasPermission =
                tenantList.stream().anyMatch(tenant -> loginDto.getTenantId().equals(tenant.getId()));

        if (!hasPermission) {
            log.warn("用户没有该租户权限，登录名：{}，租户ID：{}", loginName, loginDto.getTenantId());
            throw new ServiceException("当前空间权限校验失败，请重新登录");
        }
    }

    /**
     * 在预验证阶段检查用户是否在UAP存在，如果不存在则立即注册
     *
     * @param loginDto      登录信息
     * @param iflytekUserId 讯飞账号的userId
     * @param request       HTTP请求（用于注册UAP用户）
     */
    private void ensureUapUserExistsAndRegister(LoginDto loginDto, String iflytekUserId, HttpServletRequest request) {
        String phone = loginDto.getPhone();
        if (!StringUtils.hasText(phone)) {
            return;
        }

        // 根据手机号查询用户登录名，判断用户是否存在
        String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
        if (!StringUtils.hasText(loginName)) {
            // 用户不存在，立即注册到UAP
            log.info("用户不存在于UAP，开始注册，手机号：{}，讯飞账号userId：{}", phone, iflytekUserId);

            RegisterDto registerDto = RegisterDto.builder()
                    .phone(phone)
                    .loginName(phone) // 默认使用手机号作为登录名
                    .password(null) // 预验证阶段不需要密码
                    .build();

            AppResponse<String> registerResponse = userService.register(registerDto, request);
            if (registerResponse == null || !registerResponse.ok()) {
                String message = registerResponse == null ? "注册失败：UAP未返回响应" : registerResponse.getMessage();
                log.error("注册UAP用户失败，手机号：{}，错误：{}", phone, message);
                throw new ServiceException("注册UAP用户失败：" + message);
            }

            // 将讯飞账号的userId保存到UAP用户的third_ext_info字段
            if (StringUtils.hasText(iflytekUserId)) {
                try {
                    userDao.updateThirdExtInfo(phone, iflytekUserId, databaseName);
                    log.info("已保存讯飞账号userId到UAP用户扩展字段，登录名：{}，userId：{}", phone, iflytekUserId);
                } catch (Exception e) {
                    log.error("保存讯飞账号userId到UAP用户扩展字段失败，登录名：{}，userId：{}", phone, iflytekUserId, e);
                    // 不抛出异常，因为注册已经成功，只是扩展信息保存失败
                }
            }

            log.info("UAP用户注册成功，手机号：{}，租户ID：{}", phone, registerResponse.getData());
        } else {
            log.debug("用户已存在于UAP，登录名：{}，手机号：{}", loginName, phone);
        }
    }

    private void ensureUapTenant(LoginDto loginDto, HttpServletRequest servletRequest) {
        if (StringUtils.hasText(loginDto.getTenantId())) {
            return;
        }
        RegisterDto registerDto = RegisterDto.builder()
                .phone(loginDto.getPhone())
                .password(loginDto.getPassword())
                .build();
        AppResponse<String> registerResponse = userService.register(registerDto, servletRequest);
        if (registerResponse == null || !registerResponse.ok()) {
            String message = registerResponse == null ? "注册失败：UAP未返回响应" : registerResponse.getMessage();
            throw new ServiceException(message);
        }
        loginDto.setTenantId(registerResponse.getData());
    }

    private UapUser loginUapByPhone(LoginDto loginDto, HttpServletRequest servletRequest) {
        AppResponse<UapUser> loginResponse =
                userService.loginNoPasswordByPhone(loginDto.getPhone(), loginDto.getTenantId(), servletRequest);
        if (loginResponse == null || !loginResponse.ok() || loginResponse.getData() == null) {
            log.error("账号登录失败，UAP未返回有效用户信息");
            throw new ServiceException("账号登录失败：UAP未返回用户信息");
        }
        return loginResponse.getData();
    }

    @Override
    public String register(RegisterDto registerDto, HttpServletRequest request) {
        if (registerDto == null) {
            throw new ServiceException("注册参数不可为空");
        }

        if (!StringUtils.hasText(registerDto.getPhone())) {
            throw new ServiceException("手机号不能为空");
        }

        // 验证码校验
        if (StringUtils.hasText(registerDto.getCaptcha())) {
            if (!verifyCode(registerDto.getPhone(), registerDto.getCaptcha(), AuthenticationService.SCENE_REGISTER)) {
                throw new ServiceException("验证码错误或已失效");
            }
        } else {
            throw new ServiceException("验证码不能为空");
        }

        try {
            log.info("开始注册，手机号：{}", registerDto.getPhone());

            // 1. 在讯飞账号注册（使用空密码）
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildRegisterRequest(registerDto, traceId);
            byte[] responseBytes = executePost(client, REGISTER_SUBMIT_PATH, requestBody, "提交注册");
            IflytekAccountResponse<IflytekRegisterData> responseDto =
                    parseResponse(responseBytes, IflytekRegisterData.class);
            String respCode = responseDto.getCode();

            if ("000000".equals(respCode) || "00000".equals(respCode)) {
                if (responseDto.getData() == null
                        || !StringUtils.hasText(responseDto.getData().getUserid())) {
                    log.warn("注册成功但未返回userid");
                    throw new ServiceException("注册失败：未返回用户ID");
                }

                String iflytekUserId = responseDto.getData().getUserid();
                String phone = registerDto.getPhone();
                String tenantId;

                // 2. 检查UAP中是否已存在该用户
                String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
                if (StringUtils.hasText(loginName)) {
                    // 用户已存在，查询租户列表并选择第一个
                    log.info("用户已存在于UAP，查询租户列表，登录名：{}", loginName);
                    List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
                    if (CollectionUtils.isEmpty(tenantList)) {
                        log.warn("用户已存在但没有租户信息，登录名：{}，将执行注册逻辑", loginName);
                        // 没有租户，走注册逻辑创建新租户
                        tenantId = registerUapUser(registerDto, request);
                    } else {
                        // 选择第一个租户
                        tenantId = tenantList.get(0).getId();
                        log.info("用户已存在，选择第一个租户，登录名：{}，租户ID：{}", loginName, tenantId);
                    }
                } else {
                    // 用户不存在，执行注册逻辑
                    log.info("用户不存在于UAP，开始注册，手机号：{}", phone);
                    tenantId = registerUapUser(registerDto, request);
                }

                // 2.1 将讯飞账号的 userId 存储到 UAP 用户的 third_ext_info 字段
                String finalLoginName = StringUtils.hasText(loginName) ? loginName : phone;
                try {
                    userDao.updateThirdExtInfo(finalLoginName, iflytekUserId, databaseName);
                    log.info("已保存讯飞账号 userId 到 UAP 用户扩展字段，登录名：{}，userId：{}", finalLoginName, iflytekUserId);
                } catch (Exception e) {
                    log.error("保存讯飞账号 userId 到 UAP 用户扩展字段失败，登录名：{}，userId：{}", finalLoginName, iflytekUserId, e);
                    // 不抛出异常，因为注册已经成功，只是扩展信息保存失败
                }

                // 3. 生成临时凭证并缓存注册信息
                String tempToken = UUID.randomUUID().toString().replace("-", "");
                String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

                // 将注册信息和租户ID缓存（用于后续设置密码）
                registerDto.setPassword(null); // 清空密码字段，只缓存必要信息

                // 缓存租户ID和注册信息
                String cacheData = objectMapper.writeValueAsString(new HashMap<String, Object>() {
                    {
                        put("registerDto", registerDto);
                        put("tenantId", tenantId);
                    }
                });

                RedisUtils.set(cacheKey, cacheData, TEMP_TOKEN_EXPIRE_SECONDS);

                log.info("注册成功，手机号：{}，临时凭证已生成，租户ID：{}", registerDto.getPhone(), tenantId);
                return tempToken;

            } else if ("710201".equals(respCode)) {
                log.warn("提交注册失败：手机号格式不正确，手机号 {}", registerDto.getPhone());
                throw new ServiceException("手机号格式不正确");
            } else if ("710203".equals(respCode)) {
                log.warn("提交注册失败：账号已注册，手机号 {}", registerDto.getPhone());
                throw new ServiceException("账号已注册");
            }

            log.error("提交注册失败，错误码：{}，错误信息：{}", respCode, responseDto.getDesc());
            throw new ServiceException("提交注册失败：" + responseDto.getDesc());

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("提交注册异常，注册参数：{}", registerDto, e);
            throw new ServiceException("提交注册异常：" + e.getMessage());
        }
    }

    public String registerWithoutCaptcha(RegisterDto registerDto, HttpServletRequest request) {
        if (registerDto == null) {
            throw new ServiceException("注册参数不可为空");
        }

        if (!StringUtils.hasText(registerDto.getPhone())) {
            throw new ServiceException("手机号不能为空");
        }

        try {
            log.info("开始注册，手机号：{}", registerDto.getPhone());

            // 1. 在讯飞账号注册（使用空密码）
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildRegisterRequest(registerDto, traceId);
            byte[] responseBytes = executePost(client, REGISTER_SUBMIT_PATH, requestBody, "提交注册");
            IflytekAccountResponse<IflytekRegisterData> responseDto =
                    parseResponse(responseBytes, IflytekRegisterData.class);
            String respCode = responseDto.getCode();

            if ("000000".equals(respCode) || "00000".equals(respCode)) {
                if (responseDto.getData() == null
                        || !StringUtils.hasText(responseDto.getData().getUserid())) {
                    log.warn("注册成功但未返回userid");
                    throw new ServiceException("注册失败：未返回用户ID");
                }

                String iflytekUserId = responseDto.getData().getUserid();
                String phone = registerDto.getPhone();
                String tenantId;

                // 2. 检查UAP中是否已存在该用户
                String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
                if (StringUtils.hasText(loginName)) {
                    // 用户已存在，查询租户列表并选择第一个
                    log.info("用户已存在于UAP，查询租户列表，登录名：{}", loginName);
                    List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
                    if (CollectionUtils.isEmpty(tenantList)) {
                        log.warn("用户已存在但没有租户信息，登录名：{}，将执行注册逻辑", loginName);
                        // 没有租户，走注册逻辑创建新租户
                        tenantId = registerUapUser(registerDto, request);
                    } else {
                        // 选择第一个租户
                        tenantId = tenantList.get(0).getId();
                        log.info("用户已存在，选择第一个租户，登录名：{}，租户ID：{}", loginName, tenantId);
                    }
                } else {
                    // 用户不存在，执行注册逻辑
                    log.info("用户不存在于UAP，开始注册，手机号：{}", phone);
                    tenantId = registerUapUser(registerDto, request);
                }

                // 2.1 将讯飞账号的 userId 存储到 UAP 用户的 third_ext_info 字段
                String finalLoginName = StringUtils.hasText(loginName) ? loginName : phone;
                try {
                    userDao.updateThirdExtInfo(finalLoginName, iflytekUserId, databaseName);
                    log.info("已保存讯飞账号 userId 到 UAP 用户扩展字段，登录名：{}，userId：{}", finalLoginName, iflytekUserId);
                } catch (Exception e) {
                    log.error("保存讯飞账号 userId 到 UAP 用户扩展字段失败，登录名：{}，userId：{}", finalLoginName, iflytekUserId, e);
                    // 不抛出异常，因为注册已经成功，只是扩展信息保存失败
                }

                // 3. 生成临时凭证并缓存注册信息
                String tempToken = UUID.randomUUID().toString().replace("-", "");
                String cacheKey = TEMP_TOKEN_PREFIX + tempToken;

                // 将注册信息和租户ID缓存（用于后续设置密码）
                registerDto.setPassword(null); // 清空密码字段，只缓存必要信息

                // 缓存租户ID和注册信息
                String cacheData = objectMapper.writeValueAsString(new HashMap<String, Object>() {
                    {
                        put("registerDto", registerDto);
                        put("tenantId", tenantId);
                    }
                });

                RedisUtils.set(cacheKey, cacheData, TEMP_TOKEN_EXPIRE_SECONDS);

                log.info("注册成功，手机号：{}，临时凭证已生成，租户ID：{}", registerDto.getPhone(), tenantId);
                return tempToken;

            } else if ("710201".equals(respCode)) {
                log.warn("提交注册失败：手机号格式不正确，手机号 {}", registerDto.getPhone());
                throw new ServiceException("手机号格式不正确");
            } else if ("710203".equals(respCode)) {
                log.warn("提交注册失败：账号已注册，手机号 {}", registerDto.getPhone());
                throw new ServiceException("账号已注册");
            }

            log.error("提交注册失败，错误码：{}，错误信息：{}", respCode, responseDto.getDesc());
            throw new ServiceException("提交注册失败：" + responseDto.getDesc());

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("提交注册异常，注册参数：{}", registerDto, e);
            throw new ServiceException("提交注册异常：" + e.getMessage());
        }
    }

    /**
     * 在UAP注册用户（使用默认密码）
     *
     * @param registerDto 注册信息
     * @param request     HTTP请求
     * @return 租户ID
     */
    private String registerUapUser(RegisterDto registerDto, HttpServletRequest request) {
        AppResponse<String> register = userService.register(registerDto, request);
        if (!register.ok()) {
            throw new ServiceException(register.getMessage());
        }
        return register.getData();
    }

    @Override
    public User setPasswordAndLogin(String tempToken, String password, String tenantId, HttpServletRequest request) {
        if (!StringUtils.hasText(tempToken)) {
            throw new ServiceException("临时凭证不能为空");
        }
        if (!StringUtils.hasText(password)) {
            throw new ServiceException("密码不能为空");
        }

        try {
            log.info("开始设置密码并登录，临时凭证：{}", tempToken);

            // 1. 从缓存中获取注册信息
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedData = RedisUtils.get(cacheKey);

            if (cachedData == null) {
                throw new ServiceException("临时凭证已过期或无效，请重新注册");
            }

            // 2. 解析缓存的数据
            Map<String, Object> dataMap = objectMapper.readValue(
                    cachedData.toString(),
                    objectMapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class));

            RegisterDto registerDto = objectMapper.convertValue(dataMap.get("registerDto"), RegisterDto.class);
            String cachedTenantId = (String) dataMap.get("tenantId");

            String phone = registerDto.getPhone();
            String loginName = phone;

            log.info("设置密码，手机号：{}，登录名：{}", phone, loginName);

            // 3. 更新讯飞账号密码
            updateIflytekPassword(loginName, password);

            // 4. 更新UAP密码
            updateUapPassword(loginName, password);

            // 5. 确定租户ID
            if (!StringUtils.hasText(tenantId)) {
                tenantId = cachedTenantId;
            }

            if (!StringUtils.hasText(tenantId)) {
                throw new ServiceException("未找到用户租户，请联系管理员");
            }

            // 6. 自动登录（使用新密码）
            LoginDto loginDto = new LoginDto();
            loginDto.setPhone(phone);
            loginDto.setLoginName(loginName);
            loginDto.setPassword(password);
            loginDto.setTenantId(tenantId);
            loginDto.setLoginType(LoginTypeEnum.PASSWORD);

            UapUser uapUser = syncAndLoginUap(loginDto, request);

            // 7. 删除临时凭证
            RedisUtils.del(cacheKey);

            log.info("设置密码并登录成功，用户ID：{}，租户ID：{}", uapUser.getId(), tenantId);
            return userMapper.fromUapUser(uapUser);

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("设置密码并登录异常，临时凭证：{}", tempToken, e);
            throw new ServiceException("设置密码并登录异常：" + e.getMessage());
        }
    }

    @Override
    public boolean setPassword(String tempToken, String password, String tenantId, HttpServletRequest request) {
        if (!StringUtils.hasText(tempToken)) {
            throw new ServiceException("临时凭证不能为空");
        }
        if (!StringUtils.hasText(password)) {
            throw new ServiceException("密码不能为空");
        }

        try {
            log.info("开始设置密码，临时凭证：{}", tempToken);

            // 1. 从缓存中获取注册信息
            String cacheKey = TEMP_TOKEN_PREFIX + tempToken;
            Object cachedData = RedisUtils.get(cacheKey);

            if (cachedData == null) {
                throw new ServiceException("临时凭证已过期或无效，请重新注册");
            }

            // 2. 解析缓存的数据
            Map<String, Object> dataMap = objectMapper.readValue(
                    cachedData.toString(),
                    objectMapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class));

            RegisterDto registerDto = objectMapper.convertValue(dataMap.get("registerDto"), RegisterDto.class);
            String phone;
            if (registerDto == null) {
                phone = (String) dataMap.get("phone");
            } else {
                phone = registerDto.getPhone();
            }
            String loginName = phone;

            log.info("设置密码，手机号：{}，登录名：{}", phone, loginName);

            // 3. 更新讯飞账号密码
            updateIflytekPassword(loginName, password);

            // 4. 更新UAP密码，login接口中使用的UAP免密登录，所以这一步去掉
            // 该方法内部需要使用旧密码修改，会因为旧密码不正确而更新失败
            //            updateUapPassword(loginName, password);

            // 如果 ext_info 为 1（历史用户），更新为 0
            String extInfo = userDao.queryExtInfoByPhone(phone, databaseName);
            if ("1".equals(extInfo)) {
                userDao.updateExtInfo(loginName, "0", databaseName);
            }

            log.info("设置密码成功");
            return true;

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("设置密码，临时凭证：{}", tempToken, e);
            throw new ServiceException("设置密码异常：" + e.getMessage());
        }
    }

    /**
     * 更新讯飞账号密码（注册后首次设置密码）
     * 注册时使用的是空密码，所以旧密码使用空字符串
     */
    private void updateIflytekPassword(String loginName, String newPassword) {
        try {
            log.info("更新讯飞账号密码，登录名：{}", loginName);

            // 注册时如果没有提供密码，使用的是空字符串
            // 所以旧密码使用空字符串
            String oldPassword = "";
            String oldPwdMd5 = oldPassword;
            String newPwdMd5 = toMd5Hex(newPassword);

            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildUpdatePasswordRequest(loginName, traceId, oldPwdMd5, newPwdMd5);
            byte[] responseBytes = executePost(client, UPDATE_PASSWORD_PATH, requestBody, "更新讯飞账号密码");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);
            String code = responseDto.getCode();

            if (isSuccessCode(code)) {
                log.info("更新讯飞账号密码成功，登录名：{}", loginName);
                return;
            }

            if ("0100100".equals(code)) {
                throw new ServiceException("更新密码失败：参数错误");
            }
            if ("0402200".equals(code)) {
                throw new ServiceException("账号不存在");
            }

            throw new ServiceException("更新密码失败：" + responseDto.getDesc());

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("更新讯飞账号密码失败，登录名：{}", loginName, e);
            throw new ServiceException("更新讯飞账号密码失败：" + e.getMessage());
        }
    }

    /**
     * 更新UAP密码
     */
    private void updateUapPassword(String loginName, String newPassword) {
        try {
            log.info("更新UAP密码，登录名：{}", loginName);

            // 调用UserService的密码更新逻辑
            // 使用默认初始密码作为旧密码
            userService.updatePasswordAfterRegister(loginName, newPassword);

        } catch (Exception e) {
            log.error("更新UAP密码失败", e);
            throw new ServiceException("更新UAP密码失败：" + e.getMessage());
        }
    }

    /**
     * 获取验证码
     *
     * @param phone 登录名
     * @return 验证码
     */
    @Override
    public String getVerificationCode(String phone, String scene) {
        try {
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildSendMsgCodeRequest(phone, traceId, DEFAULT_SMS_EXPIRE_SECONDS);
            byte[] responseBytes = executePost(client, SEND_MSG_CODE_PATH, requestBody, "获取验证码");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);
            if ("000000".equals(responseDto.getCode())) {
                // 将验证码key存储到Redis，确保只能使用一次（不存储具体验证码值，因为无法获取）
                String cacheKey = buildVerifyCodeKey(phone, scene);
                RedisUtils.set(cacheKey, "1", DEFAULT_SMS_EXPIRE_SECONDS);
                log.info("验证码已发送，key已存储到Redis，手机号：{}，场景：{}", phone, cacheKey);
                return responseDto.getDesc();
            }
            log.error("获取验证码失败，错误码：{}，错误信息：{}", responseDto.getCode(), responseDto.getDesc());
            throw new ServiceException("获取验证码失败：" + responseDto.getDesc());
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取验证码异常，登录名：{}", phone, e);
            throw new ServiceException("获取验证码异常：" + e.getMessage());
        }
    }

    @Override
    public String getVerificationCode(String phone) {
        return getVerificationCode(phone, AuthenticationService.SCENE_LOGIN);
    }

    /**
     * 验证验证码
     *
     * @param phone 登录手机号
     * @param code  验证码
     * @return 校验是否成功
     */
    public boolean verifyCode(String phone, String code, String scene) {
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("手机号不能为空");
        }
        if (!StringUtils.hasText(code)) {
            throw new ServiceException("验证码不能为空");
        }
        try {
            // 先从Redis中检查验证码key是否存在（确保只能使用一次）
            String cacheKey = buildVerifyCodeKey(phone, scene);
            if (!RedisUtils.hasKey(cacheKey)) {
                log.warn("验证码不存在或已使用，手机号：{}，场景：{}", phone, scene);
                throw new ServiceException("验证码不存在或已使用");
            }

            // 验证码key存在，调用下游服务验证
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildVerifyCodeRequest(phone, code, traceId);
            byte[] responseBytes = executePost(client, VERIFY_CODE_PATH, requestBody, "验证验证码");
            IflytekAccountResponse<Void> responseDto = parseResponse(responseBytes, Void.class);

            if ("000000".equals(responseDto.getCode())) {
                // 验证成功，删除Redis中的验证码key（确保只能使用一次）
                RedisUtils.del(cacheKey);
                log.info("验证码验证成功并已删除，手机号：{}，场景：{}", phone, scene);
                return true;
            }

            log.warn("验证验证码失败，错误码：{}，错误信息：{}", responseDto.getCode(), responseDto.getDesc());
            return false;
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("验证验证码异常，手机号：{}", phone, e);
            throw new ServiceException("验证验证码异常：" + e.getMessage());
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

    private void ensurePhoneRegistered(String phone, HttpServletRequest request) {
        if (!StringUtils.hasText(phone)) {
            throw new ServiceException("手机号不能为空");
        }
        if (queryUserExist(phone)) {
            return;
        }
        RegisterDto autoRegisterDto = RegisterDto.builder().phone(phone).build();
        String userId = register(autoRegisterDto, request);
        if (!StringUtils.hasText(userId)) {
            throw new ServiceException("自动注册失败");
        }
        log.info("手机号 {} 未注册，已自动注册，用户ID {}", phone, userId);
    }

    /**
     * 查询用户信息
     *
     * @param loginName 登录名
     * @return 用户信息
     */
    @Override
    public boolean queryUserExist(String loginName) {
        try {
            CAccountClient client = getAccountClient();
            String traceId = generateTraceId();
            byte[] requestBody = buildCheckLoginIdRequest(loginName, traceId);
            byte[] responseBytes = executePost(client, CHECK_LOGIN_ID_PATH, requestBody, "查询用户信息");
            IflytekAccountResponse<IflytekCheckLoginIdData> responseDto =
                    parseResponse(responseBytes, IflytekCheckLoginIdData.class);
            if ("000000".equals(responseDto.getCode())) {
                return responseDto.getData() != null && responseDto.getData().isExist();
            }
            log.error("查询用户信息失败，错误码：{}，错误信息：{}", responseDto.getCode(), responseDto.getDesc());
            return false;
        } catch (Exception e) {
            log.error("查询用户信息异常，登录名：{}", loginName, e);
            throw new ServiceException("查询用户信息异常：" + e.getMessage());
        }
    }

    /**
     * 构建checkLoginID请求体
     *
     * @param loginName 登录名（手机号）
     * @param traceId   追踪ID
     * @return 请求JSON字符串
     */
    private byte[] buildCheckLoginIdRequest(String loginName, String traceId) {
        try {
            IflytekAccountRequest<IflytekCheckLoginIdParam> request = new IflytekAccountRequest<>(
                    new IflytekAccountBase(appid, traceId),
                    new IflytekCheckLoginIdParam(loginName, DEFAULT_COUNTRY_CODE, DEFAULT_LOGIN_TYPE));
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建请求体失败", e);
            throw new ServiceException("构建请求体失败：" + e.getMessage());
        }
    }

    private byte[] buildSendMsgCodeRequest(String phone, String traceId, int expireSeconds) {
        try {
            IflytekAccountRequest<IflytekSendMsgCodeParam> request = new IflytekAccountRequest<>(
                    new IflytekAccountBase(appid, traceId),
                    new IflytekSendMsgCodeParam(DEFAULT_COUNTRY_CODE, phone, expireSeconds));
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建验证码请求体失败", e);
            throw new ServiceException("构建验证码请求体失败：" + e.getMessage());
        }
    }

    private byte[] buildVerifyCodeRequest(String phone, String code, String traceId) {
        try {
            IflytekAccountRequest<IflytekVerifyCodeParam> request = new IflytekAccountRequest<>(
                    new IflytekAccountBase(appid, traceId), new IflytekVerifyCodeParam(phone, code));
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建验证码校验请求体失败", e);
            throw new ServiceException("构建验证码校验请求体失败：" + e.getMessage());
        }
    }

    private <T> IflytekAccountResponse<T> parseResponse(byte[] responseBytes, Class<T> dataClass) {
        try {
            return objectMapper.readValue(
                    responseBytes,
                    objectMapper.getTypeFactory().constructParametricType(IflytekAccountResponse.class, dataClass));
        } catch (Exception e) {
            log.error("解析响应失败", e);
            throw new ServiceException("解析响应失败：" + e.getMessage());
        }
    }

    private byte[] buildRegisterRequest(RegisterDto registerDto, String traceId) {
        try {
            String loginId = registerDto.getPhone();
            if (!StringUtils.hasText(loginId)) {
                throw new ServiceException("注册账号不能为空");
            }
            String password = StringUtils.isEmpty(registerDto.getPassword()) ? "" : toMd5Hex(registerDto.getPassword());
            IflytekRegisterParam param = new IflytekRegisterParam(
                    loginId, DEFAULT_LOGIN_TYPE, DEFAULT_COUNTRY_CODE, password, DEFAULT_PASSWORD_TYPE);
            IflytekAccountRequest<IflytekRegisterParam> request =
                    new IflytekAccountRequest<>(new IflytekAccountBase(appid, traceId), param);
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建注册请求体失败", e);
            throw new ServiceException("构建注册请求体失败：" + e.getMessage());
        }
    }

    private byte[] buildLoginRequest(LoginDto loginDto, String traceId, IflytekLoginModeEnum loginMode) {
        try {
            String loginId = resolveLoginId(loginDto.getLoginName(), loginDto.getPhone());
            boolean usePassword = loginMode == IflytekLoginModeEnum.PASSWORD;
            if (usePassword && !StringUtils.hasText(loginDto.getPassword())) {
                throw new ServiceException("登录密码不能为空");
            }
            String lgType = loginMode.getValue();
            String password = usePassword ? toMd5Hex(loginDto.getPassword()) : "";
            IflytekLoginParam param =
                    new IflytekLoginParam(loginId, DEFAULT_COUNTRY_CODE, lgType, password, DEFAULT_PASSWORD_TYPE);
            IflytekAccountRequest<IflytekLoginParam> request =
                    new IflytekAccountRequest<>(new IflytekAccountBase(appid, traceId), param);
            return objectMapper.writeValueAsBytes(request);
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("构建登录请求体失败", e);
            throw new ServiceException("构建登录请求体失败：" + e.getMessage());
        }
    }

    private String resolveLoginId(String loginName, String phone) {
        //        if (StringUtils.hasText(loginName)) {
        //            return loginName;
        //        }
        if (StringUtils.hasText(phone)) {
            return phone;
        }
        throw new ServiceException("手机号不能为空");
    }

    private IflytekLoginModeEnum resolveLoginMode(LoginDto loginDto) {
        if (loginDto.getLoginType() == LoginTypeEnum.PASSWORD) {
            return IflytekLoginModeEnum.PASSWORD;
        } else {
            return IflytekLoginModeEnum.FREE;
        }
    }

    private String toMd5Hex(String raw) {
        return DigestUtils.md5DigestAsHex(raw.getBytes(StandardCharsets.UTF_8));
    }

    private byte[] buildUpdatePasswordRequest(String loginId, String traceId, String oldPwdMd5, String newPwdMd5) {
        try {
            IflytekAccountRequest<IflytekUpdatePasswordParam> request = new IflytekAccountRequest<>(
                    new IflytekAccountBase(appid, traceId),
                    new IflytekUpdatePasswordParam(
                            loginId, DEFAULT_COUNTRY_CODE, "phone", oldPwdMd5, newPwdMd5, DEFAULT_PASSWORD_TYPE));
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建修改密码请求体失败", e);
            throw new ServiceException("构建修改密码请求体失败：" + e.getMessage());
        }
    }

    private boolean isSuccessCode(String code) {
        return "000000".equals(code) || "00000".equals(code);
    }

    /**
     * 构建删除用户请求体
     *
     * @param userid  讯飞账号的 userid
     * @param traceId 追踪ID
     * @return 请求体字节数组
     */
    private byte[] buildDeleteUserRequest(String userid, String traceId) {
        try {
            IflytekAccountRequest<IflytekDeleteUserParam> request = new IflytekAccountRequest<>(
                    new IflytekAccountBase(appid, traceId), new IflytekDeleteUserParam(userid));
            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建删除用户请求体失败", e);
            throw new ServiceException("构建删除用户请求体失败：" + e.getMessage());
        }
    }

    /**
     * 构建同步用户信息请求体
     *
     * @param userid        用户ID
     * @param password      密码（可为空）
     * @param loginAccounts 登录账号列表
     * @param userInfo      用户详细信息
     * @param traceId       追踪ID
     * @return 请求体字节数组
     */
    private byte[] buildSyncUserInfoRequest(
            String userid,
            String password,
            List<IflytekSyncUserInfoAccount> loginAccounts,
            IflytekSyncUserInfoUserInfo userInfo,
            String traceId) {
        try {
            // 如果密码不为空，转换为MD5
            String passwordMd5 = StringUtils.hasText(password) ? toMd5Hex(password) : "";

            // 构建登录信息
            IflytekSyncUserInfoLogin login = new IflytekSyncUserInfoLogin(loginAccounts);

            // 构建请求参数
            IflytekSyncUserInfoParam param = new IflytekSyncUserInfoParam(userid, passwordMd5, login, userInfo);

            // 构建完整请求
            IflytekAccountRequest<IflytekSyncUserInfoParam> request =
                    new IflytekAccountRequest<>(new IflytekAccountBase(appid, traceId), param);

            return objectMapper.writeValueAsBytes(request);
        } catch (Exception e) {
            log.error("构建同步用户信息请求体失败", e);
            throw new ServiceException("构建同步用户信息请求体失败：" + e.getMessage());
        }
    }

    /**
     * 初始化讯飞账号客户端
     * 使用 @PostConstruct 注解在 Bean 初始化后自动执行
     * 避免在每次请求时重复创建 client 实例
     */
    @javax.annotation.PostConstruct
    private void initAccountClient() {
        log.info("初始化讯飞账号客户端，accountHost: {}", accountHost);
        this.accountClient =
                accountClientFactory.create(accountHost, TIME_OUT, accessKey, accessSecret, USE_AES_ENCRYPT);
    }

    /**
     * 获取讯飞账号客户端实例（单例复用）
     */
    private CAccountClient getAccountClient() {
        return accountClient;
    }

    private String generateTraceId() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    /**
     * 获取当前服务器IP地址
     * 优先级：
     * 1. 本地调试模式 -> 使用配置的本地IP
     * 2. 配置的服务器IP（rpa.auth.server-ip）-> 适用于K8s等容器环境
     * 3. 自动获取本机IP -> 适用于物理机/虚拟机部署
     * 4. 默认IP -> 兜底方案
     */
    private String getServerIp() {
        // 1. 本地调试模式，使用配置的本地IP
        if (localDebug) {
            log.debug("本地调试模式，使用配置的IP：{}", localDebugIp);
            return localDebugIp;
        }

        // 2. 如果配置了服务器IP，直接使用（适用于K8s环境）
        if (serverIp != null && !serverIp.trim().isEmpty()) {
            log.debug("使用配置的服务器IP：{}", serverIp);
            return serverIp;
        }

        // 3. 尝试自动获取本机IP（适用于物理机/虚拟机部署）
        try {
            Enumeration<NetworkInterface> networkInterfaces = NetworkInterface.getNetworkInterfaces();
            while (networkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = networkInterfaces.nextElement();
                // 跳过回环接口和未启用的接口
                if (networkInterface.isLoopback() || !networkInterface.isUp()) {
                    continue;
                }

                Enumeration<InetAddress> inetAddresses = networkInterface.getInetAddresses();
                while (inetAddresses.hasMoreElements()) {
                    InetAddress inetAddress = inetAddresses.nextElement();
                    // 只获取IPv4地址，且不是回环地址
                    if (!inetAddress.isLoopbackAddress()
                            && inetAddress.getHostAddress().indexOf(':') == -1) {
                        String ip = inetAddress.getHostAddress();
                        log.debug("自动获取到IP：{}", ip);
                        return ip;
                    }
                }
            }
        } catch (SocketException e) {
            log.error("自动获取IP失败", e);
        }

        // 4. 如果获取失败，返回默认值
        log.warn("无法获取服务器IP，使用默认值：{}", localDebugIp);
        return localDebugIp;
    }

    private byte[] executePost(CAccountClient client, String path, byte[] requestBody, String actionDesc) {
        try {
            String requestString = new String(requestBody, StandardCharsets.UTF_8);
            log.info("{}，请求路径：{}，请求体：{}", actionDesc, path, requestString);
            Map<String, String> headers = new HashMap<>();
            // 根据环境自动获取IP地址：本地调试使用配置的IP，服务器部署使用真实IP
            String serverIp = getServerIp();
            headers.put("X-Forwarded-For", serverIp);
            log.debug("使用IP地址：{}", serverIp);
            CAccountResponse response = client.post(path, headers, requestBody);
            if (response.getHttpStatus() != 200) {
                log.error("{}失败，HTTP状态码：{}，错误信息：{}", actionDesc, response.getHttpStatus(), response.getErrorMessage());
                throw new ServiceException(actionDesc + "失败：" + response.getErrorMessage());
            }
            String responseData = new String(response.getData(), StandardCharsets.UTF_8);
            log.info("{}成功，响应数据：{}", actionDesc, responseData);
            return response.getData();
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("{}异常", actionDesc, e);
            throw new ServiceException(actionDesc + "异常：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) {
        return userService.logout(request, response);
    }

    /**
     * 刷新token
     *
     * @param request     HTTP请求
     * @param accessToken
     * @return
     */
    @Override
    public AppResponse<Boolean> refreshToken(HttpServletRequest request, String accessToken) {
        try {
            String refreshToken = Oauth2Util.getRefreshTokenFromRequest(request);
            if (org.apache.commons.lang3.StringUtils.isBlank(refreshToken)) {
                return AppResponse.success(false);
            }
            boolean flag = true;
            ResponseDto<LoginTokenResponseDto> responseDto =
                    ClientAuthenticationAPI.refreshToken(accessToken, refreshToken, null);
            if (responseDto.isFlag()) {
                String userFlag = null;
                if (ClientConfigUtil.instance().isUseSession()) {
                    userFlag = request.getSession().getId();
                } else {
                    userFlag = com.iflytek.sec.uap.client.util.ClientRequestUtil.getFlagFromRequest(request);
                }
                com.iflytek.sec.uap.client.util.CacheUtil.refreshAuthenticationToken(userFlag, responseDto.getData());
            } else {
                flag = false;
            }
            return AppResponse.success((flag));
        } catch (Exception e) {
            log.error("刷新access token失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "刷新access token失败：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<Boolean> checkSession(HttpServletRequest request, HttpServletResponse response) {
        try {
            // 1. 先校验session是否有效（UAP的AuthenticationFilter已经校验了）

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
        // SaaS模式暂时不支持修改密码
        throw new UnsupportedOperationException("SaaS模式暂时不支持修改密码");
    }

    /**
     * 处理单点登录：清除旧session，存储新sessionId
     *
     * @param userId  用户ID
     * @param request HTTP请求
     */
    private void handleSingleSignOn(String userId, HttpServletRequest request) {
        try {
            if (StringUtils.isEmpty(userId)) {
                return;
            }

            // 获取当前sessionId
            String currentSessionId = request.getSession().getId();
            if (StringUtils.isEmpty(currentSessionId)) {
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
            // 注意：这里不设置TTL，让它在session过期时自然失效，或者设置一个较长的TTL
            RedisUtils.set(redisKey, currentSessionId, 2592000); // 30天

            log.debug("单点登录session映射已更新，用户ID：{}，sessionId：{}", userId, currentSessionId);

        } catch (Exception e) {
            log.error("处理单点登录失败，用户ID：{}", userId, e);
            // 不抛出异常，避免影响登录流程
        }
    }

    /**
     * 控制台-直接添加用户
     */
    @Override
    public AppResponse<String> addUser(AddUserDto userDto, HttpServletRequest request) {
        String phone = userDto.getPhone();
        userDto.setPassword(DEFAULT_INITIAL_PASSWORD);
        userDto.setConfirmPassword(DEFAULT_INITIAL_PASSWORD);
        if (queryUserExist(phone)) {
            String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
            if (StringUtils.hasText(loginName)) {
                userService.addUser(userDto, request);
            } else {
                userService.doBindTenantRoleDept(userDto, request);
            }
        } else {
            String name = userDto.getName();
            RegisterDto registerDto = RegisterDto.builder().build();
            BeanUtils.copyProperties(userDto, registerDto);
            registerDto.setLoginName(name);
            registerWithoutCaptcha(registerDto, request);
            userService.doBindTenantRoleDept(userDto, request);
        }
        return AppResponse.success("添加成功");
    }
}
