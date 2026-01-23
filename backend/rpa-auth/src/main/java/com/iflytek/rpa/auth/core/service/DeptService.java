package com.iflytek.rpa.auth.core.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 部门服务
 */
public interface DeptService {

    /**
     * 查询部门树、人数、负责人
     * @param request HTTP请求
     * @return 部门树和人员信息
     */
    AppResponse<?> treeAndPerson(HttpServletRequest request);

    /**
     * 优化版本的部门树和人员查询（严格限制两层）
     * 包含以下优化：
     * 1. 只返回必要字段（name, userNum, userName, id, orgId, pid）
     * 2. 使用Redis缓存，缓存时间1小时
     * 3. 严格限制只返回顶级部门和次级部门（两层结构）
     * 4. 优化并行查询逻辑
     *
     * @param request HTTP请求
     * @return 优化后的响应结果，最多包含两层部门结构
     */
    AppResponse<java.util.Map<String, Object>> treeAndPersonOptimized(HttpServletRequest request);

    /**
     * 新增部门
     * @param createUapOrgDto 创建部门DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> addDept(CreateUapOrgDto createUapOrgDto, HttpServletRequest request);

    //    PageDto<Org> queryOrgPageList(String tenantId, OrgListDto orgListDto, HttpServletRequest request);

    /**
     * 获取部门树 todo 只返回有权限的
     * @param request HTTP请求
     * @return 部门树
     * @throws Exception 异常
     */
    AppResponse<TreeNode> queryTreeList(HttpServletRequest request) throws Exception;

    /**
     * 通过部门父节点的id查询所有部门子节点
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门子节点列表
     * @throws Exception 异常
     */
    AppResponse<List<DeptTreeNodeVo>> queryDeptTreeByPid(QueryDeptNodeDto dto, HttpServletRequest request)
            throws Exception;

    /**
     * 编辑部门
     * @param editOrgDto 编辑部门DTO
     * @param request HTTP请求
     * @return 编辑结果
     */
    AppResponse<String> editDept(EditOrgDto editOrgDto, HttpServletRequest request);

    /**
     * 删除部门
     * @param deleteCommonDto 删除部门DTO
     * @param request HTTP请求
     * @return 删除结果
     */
    AppResponse<String> deleteDept(DeleteCommonDto deleteCommonDto, HttpServletRequest request);

    /**
     * 通过deptId查询部门名
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门名
     */
    AppResponse<DeptNameVo> queryDeptNameByDeptId(QueryDeptIdDto dto, HttpServletRequest request);

    /**
     * 获取租户名
     * @param request HTTP请求
     * @return 租户名
     */
    AppResponse<String> queryTenantName(HttpServletRequest request);

    /**
     * 部门人数信息查询
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门人数节点列表
     * @throws JsonProcessingException JSON处理异常
     */
    AppResponse<List<DeptPersonTreeNodeVo>> queryDeptPersonNodeByPid(QueryDeptNodeDto dto, HttpServletRequest request)
            throws JsonProcessingException;

    /**
     * 查询当前机构的所有用户
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 用户列表
     * @throws Exception 异常
     */
    AppResponse<List<UserVo>> queryAllUserByDeptId(QueryDeptIdDto dto, HttpServletRequest request) throws Exception;

    /**
     * 获取当前登录用户的部门levelCode，即deptIdPath
     * @param request HTTP请求
     * @return 部门levelCode
     */
    AppResponse<String> getCurrentLevelCode(HttpServletRequest request);

    /**
     * 获取当前登录用户的部门ID
     * @param request HTTP请求
     * @return 部门ID
     */
    AppResponse<String> getCurrentDeptId(HttpServletRequest request);

    /**
     * 获取当前登录用户的部门详细信息
     * @param request HTTP请求
     * @return 部门信息
     */
    AppResponse<Org> getCurrentDeptInfo(HttpServletRequest request);

    /**
     * 根据部门ID查询部门详细信息
     * @param id 部门ID
     * @param request HTTP请求
     * @return 部门信息
     */
    AppResponse<Org> getDeptInfoByDeptId(String id, HttpServletRequest request);

    /**
     * 查询部门ID对应的levelCode
     * @param id 部门ID
     * @param request HTTP请求
     * @return levelCode
     */
    AppResponse<String> getLevelCodeByDeptId(String id, HttpServletRequest request);

    /**
     * 查询指定机构及所有子机构的用户数量
     * @param id 部门ID
     * @param request HTTP请求
     * @return 用户数量
     */
    AppResponse<Long> getUserNumByDeptId(String id, HttpServletRequest request);

    /**
     * 根据部门ID列表获取部门信息列表
     * @param orgIdList 部门ID列表
     * @param request HTTP请求
     * @return 部门信息列表
     */
    AppResponse<List<Org>> queryOrgListByIds(List<String> orgIdList, HttpServletRequest request);

    /**
     * 根据用户ID获取部门ID
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 部门ID
     */
    AppResponse<String> getDeptIdByUserId(String userId, String tenantId, HttpServletRequest request);

    /**
     * 查询数据权限，是一个部门列表
     * @param request HTTP请求
     * @return 数据权限详情
     */
    AppResponse<DataAuthDetailDo> getDataAuthWithDeptList(HttpServletRequest request);
}
