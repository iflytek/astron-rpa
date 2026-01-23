package com.iflytek.rpa.auth.sp.casdoor.mapper;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor Role 与通用 Role 实体类之间的映射器，仅在casdoor profile下生效
 * @author: Auto Generated
 * @create: 2025/12/11
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorRoleMapper {

    private static final String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    private static final String ISO_DATE_TIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";
    private static final SimpleDateFormat DATE_TIME_FORMATTER = new SimpleDateFormat(DATE_TIME_FORMAT);
    private static final SimpleDateFormat ISO_DATE_TIME_FORMATTER = new SimpleDateFormat(ISO_DATE_TIME_FORMAT);

    /**
     * 将 Casdoor Role 转换为通用 Role
     *
     * @param casdoorRole Casdoor 角色对象
     * @return 通用角色对象
     */
    public com.iflytek.rpa.auth.core.entity.Role toCommonRole(org.casbin.casdoor.entity.Role casdoorRole) {
        if (casdoorRole == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.Role role = new com.iflytek.rpa.auth.core.entity.Role();

        // TODO: id字段需要根据业务逻辑生成，Casdoor的name可能作为唯一标识
        // 暂时使用name作为id，后续可能需要根据实际业务调整
        role.setId(casdoorRole.name);

        // 基本字段映射
        // 显示名称映射到角色名称，如果为空则使用name
        role.setName(
                casdoorRole.displayName != null && !casdoorRole.displayName.isEmpty()
                        ? casdoorRole.displayName
                        : casdoorRole.name);
        role.setCode(casdoorRole.name); // Casdoor的name作为角色编码

        // 状态字段转换：isEnabled (true -> status=1启用, false -> status=0停用)
        role.setStatus(casdoorRole.isEnabled ? 1 : 0);

        // TODO: appId字段需要根据业务逻辑确定，暂时使用空
        // owner可能代表应用/租户标识，需要确认业务含义
        role.setAppId("");

        // 备注字段
        role.setRemark(casdoorRole.description);

        // 日期字段转换
        role.setCreateTime(parseDateTime(casdoorRole.createdTime));
        // updateTime在Casdoor中没有对应字段，设置为null或与createTime相同
        role.setUpdateTime(parseDateTime(casdoorRole.createdTime));

        // 默认值设置
        if (role.getSort() == null) {
            role.setSort(1); // 默认排序为1
        }
        if (role.getIsMustBind() == null) {
            role.setIsMustBind(1); // 默认强绑定
        }

        // 以下字段在Casdoor中没有对应，设置为null或默认值
        // higherRole, higherName, firstLevelId, appName 需要根据业务逻辑补充

        return role;
    }

    /**
     * 将通用 Role 转换为 Casdoor Role
     *
     * @param role 通用角色对象
     * @return Casdoor 角色对象
     */
    public org.casbin.casdoor.entity.Role toCasdoorRole(com.iflytek.rpa.auth.core.entity.Role role) {
        if (role == null) {
            return null;
        }

        org.casbin.casdoor.entity.Role casdoorRole = new org.casbin.casdoor.entity.Role();

        // TODO: name字段需要确认，使用code作为name（角色编码作为Casdoor的name）
        // 如果code为空，可能需要使用id或其他字段，需要根据业务逻辑调整
        if (role.getCode() != null && !role.getCode().isEmpty()) {
            casdoorRole.name = role.getCode();
        } else {
            // TODO: 如果code为空，使用id作为name，需要确认业务逻辑
            casdoorRole.name = role.getId() != null ? role.getId() : "";
        }

        // 显示名称映射，如果name为空则使用code
        casdoorRole.displayName = role.getName() != null && !role.getName().isEmpty()
                ? role.getName()
                : (role.getCode() != null ? role.getCode() : "");

        // 状态字段转换：status (1启用 -> isEnabled=true, 0停用 -> isEnabled=false)
        casdoorRole.isEnabled = role.getStatus() != null && role.getStatus() == 1;

        // owner在Casdoor是指角色所附属的组织，这里通用实体没有组织信息，因此置空
        casdoorRole.owner = "";

        // 备注字段
        casdoorRole.description = role.getRemark() != null ? role.getRemark() : "";

        // 日期字段转换：Date -> String
        casdoorRole.createdTime = formatDateTime(role.getCreateTime());
        // Casdoor Role没有updatedTime字段，只使用createdTime

        // 以下字段在Casdoor Role中需要设置默认值
        casdoorRole.users = new String[0]; // TODO: 需要根据业务逻辑填充用户列表
        casdoorRole.roles = new String[0]; // TODO: 需要根据业务逻辑填充子角色列表

        return casdoorRole;
    }

    /**
     * 解析日期时间字符串为Date对象
     *
     * @param dateTimeStr 日期时间字符串
     * @return Date对象，解析失败返回null
     */
    private Date parseDateTime(String dateTimeStr) {
        if (dateTimeStr == null || dateTimeStr.isEmpty()) {
            return null;
        }
        try {
            // 尝试ISO格式 (yyyy-MM-dd'T'HH:mm:ss)
            if (dateTimeStr.contains("T")) {
                String isoStr = dateTimeStr;
                // 移除时区信息（如果有）
                if (isoStr.contains("+") || isoStr.endsWith("Z")) {
                    isoStr = isoStr.replaceAll("[+Z].*", "");
                }
                // 尝试解析ISO格式
                if (isoStr.length() >= 19) {
                    isoStr = isoStr.substring(0, 19);
                    synchronized (ISO_DATE_TIME_FORMATTER) {
                        return ISO_DATE_TIME_FORMATTER.parse(isoStr);
                    }
                }
            }
            // 尝试标准日期时间格式 (yyyy-MM-dd HH:mm:ss)
            if (dateTimeStr.length() >= DATE_TIME_FORMAT.length()) {
                String dtStr = dateTimeStr.substring(0, DATE_TIME_FORMAT.length());
                synchronized (DATE_TIME_FORMATTER) {
                    return DATE_TIME_FORMATTER.parse(dtStr);
                }
            }
        } catch (ParseException e) {
            // 解析失败，返回null
        }
        return null;
    }

    /**
     * 格式化Date对象为日期时间字符串
     *
     * @param date Date对象
     * @return 日期时间字符串，date为null返回空字符串
     */
    private String formatDateTime(Date date) {
        if (date == null) {
            return "";
        }
        synchronized (DATE_TIME_FORMATTER) {
            return DATE_TIME_FORMATTER.format(date);
        }
    }
}
