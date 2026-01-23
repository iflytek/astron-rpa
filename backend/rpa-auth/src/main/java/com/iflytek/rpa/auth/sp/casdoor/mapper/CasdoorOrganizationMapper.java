package com.iflytek.rpa.auth.sp.casdoor.mapper;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor Group 与通用 Org 实体类之间的映射器，仅在casdoor profile下生效
 * 注意：Casdoor的Organization对应通用的Tenant，Casdoor的Group对应通用的Org
 * @author: Auto Generated
 * @create: 2025/12/11
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorOrganizationMapper {

    private static final String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    private static final String ISO_DATE_TIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";
    private static final SimpleDateFormat DATE_TIME_FORMATTER = new SimpleDateFormat(DATE_TIME_FORMAT);
    private static final SimpleDateFormat ISO_DATE_TIME_FORMATTER = new SimpleDateFormat(ISO_DATE_TIME_FORMAT);

    /**
     * 将 Casdoor Group 转换为通用 Org
     *
     * @param casdoorGroup Casdoor 组对象
     * @return 通用组织对象
     */
    public com.iflytek.rpa.auth.core.entity.Org toCommonOrg(org.casbin.casdoor.entity.Group casdoorGroup) {
        if (casdoorGroup == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.Org org = new com.iflytek.rpa.auth.core.entity.Org();

        // TODO: id字段需要根据业务逻辑生成，Casdoor的name可能作为唯一标识
        // 暂时使用name作为id，后续可能需要根据实际业务调整
        org.setId(casdoorGroup.name);

        // 基本字段映射
        org.setName(
                casdoorGroup.displayName != null && !casdoorGroup.displayName.isEmpty()
                        ? casdoorGroup.displayName
                        : casdoorGroup.name); // 显示名称映射到机构名称
        org.setCode(casdoorGroup.name); // Casdoor的name作为机构编码

        // 机构类型映射
        org.setOrgType(casdoorGroup.type);

        // 上级机构映射
        org.setHigherOrg(casdoorGroup.parentId);

        // 机构简称：使用title
        org.setShortName(casdoorGroup.title);

        // 状态字段转换：isEnabled (true -> status=1启用, false -> status=0停用)
        org.setStatus(casdoorGroup.isEnabled ? 1 : 0);

        // 日期字段转换
        org.setCreateTime(parseDateTime(casdoorGroup.createdTime));
        org.setUpdateTime(parseDateTime(casdoorGroup.updatedTime));

        // TODO: isTopGroup字段需要根据业务逻辑处理，可能用于判断level或firstLevelId
        // 如果是顶级组，可能需要设置level=1或firstLevelId
        if (casdoorGroup.isTopGroup) {
            org.setLevel(1);
            // TODO: firstLevelId可能需要设置为当前id，需要确认业务逻辑
            org.setFirstLevelId(casdoorGroup.name);
        }

        // 默认值设置
        if (org.getSort() == null) {
            org.setSort(1); // 默认排序为1
        }

        // 逻辑删除字段：Group没有对应字段，默认设置为0（未删除）
        org.setIsDelete(0);

        // 扩展信息：将manager、contactEmail、users、key等信息存储到extInfo
        StringBuilder extInfoBuilder = new StringBuilder();
        if (casdoorGroup.manager != null && !casdoorGroup.manager.isEmpty()) {
            extInfoBuilder.append("manager:").append(casdoorGroup.manager);
        }
        if (casdoorGroup.contactEmail != null && !casdoorGroup.contactEmail.isEmpty()) {
            if (extInfoBuilder.length() > 0) {
                extInfoBuilder.append("|");
            }
            extInfoBuilder.append("contactEmail:").append(casdoorGroup.contactEmail);
        }
        if (casdoorGroup.users != null && !casdoorGroup.users.isEmpty()) {
            if (extInfoBuilder.length() > 0) {
                extInfoBuilder.append("|");
            }
            extInfoBuilder.append("users:").append(String.join(",", casdoorGroup.users));
        }
        if (casdoorGroup.key != null && !casdoorGroup.key.isEmpty()) {
            if (extInfoBuilder.length() > 0) {
                extInfoBuilder.append("|");
            }
            extInfoBuilder.append("key:").append(casdoorGroup.key);
        }
        if (extInfoBuilder.length() > 0) {
            org.setExtInfo(extInfoBuilder.toString());
        }

        // TODO: owner字段需要根据业务逻辑确定，可能代表租户标识
        // 暂时可以存储到thirdExtInfo中
        if (casdoorGroup.owner != null && !casdoorGroup.owner.isEmpty()) {
            org.setThirdExtInfo("owner:" + casdoorGroup.owner);
        }

        // TODO: children字段需要根据业务逻辑处理，可能需要递归处理子组织
        // 这里暂时不处理，需要业务逻辑补充

        // 以下字段在Casdoor Group中没有对应，设置为null或默认值
        // province, provinceCode, city, cityCode, district, districtCode
        // orgTypeName, orgTypeCode
        // higherName, levelCode
        // remark 可以尝试从其他字段映射，如果没有则置空

        return org;
    }

    /**
     * 将通用 Org 转换为 Casdoor Group
     *
     * @param org 通用组织对象
     * @return Casdoor 组对象
     */
    public org.casbin.casdoor.entity.Group toCasdoorGroup(com.iflytek.rpa.auth.core.entity.Org org) {
        if (org == null) {
            return null;
        }

        org.casbin.casdoor.entity.Group casdoorGroup = new org.casbin.casdoor.entity.Group();

        // TODO: name字段需要确认，使用code作为name（机构编码作为Casdoor的name）
        // 如果code为空，可能需要使用id或其他字段，需要根据业务逻辑调整
        if (org.getCode() != null && !org.getCode().isEmpty()) {
            casdoorGroup.name = org.getCode();
        } else {
            // TODO: 如果code为空，使用id作为name，需要确认业务逻辑
            casdoorGroup.name = org.getId() != null ? org.getId() : "";
        }

        // 显示名称映射，如果name为空则使用code
        casdoorGroup.displayName = org.getName() != null && !org.getName().isEmpty()
                ? org.getName()
                : (org.getCode() != null ? org.getCode() : "");

        // 机构类型映射
        casdoorGroup.type = org.getOrgType() != null ? org.getOrgType() : "";

        // 上级机构映射
        casdoorGroup.parentId = org.getHigherOrg();

        // title字段：使用shortName
        casdoorGroup.title = org.getShortName();

        // 状态字段转换：status (1启用 -> isEnabled=true, 0停用 -> isEnabled=false)
        casdoorGroup.isEnabled = org.getStatus() != null && org.getStatus() == 1;

        // 日期字段转换：Date -> String
        casdoorGroup.createdTime = formatDateTime(org.getCreateTime());
        casdoorGroup.updatedTime = formatDateTime(org.getUpdateTime());

        // TODO: isTopGroup字段需要根据业务逻辑判断，可能根据level或firstLevelId判断
        // 如果level=1或firstLevelId等于当前id，可能是顶级组
        casdoorGroup.isTopGroup = (org.getLevel() != null && org.getLevel() == 1)
                || (org.getFirstLevelId() != null && org.getFirstLevelId().equals(org.getId()));

        // TODO: owner字段需要确认业务逻辑，可以从thirdExtInfo中解析
        // 暂时置空，需要根据业务逻辑补充
        casdoorGroup.owner = "";

        // 以下字段在Casdoor Group中需要设置默认值
        casdoorGroup.manager = ""; // TODO: 可以从extInfo中解析manager，需要根据业务逻辑补充
        casdoorGroup.contactEmail = ""; // TODO: 可以从extInfo中解析contactEmail，需要根据业务逻辑补充
        casdoorGroup.users = new ArrayList<>(); // TODO: 可以从extInfo中解析users，需要根据业务逻辑补充
        casdoorGroup.key = ""; // TODO: 可以从extInfo中解析key，需要根据业务逻辑补充
        casdoorGroup.children = new ArrayList<>(); // TODO: 需要根据业务逻辑填充子组织列表

        // 尝试从extInfo中提取manager、contactEmail、users、key等信息
        if (org.getExtInfo() != null && !org.getExtInfo().isEmpty()) {
            String extInfo = org.getExtInfo();
            if (extInfo.contains("manager:")) {
                String managerPart = extInfo.substring(extInfo.indexOf("manager:") + 8);
                if (managerPart.contains("|")) {
                    managerPart = managerPart.substring(0, managerPart.indexOf("|"));
                }
                if (!managerPart.isEmpty()) {
                    casdoorGroup.manager = managerPart;
                }
            }
            if (extInfo.contains("contactEmail:")) {
                String emailPart = extInfo.substring(extInfo.indexOf("contactEmail:") + 13);
                if (emailPart.contains("|")) {
                    emailPart = emailPart.substring(0, emailPart.indexOf("|"));
                }
                if (!emailPart.isEmpty()) {
                    casdoorGroup.contactEmail = emailPart;
                }
            }
            if (extInfo.contains("users:")) {
                String usersPart = extInfo.substring(extInfo.indexOf("users:") + 6);
                if (usersPart.contains("|")) {
                    usersPart = usersPart.substring(0, usersPart.indexOf("|"));
                }
                if (!usersPart.isEmpty()) {
                    casdoorGroup.users = Arrays.asList(usersPart.split(","));
                }
            }
            if (extInfo.contains("key:")) {
                String keyPart = extInfo.substring(extInfo.indexOf("key:") + 4);
                if (keyPart.contains("|")) {
                    keyPart = keyPart.substring(0, keyPart.indexOf("|"));
                }
                if (!keyPart.isEmpty()) {
                    casdoorGroup.key = keyPart;
                }
            }
        }

        // 尝试从thirdExtInfo中解析owner
        if (org.getThirdExtInfo() != null && org.getThirdExtInfo().contains("owner:")) {
            String ownerPart =
                    org.getThirdExtInfo().substring(org.getThirdExtInfo().indexOf("owner:") + 6);
            if (!ownerPart.isEmpty()) {
                casdoorGroup.owner = ownerPart;
            }
        }

        return casdoorGroup;
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
