package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.DeptService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 17:51
 */
@Slf4j
@Service("casdoorDeptService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorDeptServiceImpl implements DeptService {
    @Override
    public AppResponse<?> treeAndPerson(HttpServletRequest request) {
        return AppResponse.success(Collections.emptyMap());
    }

    @Override
    public AppResponse<Map<String, Object>> treeAndPersonOptimized(HttpServletRequest request) {
        return AppResponse.success(Collections.emptyMap());
    }

    @Override
    public AppResponse<String> addDept(CreateUapOrgDto createUapOrgDto, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<TreeNode> queryTreeList(HttpServletRequest request) throws Exception {
        return AppResponse.success(new TreeNode());
    }

    @Override
    public AppResponse<List<DeptTreeNodeVo>> queryDeptTreeByPid(QueryDeptNodeDto dto, HttpServletRequest request)
            throws Exception {
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<String> editDept(EditOrgDto editOrgDto, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<String> deleteDept(DeleteCommonDto deleteCommonDto, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<DeptNameVo> queryDeptNameByDeptId(QueryDeptIdDto dto, HttpServletRequest request) {
        return AppResponse.success(new DeptNameVo());
    }

    @Override
    public AppResponse<String> queryTenantName(HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<List<DeptPersonTreeNodeVo>> queryDeptPersonNodeByPid(
            QueryDeptNodeDto dto, HttpServletRequest request) throws JsonProcessingException {
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<List<UserVo>> queryAllUserByDeptId(QueryDeptIdDto dto, HttpServletRequest request)
            throws Exception {
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<String> getCurrentLevelCode(HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<String> getCurrentDeptId(HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<Org> getCurrentDeptInfo(HttpServletRequest request) {
        return AppResponse.success(new Org());
    }

    @Override
    public AppResponse<Org> getDeptInfoByDeptId(String id, HttpServletRequest request) {
        return AppResponse.success(new Org());
    }

    @Override
    public AppResponse<String> getLevelCodeByDeptId(String id, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<Long> getUserNumByDeptId(String id, HttpServletRequest request) {
        return AppResponse.success(0L);
    }

    @Override
    public AppResponse<List<Org>> queryOrgListByIds(List<String> orgIdList, HttpServletRequest request) {
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<String> getDeptIdByUserId(String userId, String tenantId, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<DataAuthDetailDo> getDataAuthWithDeptList(HttpServletRequest request) {
        DataAuthDetailDo empty = new DataAuthDetailDo();
        empty.setDeptIdList(Collections.emptyList());
        empty.setDeptIdPathList(Collections.emptyList());
        return AppResponse.success(empty);
    }
}
