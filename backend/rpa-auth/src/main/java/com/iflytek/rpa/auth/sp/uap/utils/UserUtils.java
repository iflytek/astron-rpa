package com.iflytek.rpa.auth.sp.uap.utils;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.exception.NoLoginException;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.HttpUtils;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.user.ListUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.*;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.CollectionUtils;

/**
 * 用户工具类
 */
@ConditionalOnSaaSOrUAP
public class UserUtils {
    private static final Logger LOGGER = LoggerFactory.getLogger(UserUtils.class);
    public static final String USER_SESSION_KEY = "nowLoginUser";

    public UserUtils() {}

    public static UapUser nowLoginUser() throws NoLoginException {
        UapUser uapUser = UapUserInfoAPI.getLoginUser(HttpUtils.getRequest());
        if (null == uapUser) {
            throw new NoLoginException();
        } else {
            return uapUser;
        }
    }

    public static AppResponse<?> nowLoginUserResponse() {
        try {
            return AppResponse.success(nowLoginUser());
        } catch (Exception var1) {
            return AppResponse.error("900001", "用户未登录");
        }
    }

    /**
     * 获取当前登录用户的id
     * @return
     * @throws NoLoginException
     */
    public static String nowUserId() throws NoLoginException {
        return nowLoginUser().getId();
    }

    /**
     * 获取当前登录用户的用户名
     * @return
     * @throws NoLoginException
     */
    public static String nowLoginUsername() throws NoLoginException {
        return nowLoginUser().getLoginName();
    }

    /**
     * 根据用户id查询用户名
     * @param id
     * @return
     */
    public static String getLoginNameById(String id) {
        UapUser user = getUserInfoById(id);
        if (null == user) {
            return null;
        }
        return user.getLoginName();
    }

    /**
     * 根据用户id查询姓名
     * @param id
     * @return
     */
    public static String getRealNameById(String id) {
        UapUser user = getUserInfoById(id);
        if (null == user) {
            return null;
        }
        return user.getName();
    }

    /**
     * 根据用户id查询用户信息
     * @param id
     * @return
     */
    public static UapUser getUserInfoById(String id) {
        List<UapUser> userList = queryUserPageList(Collections.singletonList(id));
        userList.removeIf(Objects::isNull);
        if (CollectionUtils.isEmpty(userList)) {
            LOGGER.error("根据userId查询用户信息失败, userId: {}", id);
            return null;
        }
        return userList.get(0);
    }

    /**
     * 根据手机号查询用户姓名
     */
    public static String getRealNameByPhone(String phone) {
        UapUser user = getUserInfoByPhone(phone);
        if (null == user) {
            return null;
        }
        return user.getName();
    }

    public static String getLoginNameByPhone(String phone) {
        UapUser user = getUserInfoByPhone(phone);
        if (null == user) {
            return null;
        }
        return user.getLoginName();
    }

    public static UapUser getUserInfoByPhone(String phone) {
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setStatus(null);
        listUserDto.setPhone(phone);
        PageDto<UapUser> userList =
                ClientManagementAPI.queryUserPageList(UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), listUserDto);
        if (CollectionUtils.isEmpty(userList.getResult())) {
            LOGGER.error("根据手机号查询用户信息失败, phone: {}", phone);
            return null;
        }
        return userList.getResult().get(0);
    }

    /**
     * 根据userIdList查用户基本信息列表,最多支持100个id
     * @return
     */
    public static List<UapUser> queryUserPageList(List<String> userIdList) {
        //        分页查用户基本信息列表
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setStatus(null);
        listUserDto.setUserIds(userIdList);
        listUserDto.setPageSize(100);
        String tenantId = UapUserInfoAPI.getTenantId(HttpUtils.getRequest());
        PageDto<UapUser> userList = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);
        if (CollectionUtils.isEmpty(userList.getResult())) {
            LOGGER.error("根据userId查询用户信息失败, userId: {}", Arrays.toString(userIdList.toArray()));
            return Collections.emptyList();
        }
        return userList.getResult();
    }

    /**
     * 根据姓名模糊查询人员
     * @param keyword
     * @param deptId
     * @return
     */
    public static List<UapUser> searchUserByName(String keyword, String deptId) {
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setStatus(null);
        if (StringUtils.isNotBlank(deptId)) {
            listUserDto.setOrgId(deptId);
        }
        listUserDto.setName(keyword);
        PageDto<UapUser> userListByName =
                ClientManagementAPI.queryUserPageList(UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), listUserDto);
        if (null != userListByName) {
            return userListByName.getResult();
        }
        return null;
    }

    /**
     * 根据手机号模糊查询人员
     * @param keyword
     * @param deptId
     * @return
     */
    public static List<UapUser> searchUserByPhone(String keyword, String deptId) {
        ListUserDto listUserDtoByPhone = new ListUserDto();
        listUserDtoByPhone.setStatus(null);
        if (StringUtils.isNotBlank(deptId)) {
            listUserDtoByPhone.setOrgId(deptId);
        }
        listUserDtoByPhone.setPhone(keyword);
        PageDto<UapUser> userListByPhone = ClientManagementAPI.queryUserPageList(
                UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), listUserDtoByPhone);
        if (null != userListByPhone) {
            return userListByPhone.getResult();
        }
        return null;
    }

    /**
     * 根据姓名或手机号模糊查询人员
     * @param keyword
     * @param deptId
     * @return
     */
    public static List<UapUser> searchUserByNameOrPhone(String keyword, String deptId) {
        List<UapUser> result = new ArrayList<>();
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setStatus(null);
        listUserDto.setOrgId(deptId);
        listUserDto.setName(keyword);
        PageDto<UapUser> userListByName =
                ClientManagementAPI.queryUserPageList(UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), listUserDto);
        if (null != userListByName && !CollectionUtils.isEmpty(userListByName.getResult())) {
            result.addAll(userListByName.getResult());
        }
        ListUserDto listUserDtoByPhone = new ListUserDto();
        listUserDtoByPhone.setStatus(null);
        listUserDtoByPhone.setOrgId(deptId);
        listUserDtoByPhone.setPhone(keyword);
        PageDto<UapUser> userListByPhone = ClientManagementAPI.queryUserPageList(
                UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), listUserDtoByPhone);
        if (null != userListByPhone && !CollectionUtils.isEmpty(userListByPhone.getResult())) {
            result.addAll(userListByPhone.getResult());
        }
        return result;
    }
}
