package com.iflytek.rpa.auth.sp.uap.utils;

import com.fasterxml.jackson.core.type.TypeReference;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.BindResourceDto;
import com.iflytek.rpa.auth.core.entity.OrgListDto;
import com.iflytek.sec.uap.client.core.client.BaseClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.enums.MethodEnum;
import com.iflytek.sec.uap.client.core.model.ManagementClientOptions;
import com.iflytek.sec.uap.client.core.model.UapRequestConfig;
import com.iflytek.sec.uap.client.core.util.JsonUtils;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

/**
 * @author mjren
 * @date 2025-03-05 16:24
 * @copyright Copyright (c) 2025 mjren
 */
@Slf4j
@ConditionalOnSaaSOrUAP
public class UapManagementClient extends BaseClient {
    private final ManagementClientOptions options;

    public UapManagementClient(ManagementClientOptions options) {
        super(options);
        if (null == options) {
            throw new IllegalArgumentException("options is required");
        } else {
            this.options = options;
            if (StringUtils.isBlank(options.getUapHost())) {
                throw new IllegalArgumentException("uapHost is required");
            } else if (StringUtils.isBlank(options.getAppCode())) {
                throw new IllegalArgumentException("appCode is required");
            } else if (StringUtils.isBlank(options.getAppAuthCode())) {
                throw new IllegalArgumentException("appAuthCode is required");
            }
        }
    }

    public ResponseDto<Object> unbindRoleSource(BindResourceDto dto) {
        UapRequestConfig config = new UapRequestConfig("/rest/v2/role/unBindResource", MethodEnum.JSON_POST, dto);
        String response = this.request(config);
        return (ResponseDto) JsonUtils.parseObject(response, new TypeReference<ResponseDto<Object>>() {});
    }

    public ResponseDto<Object> dataAuthSearchPage(Map<String, Object> searchDto) {

        UapRequestConfig config = new UapRequestConfig("/rest/v3/dataAuth/search", MethodEnum.JSON_POST, searchDto);
        String response = this.request(config);
        return (ResponseDto) JsonUtils.parseObject(response, new TypeReference<ResponseDto<Object>>() {});
    }

    public ResponseDto<PageDto<UapOrg>> queryOrgPageList(OrgListDto dto) {
        UapRequestConfig config = new UapRequestConfig("/rest/v4/org/queryList", MethodEnum.JSON_POST, dto);
        String response = this.request(config);
        return (ResponseDto) JsonUtils.parseObject(response, new TypeReference<ResponseDto<PageDto<UapOrg>>>() {});
    }

    /**
     * 根据角色id获取数据权限
     * @param roleId
     * @return
     */
    public List<DataAuthorityWithDimDictDto> queryDataAuthByRoleId(String tenantId, String roleId) {
        Map<String, String> param = new HashMap();
        param.put("tenantId", tenantId);
        param.put("roleId", roleId);
        UapRequestConfig config = new UapRequestConfig("/rest/dataAuth/get/byRoleId/", MethodEnum.GET, param);
        String response = this.request(config);
        ResponseDto<List<DataAuthorityWithDimDictDto>> responseDto = (ResponseDto)
                JsonUtils.parseObject(response, new TypeReference<ResponseDto<List<DataAuthorityWithDimDictDto>>>() {});
        if (responseDto.isFlag()) {
            return responseDto.getData();
        } else {
            log.error("接口调用异常 {}", responseDto.getMessage());
            return null;
        }
    }
}
