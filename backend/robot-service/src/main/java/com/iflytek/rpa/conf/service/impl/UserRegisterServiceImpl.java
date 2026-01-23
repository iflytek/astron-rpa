package com.iflytek.rpa.conf.service.impl;

import com.iflytek.rpa.conf.dao.UapUserDao;
import com.iflytek.rpa.conf.entity.vo.UserRegisterVo;
import com.iflytek.rpa.conf.service.UserRegisterService;
import com.iflytek.rpa.utils.response.AppResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 用户注册服务实现类
 */
@Service
public class UserRegisterServiceImpl implements UserRegisterService {

    @Autowired
    private UapUserDao uapUserDao;

    //    @Value("${uap.database.name:uap_db}")
    //    private String uapDatabaseName;
    //
    //    @Value("${uap.default-tenant-id:}")
    //    private String defaultTenantId;
    //
    //    @Value("${uap.default-user-secret:}")
    //    private String defaultUserSecret;
    //
    //    @Value("${package.download:}")
    //    private String packageDownloadUrl;
    //
    //    @Value("${uap.default-role-id:}")
    //    private String defaultRoleId;

    /**
     * 默认密码配置字段名
     */
    private static final String DEFAULT_PASSWORD_FIELD_NAME = "user.default.pwd";

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<UserRegisterVo> register(String phone) {
        return AppResponse.success(new UserRegisterVo());
        //        try {
        //            // 检查账号是否已存在
        //            String existingUserId = uapUserDao.getUserIdByLoginNameOrPhone(uapDatabaseName, phone, phone);
        //            if (existingUserId != null) {
        //                // 如果账号已存在，返回该用户的userId
        //                UserRegisterVo registerVo = new UserRegisterVo();
        //                registerVo.setAccount(phone);
        //                registerVo.setUserId(existingUserId);
        //                AppResponse<UserRegisterVo> response = AppResponse.error(ErrorCodeEnum.E_COMMON,
        // "注册失败：账号已存在");
        //                response.setData(registerVo);
        //                return response;
        //            }
        //
        //            // 从数据库获取默认密码
        //            String defaultPassword = uapUserDao.getConfigValue(uapDatabaseName, DEFAULT_PASSWORD_FIELD_NAME);
        //            if (defaultPassword == null || defaultPassword.trim().isEmpty()) {
        //                AppResponse<UserRegisterVo> response = AppResponse.error(ErrorCodeEnum.E_COMMON,
        // "注册失败：未找到默认密码配置");
        //                return response;
        //            }
        //
        //            // 生成UUID作为用户ID和租户用户关系ID
        //            String userId = UUID.randomUUID().toString();
        //            String tenantUserId = UUID.randomUUID().toString();
        //            String roleUserId = UUID.randomUUID().toString();
        //
        //            // 插入用户表（使用加密后的密码）
        //            int userResult = uapUserDao.insertUser(uapDatabaseName, userId, phone, defaultUserSecret, phone);
        //            if (userResult <= 0) {
        //                AppResponse<UserRegisterVo> response =
        // AppResponse.error(ErrorCodeEnum.E_COMMON,"注册失败：插入用户信息失败");
        //                return response;
        //            }
        //
        //            // 插入租户用户关系表
        //            int tenantUserResult = uapUserDao.insertTenantUser(uapDatabaseName, tenantUserId, defaultTenantId,
        // userId);
        //            if (tenantUserResult <= 0) {
        //                AppResponse<UserRegisterVo> response =
        // AppResponse.error(ErrorCodeEnum.E_COMMON,"注册失败：插入租户用户关系失败");
        //                return response;
        //            }
        //
        //            int roleUserResult = uapUserDao.insertRoleUser(uapDatabaseName, roleUserId, defaultRoleId,
        // defaultTenantId, userId);
        //            if (roleUserResult <= 0) {
        //                AppResponse<UserRegisterVo> response =
        // AppResponse.error(ErrorCodeEnum.E_COMMON,"注册失败：插入角色用户关系失败");
        //                return response;
        //            }
        //
        //            // 返回账号和默认密码（明文）
        //            UserRegisterVo registerVo = new UserRegisterVo();
        //            registerVo.setAccount(phone);
        //            registerVo.setPassword(defaultPassword);
        //            registerVo.setUserId(userId);
        //            registerVo.setUrl(packageDownloadUrl);
        //
        //            return AppResponse.success(registerVo);
        //        } catch (Exception e) {
        //            AppResponse<UserRegisterVo> response = AppResponse.error(ErrorCodeEnum.E_COMMON,"注册失败：" +
        // e.getMessage());
        //            return response;
        //        }
    }
}
