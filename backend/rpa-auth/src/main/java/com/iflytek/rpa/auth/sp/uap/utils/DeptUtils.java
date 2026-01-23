package com.iflytek.rpa.auth.sp.uap.utils;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.DataAuthDetailDo;
import com.iflytek.rpa.auth.core.entity.OrgListDto;
import com.iflytek.rpa.auth.exception.NoLoginException;
import com.iflytek.rpa.auth.utils.HttpUtils;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto;
import com.iflytek.sec.uap.client.core.dto.org.GetOrgDto;
import com.iflytek.sec.uap.client.core.dto.org.OrgExtendDto;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.user.*;
import com.iflytek.sec.uap.client.util.Oauth2Util;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-05-08 11:22
 * @copyright Copyright (c) 2025 mjren
 */
@ConditionalOnSaaSOrUAP
public class DeptUtils {
    private static final Logger log = LoggerFactory.getLogger(DeptUtils.class);

    public DeptUtils() {}

    /*
     UAP字段和RPA字段的映射：
     levelCode = deptIdPath
     id = deptId
    */

    /**
     * 获取当前登录用户的部门levelCode，即deptIdPath
     * @return
     */
    public static String getLevelCode() {
        UapOrg deptInfo = getDeptInfo();
        if (deptInfo != null) {
            return deptInfo.getLevelCode() + "-";
        } else {
            log.error("获取部门id path失败");
            return null;
        }
    }

    /**
     * 获取当前登录用户的部门id
     * @return
     */
    public static String getDeptId() {
        UapOrg deptInfo = getDeptInfo();
        if (deptInfo != null) {
            return deptInfo.getId();
        } else {
            log.error("获取部门id失败");
            return null;
        }
    }

    /**
     * 获取当前登录用户的部门详细信息
     * @return
     */
    public static UapOrg getDeptInfo() {
        String accessToken = Oauth2Util.getAccessToken(HttpUtils.getRequest());
        return ClientAuthenticationAPI.getUserOrgInfo(null, null, accessToken);
    }

    /**
     * 根据部门id查部门详细信息
     * @param id
     * @return
     */
    public static UapOrg getDeptInfoByDeptId(String id) {
        GetOrgDto getOrgDto = new GetOrgDto();
        getOrgDto.setId(id);
        OrgExtendDto orgExtendDto =
                ClientManagementAPI.getOrgExtendInfo(UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), getOrgDto);
        if (orgExtendDto != null) {
            return orgExtendDto.getUapOrg();
        } else {
            log.error("获取部门信息失败");
            return null;
        }
    }

    /**
     * 查询部门id对应的levelCode
     * @param id
     * @return
     */
    public static String getLevelCodeByDeptId(String id) {
        GetOrgDto getOrgDto = new GetOrgDto();
        getOrgDto.setId(id);
        OrgExtendDto orgExtendDto =
                ClientManagementAPI.getOrgExtendInfo(UapUserInfoAPI.getTenantId(HttpUtils.getRequest()), getOrgDto);
        if (orgExtendDto != null) {
            return orgExtendDto.getUapOrg().getLevelCode() + "-";
        } else {
            log.error("获取部门信息失败");
            return null;
        }
    }

    /**
     * 查询指定机构及所有子机构的用户数量
     * @param id
     * @return
     */
    public static Long getUserNumByDeptId(String id) {
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(HttpUtils.getRequest());
        ListUserByOrgDto listUserByOrgDto = new ListUserByOrgDto();
        listUserByOrgDto.setOrgId(id);
        // 分页查询当前机构及所有子机构的用户
        ResponseDto<PageDto<UapUser>> userListPageResponse = managementClient.queryUserPageListByOrg(listUserByOrgDto);
        if (userListPageResponse.isFlag()) {
            return userListPageResponse.getData().getTotalCount();
        } else {
            log.error("queryUserPageListByOrg接口调用异常 {}", userListPageResponse.getMessage());
            return null;
        }
    }

    /**
     * 根据部门id列表获取部门信息列表
     * @param tenantId
     * @param orgIdList
     * @return
     */
    public static List<UapOrg> queryOrgPageList(String tenantId, List<String> orgIdList) {
        OrgListDto orgListDto = new OrgListDto();
        orgListDto.setOrgIds(orgIdList);
        ResponseDto<PageDto<UapOrg>> orgPageResponse =
                UapManagementClientUtil.queryOrgPageList(tenantId, orgListDto, HttpUtils.getRequest());
        if (!orgPageResponse.isFlag()) {
            log.error("queryOrgPageList error, msg:{}", orgPageResponse.getMessage());
            throw new RuntimeException(orgPageResponse.getMessage());
        }
        return orgPageResponse.getData().getResult();
    }

    public static String getDeptIdByUserId(String userId, String tenantId) {
        GetUserDto getUserDto = new GetUserDto();
        getUserDto.setUserId(userId);
        UserExtendDto userExtendDto = ClientManagementAPI.getUserExtendInfo(tenantId, getUserDto);
        UapUser user = userExtendDto.getUser();
        if (null == user) {
            return null;
        }
        return user.getOrgId();
    }

    /**
     * 查询数据权限，是一个部门列表
     * @return
     */
    public static DataAuthDetailDo getDataAuthWithDeptList() throws NoLoginException {
        UapUser uapUser = UserUtils.nowLoginUser();
        // admin 单独处理
        if (uapUser.getLoginName().equals("admin")) {
            DataAuthDetailDo dataAuthDetailDo = new DataAuthDetailDo();
            dataAuthDetailDo.setDataAuthType("all");
            return dataAuthDetailDo;
        }

        DataAuthDetailDo dataAuthDetailDo = new DataAuthDetailDo();
        List<DataAuthorityWithDimDictDto> dataAuthList = UapUserInfoAPI.getDataAuthList(HttpUtils.getRequest());
        if (dataAuthList == null || CollectionUtils.isEmpty(dataAuthList)) {
            dataAuthDetailDo.setDataAuthType("all");
            return dataAuthDetailDo;
        }
        DataAuthorityWithDimDictDto checkedDataAuth = null;
        for (DataAuthorityWithDimDictDto dataAuth : dataAuthList) {
            if (null != dataAuth && dataAuth.isChecked()) {
                checkedDataAuth = dataAuth;
                break;
            }
        }
        if (null == checkedDataAuth) {
            dataAuthDetailDo.setDataAuthType("all");
            return dataAuthDetailDo;
        }
        // 如果是数据权限为全部，返回null
        if ("全部".equals(checkedDataAuth.getDataAuthName())) {
            dataAuthDetailDo.setDataAuthType("all");
            return dataAuthDetailDo;
        }
        // 如果是数据权限为所在部门，则返回所在部门levelCode
        if ("所在部门".equals(checkedDataAuth.getDataAuthName())) {
            UapOrg deptInfo = getDeptInfo();
            List<String> deptIdList = Collections.singletonList(deptInfo.getId());
            List<String> deptIdPathList = Collections.singletonList(deptInfo.getLevelCode() + "-");
            dataAuthDetailDo.setDataAuthType("in_dept");
            dataAuthDetailDo.setDeptIdList(deptIdList);
            dataAuthDetailDo.setDeptIdPathList(deptIdPathList);
            return dataAuthDetailDo;
        }
        // todo 如果数据权限为指定部门，则查询部门范围，根据部门id获取levelCode
        // todo 如果数据权限为仅个人，则只返回type，暂不做
        dataAuthDetailDo.setDataAuthType("all");
        return dataAuthDetailDo;
    }
}
