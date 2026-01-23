package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.Role;
import com.iflytek.sec.uap.client.core.dto.role.UapRole;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;

/**
 * @desc: UapRole到Role的映射器
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/25 10:17
 */
@Component
public class RoleMapper {

    /**
     * 将 UapRole 转换为通用 Role
     */
    public Role fromUapRole(UapRole uapRole) {
        if (uapRole == null) {
            return null;
        }

        Role role = new Role();
        role.setId(uapRole.getId());
        role.setName(uapRole.getName());
        role.setCode(uapRole.getCode());
        role.setStatus(uapRole.getStatus());
        role.setAppId(uapRole.getAppId());
        role.setAppName(uapRole.getAppName());
        role.setHigherRole(uapRole.getHigherRole());
        role.setHigherName(uapRole.getHigherName());
        role.setSort(uapRole.getSort());
        role.setRemark(uapRole.getRemark());
        role.setIsMustBind(uapRole.getIsMustBind());
        role.setFirstLevelId(uapRole.getFirstLevelId());
        role.setCreateTime(uapRole.getCreateTime());
        role.setUpdateTime(uapRole.getUpdateTime());

        return role;
    }

    /**
     * 批量转换
     */
    public List<Role> fromUapRoles(List<UapRole> uapRoles) {
        if (uapRoles == null) {
            return Collections.emptyList();
        }

        return uapRoles.stream().map(this::fromUapRole).collect(Collectors.toList());
    }
}
