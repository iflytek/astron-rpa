package com.iflytek.rpa.auth.sp.casdoor.mapper;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor Permission 与通用 Permission 实体类之间的映射器，仅在casdoor profile下生效
 * @author: Auto Generated
 * @create: 2025/12/11
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorPermissionMapper {

    /**
     * 将 Casdoor Permission 转换为通用 Permission
     * 由于两个实体类结构相同，直接进行字段复制
     *
     * @param casdoorPermission Casdoor 权限对象
     * @return 通用权限对象
     */
    public com.iflytek.rpa.auth.core.entity.Permission toCommonPermission(
            org.casbin.casdoor.entity.Permission casdoorPermission) {
        if (casdoorPermission == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.Permission permission = new com.iflytek.rpa.auth.core.entity.Permission();

        // 基本字段映射（结构相同，直接复制）
        permission.owner = casdoorPermission.owner;
        permission.name = casdoorPermission.name;
        permission.createdTime = casdoorPermission.createdTime;
        permission.displayName = casdoorPermission.displayName;
        permission.description = casdoorPermission.description;

        // 数组字段映射
        permission.users = casdoorPermission.users;
        permission.roles = casdoorPermission.roles;
        permission.domains = casdoorPermission.domains;

        // 模型和资源字段映射
        permission.model = casdoorPermission.model;
        permission.adapter = casdoorPermission.adapter;
        permission.resourceType = casdoorPermission.resourceType;
        permission.resources = casdoorPermission.resources;
        permission.actions = casdoorPermission.actions;
        permission.effect = casdoorPermission.effect;

        // 状态字段映射
        permission.isEnabled = casdoorPermission.isEnabled;

        // 审批相关字段映射
        permission.submitter = casdoorPermission.submitter;
        permission.approver = casdoorPermission.approver;
        permission.approveTime = casdoorPermission.approveTime;
        permission.state = casdoorPermission.state;

        return permission;
    }

    /**
     * 将通用 Permission 转换为 Casdoor Permission
     * 由于两个实体类结构相同，直接进行字段复制
     *
     * @param permission 通用权限对象
     * @return Casdoor 权限对象
     */
    public org.casbin.casdoor.entity.Permission toCasdoorPermission(
            com.iflytek.rpa.auth.core.entity.Permission permission) {
        if (permission == null) {
            return null;
        }

        org.casbin.casdoor.entity.Permission casdoorPermission = new org.casbin.casdoor.entity.Permission();

        // 基本字段映射（结构相同，直接复制）
        casdoorPermission.owner = permission.owner;
        casdoorPermission.name = permission.name;
        casdoorPermission.createdTime = permission.createdTime;
        casdoorPermission.displayName = permission.displayName;
        casdoorPermission.description = permission.description;

        // 数组字段映射
        casdoorPermission.users = permission.users;
        casdoorPermission.roles = permission.roles;
        casdoorPermission.domains = permission.domains;

        // 模型和资源字段映射
        casdoorPermission.model = permission.model;
        casdoorPermission.adapter = permission.adapter;
        casdoorPermission.resourceType = permission.resourceType;
        casdoorPermission.resources = permission.resources;
        casdoorPermission.actions = permission.actions;
        casdoorPermission.effect = permission.effect;

        // 状态字段映射
        casdoorPermission.isEnabled = permission.isEnabled;

        // 审批相关字段映射
        casdoorPermission.submitter = permission.submitter;
        casdoorPermission.approver = permission.approver;
        casdoorPermission.approveTime = permission.approveTime;
        casdoorPermission.state = permission.state;

        return casdoorPermission;
    }
}
