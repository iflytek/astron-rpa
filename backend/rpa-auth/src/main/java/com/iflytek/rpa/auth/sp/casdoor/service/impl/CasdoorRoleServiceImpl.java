package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.RoleService;
import com.iflytek.rpa.auth.sp.casdoor.dao.CasdoorRoleDao;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorRoleMapper;
import com.iflytek.rpa.auth.sp.casdoor.utils.SessionUserUtils;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 9:46
 */
@Slf4j
@Service("casdoorRoleService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorRoleServiceImpl implements RoleService {

    @Autowired
    private CasdoorRoleMapper casdoorRoleMapper;

    @Autowired
    private org.casbin.casdoor.service.RoleService roleService;

    @Autowired
    private CasdoorRoleDao casdoorRoleDao;

    @Value("${casdoor.database.name:casdoor}")
    private String databaseName;

    /**
     * 查询应用内全部角色列表
     * @param request HTTP请求
     * @return 角色列表
     */
    @Override
    public AppResponse<List<Role>> getUserRoleListInApp(HttpServletRequest request) throws IOException {
        try {
            log.debug("开始查询应用内全部角色列表");

            // casdoor的角色列表是直接隶属于组织的，组织中包含应用，应用和角色之间无绑定关系，这里默认按组织下所有角色列表处理
            AppResponse<List<Role>> response = getUserRoleList(request);

            if (response.ok() && response.getData() != null) {
                log.debug("查询应用内全部角色列表成功，共 {} 个角色", response.getData().size());
            }

            return response;
        } catch (Exception e) {
            log.error("查询应用内全部角色列表异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询应用内全部角色列表异常: " + e.getMessage());
        }
    }

    /**
     * 查询角色列表
     * @param request HTTP请求
     * @return 角色列表
     */
    @Override
    public AppResponse<List<Role>> getUserRoleList(HttpServletRequest request) throws IOException {
        try {
            log.debug("开始查询角色列表");

            // 查询Casdoor角色列表
            List<org.casbin.casdoor.entity.Role> casdoorRoles = roleService.getRoles();
            if (casdoorRoles == null) {
                log.debug("查询角色列表结果为空");
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个Casdoor角色", casdoorRoles.size());

            // 转换为通用角色对象列表，过滤掉转换失败的对象
            List<Role> roles = casdoorRoles.stream()
                    .filter(role -> role != null)
                    .map(role -> {
                        try {
                            return casdoorRoleMapper.toCommonRole(role);
                        } catch (Exception e) {
                            log.warn("角色信息转换失败，roleName: {}", role != null ? role.name : "null", e);
                            return null;
                        }
                    })
                    .filter(role -> role != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个角色", roles.size());
            return AppResponse.success(roles);
        } catch (IOException e) {
            log.error("查询角色列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询角色列表失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("查询角色列表异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询角色列表异常: " + e.getMessage());
        }
    }

    /**
     * 查询角色详情
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 角色详情
     */
    @Override
    public AppResponse<Role> queryRoleDetail(GetRoleDto dto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始查询角色详情，roleId: {}", dto != null ? dto.getId() : "null");

            // 参数校验
            if (dto == null || StringUtils.isEmpty(dto.getId())) {
                log.warn("查询角色详情失败：角色ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色ID不能为空");
            }

            String roleId = dto.getId();
            log.debug("查询角色详情，roleId: {} (对应casdoor的角色名称)", roleId);

            // 查询Casdoor角色详情（这里的角色id对应casdoor的角色名称）
            org.casbin.casdoor.entity.Role casdoorRole = roleService.getRole(roleId);
            if (casdoorRole == null) {
                log.warn("未查询到角色信息，roleId: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "角色不存在");
            }

            // 转换为通用角色对象
            Role commonRole = casdoorRoleMapper.toCommonRole(casdoorRole);
            if (commonRole == null) {
                log.warn("角色信息转换失败，roleId: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "角色信息转换失败");
            }

            log.debug("查询角色详情成功，roleId: {}, roleName: {}", roleId, commonRole.getName());
            return AppResponse.success(commonRole);
        } catch (IOException e) {
            log.error("查询角色详情失败，roleId: {}", dto != null ? dto.getId() : "null", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询角色详情失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("查询角色详情异常，roleId: {}", dto != null ? dto.getId() : "null", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询角色详情异常: " + e.getMessage());
        }
    }

    /**
     * 新增角色
     * @param createRoleDto 新增角色DTO
     * @param request HTTP请求
     * @return 结果
     */
    @Override
    public AppResponse<String> addRole(CreateRoleDto createRoleDto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始新增角色");

            // 参数校验
            if (createRoleDto == null) {
                log.warn("新增角色失败：参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "新增角色信息不能为空");
            }
            if (StringUtils.isBlank(createRoleDto.getName())) {
                log.warn("新增角色失败：角色名称为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色名称不能为空");
            }

            String roleName = createRoleDto.getName().trim();
            String roleCode = createRoleDto.getCode().trim();
            log.debug("新增角色参数，name: {}, code: {}", roleName, roleCode);

            // Casdoor中使用name作为唯一标识，这里使用角色编码code作为Casdoor的name
            org.casbin.casdoor.entity.Role existing = roleService.getRole(roleCode);
            if (existing != null) {
                log.warn("新增角色失败：角色编码已存在，code: {}", roleCode);
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "角色编码已存在");
            }

            // 组装Casdoor Role
            org.casbin.casdoor.entity.Role casdoorRole = new org.casbin.casdoor.entity.Role();
            // owner取当前用户的租户
            String currentTenantOwner = getCurrentTenantOwner(request);
            casdoorRole.owner = currentTenantOwner;
            casdoorRole.name = roleCode;
            casdoorRole.displayName = roleName;
            casdoorRole.description = createRoleDto.getRemark();
            casdoorRole.isEnabled = createRoleDto.getStatus() == null || createRoleDto.getStatus() == 1;

            log.debug(
                    "调用Casdoor API新增角色，owner: {}, name: {}, displayName: {}",
                    casdoorRole.owner,
                    casdoorRole.name,
                    casdoorRole.displayName);
            CasdoorResponse<String, Object> addRoleResponse = roleService.addRole(casdoorRole);

            if (addRoleResponse == null) {
                log.error("新增角色失败：Casdoor API返回为空，code: {}", roleCode);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "新增角色失败：API返回为空");
            }

            if (addRoleResponse.getStatus() != null && !"ok".equals(addRoleResponse.getStatus())) {
                log.error(
                        "新增角色失败：Casdoor API返回错误，code: {}, status: {}, msg: {}",
                        roleCode,
                        addRoleResponse.getStatus(),
                        addRoleResponse.getMsg());
                return AppResponse.error(
                        ErrorCodeEnum.E_API_EXCEPTION,
                        "新增角色失败: " + (addRoleResponse.getMsg() != null ? addRoleResponse.getMsg() : "未知错误"));
            }

            log.debug("新增角色成功，code: {}, name: {}", roleCode, roleName);
            return AppResponse.success("新增角色成功");
        } catch (IOException e) {
            log.error("新增角色失败（IO异常）", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "新增角色失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("新增角色异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "新增角色异常: " + e.getMessage());
        }
    }

    /**
     * 编辑角色
     * @param updateRoleDto 更新角色DTO
     * @param request HTTP请求
     * @return 结果
     */
    @Override
    public AppResponse<String> updateRole(UpdateRoleDto updateRoleDto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始编辑角色");

            // 参数校验
            if (updateRoleDto == null) {
                log.warn("编辑角色失败：参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "更新角色信息不能为空");
            }
            if (StringUtils.isBlank(updateRoleDto.getId())) {
                log.warn("编辑角色失败：角色ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色ID不能为空");
            }

            String roleId = updateRoleDto.getId().trim();
            log.debug("编辑角色参数，id: {}, name: {}, code: {}", roleId, updateRoleDto.getName(), updateRoleDto.getCode());

            // Casdoor中使用name作为唯一标识，约定：Role.id 保存的是 Casdoor 的 role.name（即code）
            org.casbin.casdoor.entity.Role existingRole = roleService.getRole(roleId);
            if (existingRole == null) {
                log.warn("编辑角色失败：角色不存在，id: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "角色不存在");
            }

            // 在不改变Casdoor角色name的前提下，更新显示名、描述、启用状态等信息
            org.casbin.casdoor.entity.Role casdoorRole = new org.casbin.casdoor.entity.Role();
            casdoorRole.owner = existingRole.owner;
            casdoorRole.name = existingRole.name; // 保持原有唯一标识不变

            // 显示名称：优先使用更新名称，否则保留原值
            if (StringUtils.isNotBlank(updateRoleDto.getName())) {
                casdoorRole.displayName = updateRoleDto.getName().trim();
            } else {
                casdoorRole.displayName = existingRole.displayName;
            }

            // 描述
            if (StringUtils.isNotBlank(updateRoleDto.getRemark())) {
                casdoorRole.description = updateRoleDto.getRemark().trim();
            } else {
                casdoorRole.description = existingRole.description;
            }

            // 启用状态：status (1启用 -> isEnabled=true, 0停用 -> isEnabled=false)
            if (updateRoleDto.getStatus() != null) {
                casdoorRole.isEnabled = (updateRoleDto.getStatus() == 1);
            } else {
                casdoorRole.isEnabled = existingRole.isEnabled;
            }

            // 保留原有绑定关系
            casdoorRole.users = existingRole.users;
            casdoorRole.roles = existingRole.roles;

            log.debug("调用Casdoor API更新角色，name: {}, displayName: {}", casdoorRole.name, casdoorRole.displayName);
            CasdoorResponse<String, Object> updateRoleResponse = roleService.updateRole(casdoorRole);

            if (updateRoleResponse == null) {
                log.error("编辑角色失败：Casdoor API返回为空，id: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "编辑角色失败：API返回为空");
            }

            if (updateRoleResponse.getStatus() != null && !"ok".equals(updateRoleResponse.getStatus())) {
                log.error(
                        "编辑角色失败：Casdoor API返回错误，id: {}, status: {}, msg: {}",
                        roleId,
                        updateRoleResponse.getStatus(),
                        updateRoleResponse.getMsg());
                return AppResponse.error(
                        ErrorCodeEnum.E_API_EXCEPTION,
                        "编辑角色失败: " + (updateRoleResponse.getMsg() != null ? updateRoleResponse.getMsg() : "未知错误"));
            }

            log.debug("编辑角色成功，id: {}, name: {}", roleId, casdoorRole.displayName);
            return AppResponse.success("编辑角色成功");
        } catch (IOException e) {
            log.error("编辑角色失败（IO异常）", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "编辑角色失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("编辑角色异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "编辑角色异常: " + e.getMessage());
        }
    }

    /**
     * 删除角色
     * @param deleteCommonDto 删除角色DTO
     * @param request HTTP请求
     * @return 删除结果
     */
    @Override
    public AppResponse<String> deleteRole(DeleteCommonDto deleteCommonDto, HttpServletRequest request)
            throws IOException {
        try {
            log.debug("开始删除角色");

            // 参数校验
            if (deleteCommonDto == null || StringUtils.isBlank(deleteCommonDto.getId())) {
                log.warn("删除角色失败：角色ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色ID不能为空");
            }

            String roleId = deleteCommonDto.getId().trim();
            log.debug("准备删除角色，id: {}", roleId);

            // 先查询角色是否存在
            org.casbin.casdoor.entity.Role existingRole = roleService.getRole(roleId);
            if (existingRole == null) {
                log.warn("删除角色失败：角色不存在，id: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "角色不存在");
            }

            // 调用Casdoor删除接口
            log.debug("调用Casdoor API删除角色，name: {}", existingRole.name);
            CasdoorResponse<String, Object> deleteRoleResponse = roleService.deleteRole(existingRole);

            if (deleteRoleResponse == null) {
                log.error("删除角色失败：Casdoor API返回为空，id: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "删除角色失败：API返回为空");
            }

            if (deleteRoleResponse.getStatus() != null && !"ok".equals(deleteRoleResponse.getStatus())) {
                log.error(
                        "删除角色失败：Casdoor API返回错误，id: {}, status: {}, msg: {}",
                        roleId,
                        deleteRoleResponse.getStatus(),
                        deleteRoleResponse.getMsg());
                return AppResponse.error(
                        ErrorCodeEnum.E_API_EXCEPTION,
                        "删除角色失败: " + (deleteRoleResponse.getMsg() != null ? deleteRoleResponse.getMsg() : "未知错误"));
            }

            log.debug("删除角色成功，id: {}", roleId);
            return AppResponse.success("删除角色成功");
        } catch (IOException e) {
            log.error("删除角色失败（IO异常）", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "删除角色失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("删除角色异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "删除角色异常: " + e.getMessage());
        }
    }

    /**
     * 根据名称模糊查询角色
     * @param listRoleDto 查询条件
     * @param request HTTP请求
     * @return 分页结果
     */
    @Override
    public AppResponse<PageDto<Role>> searchRole(ListRoleDto listRoleDto, HttpServletRequest request) {
        try {
            // 参数校验
            if (listRoleDto == null
                    || listRoleDto.getRoleName() == null
                    || listRoleDto.getRoleName().trim().isEmpty()) {
                log.warn("根据名称模糊查询角色失败：角色名称为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色名称不能为空");
            }

            String keyword = listRoleDto.getRoleName().trim();
            log.debug("开始根据名称模糊查询角色，keyword: {}", keyword);

            // 调用DAO查询Casdoor角色列表（不分页，最多1000条）
            String currentTenantOwner = getCurrentTenantOwner(request);
            List<org.casbin.casdoor.entity.Role> casdoorRoles =
                    casdoorRoleDao.searchRoleByName(keyword, currentTenantOwner, databaseName);

            if (casdoorRoles == null || casdoorRoles.isEmpty()) {
                log.debug("根据名称模糊查询角色结果为空，keyword: {}", keyword);
                PageDto<Role> emptyPage = new PageDto<>();
                emptyPage.setResult(Collections.emptyList());
                emptyPage.setCurrentPageNo(listRoleDto.getPageNum());
                emptyPage.setPageSize(listRoleDto.getPageSize());
                emptyPage.setTotalCount(0L);
                return AppResponse.success(emptyPage);
            }

            log.debug("根据名称模糊查询到 {} 个Casdoor角色，keyword: {}", casdoorRoles.size(), keyword);

            // Casdoor Role 转通用 Role
            List<Role> allRoles = casdoorRoles.stream()
                    .filter(role -> role != null)
                    .map(role -> {
                        try {
                            return casdoorRoleMapper.toCommonRole(role);
                        } catch (Exception e) {
                            log.warn("角色信息转换失败，roleName: {}", role != null ? role.name : "null", e);
                            return null;
                        }
                    })
                    .filter(role -> role != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个角色为通用角色对象，keyword: {}", allRoles.size(), keyword);

            // Java 侧分页
            int pageNum = listRoleDto.getPageNum() == null ? 1 : listRoleDto.getPageNum();
            int pageSize = listRoleDto.getPageSize() == null ? 10 : listRoleDto.getPageSize();
            if (pageNum < 1) {
                pageNum = 1;
            }
            if (pageSize <= 0) {
                pageSize = 10;
            }

            int fromIndex = (pageNum - 1) * pageSize;
            int toIndex = Math.min(fromIndex + pageSize, allRoles.size());

            List<Role> pageResult;
            if (fromIndex >= allRoles.size()) {
                pageResult = Collections.emptyList();
            } else {
                pageResult = allRoles.subList(fromIndex, toIndex);
            }

            PageDto<Role> pageDto = new PageDto<>();
            pageDto.setResult(pageResult);
            pageDto.setCurrentPageNo(pageNum);
            pageDto.setPageSize(pageSize);
            pageDto.setTotalCount((long) allRoles.size());

            log.debug(
                    "根据名称模糊查询角色成功，keyword: {}，总数: {}，当前页: {}，每页: {}，当前页数量: {}",
                    keyword,
                    allRoles.size(),
                    pageNum,
                    pageSize,
                    pageResult.size());

            return AppResponse.success(pageDto);
        } catch (Exception e) {
            log.error("根据名称模糊查询角色异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据名称模糊查询角色异常: " + e.getMessage());
        }
    }

    /**
     * 从当前登录用户获取租户ID（Casdoor中的 owner）
     *
     * @param request HTTP请求
     * @return 租户ID（owner），获取失败时返回null
     */
    private String getCurrentTenantOwner(HttpServletRequest request) {
        return SessionUserUtils.getTenantOwnerFromSession(request);
    }
}
