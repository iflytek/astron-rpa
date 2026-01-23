package com.iflytek.rpa.auth.sp.casdoor.mapper;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor Organization 与通用 Tenant 实体类之间的映射器，仅在casdoor profile下生效
 * 注意：Casdoor的Organization对应通用的Tenant
 * @author: Auto Generated
 * @create: 2025/12/11
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorTenantMapper {

    private static final String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    private static final String ISO_DATE_TIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";
    private static final SimpleDateFormat DATE_TIME_FORMATTER = new SimpleDateFormat(DATE_TIME_FORMAT);
    private static final SimpleDateFormat ISO_DATE_TIME_FORMATTER = new SimpleDateFormat(ISO_DATE_TIME_FORMAT);

    /**
     * 将 Casdoor Organization 转换为通用 Tenant
     *
     * @param casdoorOrg Casdoor 组织对象
     * @return 通用租户对象
     */
    public com.iflytek.rpa.auth.core.entity.Tenant toCommonTenant(org.casbin.casdoor.entity.Organization casdoorOrg) {
        if (casdoorOrg == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.Tenant tenant = new com.iflytek.rpa.auth.core.entity.Tenant();

        // TODO: id字段需要根据业务逻辑生成，Casdoor的name可能作为唯一标识
        // 暂时使用name作为id，后续可能需要根据实际业务调整
        tenant.setId(casdoorOrg.name);

        // 基本字段映射
        tenant.setName(
                casdoorOrg.displayName != null && !casdoorOrg.displayName.isEmpty()
                        ? casdoorOrg.displayName
                        : casdoorOrg.name); // 显示名称映射到租户名称
        tenant.setTenantCode(casdoorOrg.name); // Casdoor的name作为租户编码

        // 逻辑删除字段默认0
        tenant.setIsDelete(0);

        // 日期字段转换
        tenant.setCreateTime(parseDateTime(casdoorOrg.createdTime));
        // updateTime在Casdoor Organization中没有对应字段，设置为null或与createTime相同
        tenant.setUpdateTime(parseDateTime(casdoorOrg.createdTime));

        // 默认值设置
        if (tenant.getStatus() == null) {
            tenant.setStatus(1); // 默认启用状态
        }
        if (tenant.getIsDefaultTenant() == null) {
            tenant.setIsDefaultTenant(false); // 默认不是默认租户
        }

        // TODO: owner字段需要根据业务逻辑确定，可能代表租户所有者或标识
        // 暂时可以存储到remark中，或者需要根据业务逻辑补充
        if (casdoorOrg.owner != null && !casdoorOrg.owner.isEmpty()) {
            // 可以将owner信息存储到remark中
            tenant.setRemark("owner:" + casdoorOrg.owner);
        }

        // TODO: 以下字段在Casdoor Organization中没有直接对应，需要根据业务逻辑补充
        // creator字段暂时置空，需要根据业务逻辑补充
        // tenantType字段暂时置空，需要根据业务逻辑补充
        // websiteUrl, tags, languages等字段可以存储到remark中
        if (casdoorOrg.websiteUrl != null && !casdoorOrg.websiteUrl.isEmpty()) {
            String remark = tenant.getRemark();
            if (remark != null && !remark.isEmpty()) {
                tenant.setRemark(remark + "|websiteUrl:" + casdoorOrg.websiteUrl);
            } else {
                tenant.setRemark("websiteUrl:" + casdoorOrg.websiteUrl);
            }
        }

        // 如果tags不为空，可以存储到remark中
        if (casdoorOrg.tags != null && casdoorOrg.tags.length > 0) {
            String tagsStr = String.join(",", casdoorOrg.tags);
            String remark = tenant.getRemark();
            if (remark != null && !remark.isEmpty()) {
                tenant.setRemark(remark + "|tags:" + tagsStr);
            } else {
                tenant.setRemark("tags:" + tagsStr);
            }
        }

        return tenant;
    }

    /**
     * 将通用 Tenant 转换为 Casdoor Organization
     *
     * @param tenant 通用租户对象
     * @return Casdoor 组织对象
     */
    public org.casbin.casdoor.entity.Organization toCasdoorOrganization(
            com.iflytek.rpa.auth.core.entity.Tenant tenant) {
        if (tenant == null) {
            return null;
        }

        org.casbin.casdoor.entity.Organization casdoorOrg = new org.casbin.casdoor.entity.Organization();

        // TODO: name字段需要确认，使用tenantCode作为name（租户编码作为Casdoor的name）
        // 如果tenantCode为空，可能需要使用id或其他字段，需要根据业务逻辑调整
        if (tenant.getTenantCode() != null && !tenant.getTenantCode().isEmpty()) {
            casdoorOrg.name = tenant.getTenantCode();
        } else {
            // TODO: 如果tenantCode为空，使用id作为name，需要确认业务逻辑
            casdoorOrg.name = tenant.getId() != null ? tenant.getId() : "";
        }

        // 显示名称映射，如果name为空则使用tenantCode
        casdoorOrg.displayName = tenant.getName() != null && !tenant.getName().isEmpty()
                ? tenant.getName()
                : (tenant.getTenantCode() != null ? tenant.getTenantCode() : "");

        // 逻辑删除字段默认false
        casdoorOrg.enableSoftDeletion = false;

        // 日期字段转换：Date -> String
        casdoorOrg.createdTime = formatDateTime(tenant.getCreateTime());
        // Casdoor Organization没有updatedTime字段，只使用createdTime

        // TODO: owner字段需要确认业务逻辑，可以从remark中解析
        // 暂时置空，需要根据业务逻辑补充
        casdoorOrg.owner = "";

        // 以下字段在Casdoor Organization中需要设置默认值
        casdoorOrg.websiteUrl = ""; // TODO: 可以从remark中解析websiteUrl，需要根据业务逻辑补充
        casdoorOrg.favicon = "";
        casdoorOrg.passwordType = ""; // TODO: 需要根据业务逻辑设置密码类型
        casdoorOrg.passwordSalt = "";
        casdoorOrg.passwordOptions = new String[0];
        casdoorOrg.countryCodes = new String[0];
        casdoorOrg.defaultAvatar = "";
        casdoorOrg.defaultApplication = ""; // TODO: 需要根据业务逻辑设置默认应用
        casdoorOrg.tags = new String[0]; // TODO: 可以从remark中解析tags，需要根据业务逻辑补充
        casdoorOrg.languages = new String[0];
        casdoorOrg.themeData = null;
        casdoorOrg.masterPassword = "";
        casdoorOrg.initScore = 0;
        casdoorOrg.isProfilePublic = false;
        casdoorOrg.mfaItems = null;
        casdoorOrg.accountItems = null;

        // 尝试从remark中提取owner、websiteUrl和tags
        if (tenant.getRemark() != null && !tenant.getRemark().isEmpty()) {
            String remark = tenant.getRemark();
            if (remark.contains("owner:")) {
                String ownerPart = remark.substring(remark.indexOf("owner:") + 6);
                if (ownerPart.contains("|")) {
                    ownerPart = ownerPart.substring(0, ownerPart.indexOf("|"));
                }
                if (!ownerPart.isEmpty()) {
                    casdoorOrg.owner = ownerPart;
                }
            }
            if (remark.contains("websiteUrl:")) {
                String urlPart = remark.substring(remark.indexOf("websiteUrl:") + 11);
                if (urlPart.contains("|")) {
                    urlPart = urlPart.substring(0, urlPart.indexOf("|"));
                }
                if (!urlPart.isEmpty()) {
                    casdoorOrg.websiteUrl = urlPart;
                }
            }
            if (remark.contains("tags:")) {
                String tagsPart = remark.substring(remark.indexOf("tags:") + 5);
                if (tagsPart.contains("|")) {
                    tagsPart = tagsPart.substring(0, tagsPart.indexOf("|"));
                }
                if (!tagsPart.isEmpty()) {
                    casdoorOrg.tags = tagsPart.split(",");
                }
            }
        }

        return casdoorOrg;
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
