package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.DeptService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 部门
 */
@RestController
@RequestMapping("/dept")
@Slf4j
public class DeptController {

    @Autowired
    private DeptService deptService;

    /**
     * 获取部门树 todo 只返回有权限的
     * @param
     * @param request
     * @return
     */
    @GetMapping("/queryTreeList")
    public AppResponse<TreeNode> queryTreeList(HttpServletRequest request) throws Exception {
        return deptService.queryTreeList(request);
    }

    /**
     * 通过部门父节点的id查询所有部门子节点
     * @param request
     * @return
     * @throws Exception
     */
    @PostMapping("queryDeptNodeByPid")
    public AppResponse<List<DeptTreeNodeVo>> queryDeptTreeByPid(
            @RequestBody QueryDeptNodeDto dto, HttpServletRequest request) throws Exception {
        return deptService.queryDeptTreeByPid(dto, request);
    }

    /**
     * 获取租户名 (兼容用)
     * @param request
     * @return
     * @throws Exception
     */
    @GetMapping("queryTenantName")
    public AppResponse<String> queryTenantName(HttpServletRequest request) throws Exception {
        return deptService.queryTenantName(request);
    }
    /**
     * 通过deptId查询部门名
     */
    @PostMapping("queryDeptNameByDeptId")
    public AppResponse<DeptNameVo> queryDeptNameByDeptId(@RequestBody QueryDeptIdDto dto, HttpServletRequest request)
            throws Exception {
        return deptService.queryDeptNameByDeptId(dto, request);
    }

    /**
     * 新增部门
     * @param
     * @param request
     * @return
     */
    @PostMapping("/add")
    public AppResponse<String> addDept(@RequestBody CreateUapOrgDto createUapOrgDto, HttpServletRequest request) {
        return deptService.addDept(createUapOrgDto, request);
    }

    /**
     * 编辑部门
     * @param
     * @param request
     * @return
     */
    @PostMapping("/edit")
    public AppResponse<String> editDept(@RequestBody EditOrgDto editOrgDto, HttpServletRequest request) {
        return deptService.editDept(editOrgDto, request);
    }

    /**
     * 删除部门
     * @param
     * @param request
     * @return
     */
    @PostMapping("/delete")
    public AppResponse<String> deleteDept(@RequestBody DeleteCommonDto deleteCommonDto, HttpServletRequest request) {
        return deptService.deleteDept(deleteCommonDto, request);
    }

    /**
     * 查询部门树、人数、负责人
     * @param
     * @param request
     * @return
     */
    @GetMapping("/treeAndPerson")
    public AppResponse<java.util.Map<String, Object>> treeAndPerson(HttpServletRequest request) {
        return deptService.treeAndPersonOptimized(request);
    }

    /**
     * 部门人数信息查询
     * @param request
     * @return
     * @throws Exception
     */
    @PostMapping("queryDeptPersonNodeByPid")
    public AppResponse<List<DeptPersonTreeNodeVo>> queryDeptPersonNodeByPid(
            @RequestBody QueryDeptNodeDto dto, HttpServletRequest request) throws Exception {

        return deptService.queryDeptPersonNodeByPid(dto, request);
    }

    /**
     * 查询当前机构的所有用户
     * @param
     * @param request
     * @return
     */
    @PostMapping("/queryUserListByDeptId")
    public AppResponse<List<UserVo>> queryAllUserByDeptId(@RequestBody QueryDeptIdDto dto, HttpServletRequest request)
            throws Exception {
        return deptService.queryAllUserByDeptId(dto, request);
    }

    /**
     * 获取当前登录用户的部门levelCode，即deptIdPath
     * @param request HTTP请求
     * @return 部门levelCode
     */
    @GetMapping("/current/levelCode")
    public AppResponse<String> getCurrentLevelCode(HttpServletRequest request) {
        return deptService.getCurrentLevelCode(request);
    }

    /**
     * 获取当前登录用户的部门ID
     * @param request HTTP请求
     * @return 部门ID
     */
    @GetMapping("/current/id")
    public AppResponse<String> getCurrentDeptId(HttpServletRequest request) {
        return deptService.getCurrentDeptId(request);
    }

    /**
     * 获取当前登录用户的部门详细信息
     * @param request HTTP请求
     * @return 部门信息
     */
    @GetMapping("/current")
    public AppResponse<Org> getCurrentDeptInfo(HttpServletRequest request) {
        return deptService.getCurrentDeptInfo(request);
    }

    /**
     * 根据部门ID查询部门详细信息
     * @param id 部门ID
     * @param request HTTP请求
     * @return 部门信息
     */
    @GetMapping("/info")
    public AppResponse<Org> getDeptInfoByDeptId(@RequestParam("id") String id, HttpServletRequest request) {
        return deptService.getDeptInfoByDeptId(id, request);
    }

    /**
     * 查询部门ID对应的levelCode
     * @param id 部门ID
     * @param request HTTP请求
     * @return levelCode
     */
    @GetMapping("/levelCode")
    public AppResponse<String> getLevelCodeByDeptId(@RequestParam("id") String id, HttpServletRequest request) {
        return deptService.getLevelCodeByDeptId(id, request);
    }

    /**
     * 查询指定机构及所有子机构的用户数量
     * @param id 部门ID
     * @param request HTTP请求
     * @return 用户数量
     */
    @GetMapping("/userNum")
    public AppResponse<Long> getUserNumByDeptId(@RequestParam("id") String id, HttpServletRequest request) {
        return deptService.getUserNumByDeptId(id, request);
    }

    /**
     * 根据部门ID列表获取部门信息列表
     * @param orgIdList 部门ID列表
     * @param request HTTP请求
     * @return 部门信息列表
     */
    @PostMapping("/queryByIds")
    public AppResponse<List<Org>> queryOrgListByIds(@RequestBody List<String> orgIdList, HttpServletRequest request) {
        return deptService.queryOrgListByIds(orgIdList, request);
    }

    /**
     * 根据用户ID获取部门ID
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 部门ID
     */
    @GetMapping("/user/deptId")
    public AppResponse<String> getDeptIdByUserId(
            @RequestParam("userId") String userId,
            @RequestParam("tenantId") String tenantId,
            HttpServletRequest request) {
        return deptService.getDeptIdByUserId(userId, tenantId, request);
    }

    /**
     * 查询数据权限，是一个部门列表
     * @param request HTTP请求
     * @return 数据权限详情
     */
    @GetMapping("/dataAuth")
    public AppResponse<DataAuthDetailDo> getDataAuthWithDeptList(HttpServletRequest request) {
        return deptService.getDataAuthWithDeptList(request);
    }
}
