package com.iflytek.rpa.auth.sp.casdoor.mapper;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor User 与通用 User 实体类之间的映射器，仅在casdoor profile下生效
 * @author: Auto Generated
 * @create: 2025/12/11
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorUserMapper {

    private static final String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    private static final String DATE_FORMAT = "yyyy-MM-dd";
    private static final String ISO_DATE_TIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";
    private static final SimpleDateFormat DATE_TIME_FORMATTER = new SimpleDateFormat(DATE_TIME_FORMAT);
    private static final SimpleDateFormat DATE_FORMATTER = new SimpleDateFormat(DATE_FORMAT);
    private static final SimpleDateFormat ISO_DATE_TIME_FORMATTER = new SimpleDateFormat(ISO_DATE_TIME_FORMAT);

    /**
     * 将 Casdoor User 转换为通用 User
     *
     * @param casdoorUser Casdoor 用户对象
     * @return 通用用户对象
     */
    public com.iflytek.rpa.auth.core.entity.User toCommonUser(org.casbin.casdoor.entity.User casdoorUser) {
        if (casdoorUser == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.User user = new com.iflytek.rpa.auth.core.entity.User();

        // 基本字段映射
        user.setId(casdoorUser.id);
        user.setLoginName(casdoorUser.name); // Casdoor的name是登录名
        user.setName(casdoorUser.displayName); // 显示名称映射到用户姓名
        user.setEmail(casdoorUser.email);
        user.setPhone(casdoorUser.phone != null ? casdoorUser.phone : "");

        // 头像映射：优先使用permanentAvatar，其次使用avatar
        if (casdoorUser.permanentAvatar != null && !casdoorUser.permanentAvatar.isEmpty()) {
            user.setProfile(casdoorUser.permanentAvatar);
        } else if (casdoorUser.avatar != null && !casdoorUser.avatar.isEmpty()) {
            user.setProfile(casdoorUser.avatar);
        }

        // 日期字段转换
        user.setBirthday(parseDate(casdoorUser.birthday));
        user.setCreateTime(parseDateTime(casdoorUser.createdTime));
        user.setUpdateTime(parseDateTime(casdoorUser.updatedTime));

        // 身份证号
        user.setIdNumber(casdoorUser.idCard);

        // 逻辑删除字段转换：boolean -> Integer (true -> 1, false -> 0)
        user.setIsDelete(casdoorUser.isDeleted ? 1 : 0);

        // 状态字段转换：isForbidden (true -> status=0停用, false -> status=1启用)
        user.setStatus(casdoorUser.isForbidden ? 0 : 1);

        // 地址字段转换：String[] -> String
        if (casdoorUser.address != null && casdoorUser.address.length > 0) {
            user.setAddress(String.join(", ", casdoorUser.address));
        } else if (casdoorUser.location != null && !casdoorUser.location.isEmpty()) {
            user.setAddress(casdoorUser.location);
        }

        // todo 机构相关字段 这里的机构对应的是casdoor的group name，需要调api查询
        user.setOrgId("group");
        user.setOrgCode("group");

        // 备注字段
        if (casdoorUser.bio != null && !casdoorUser.bio.isEmpty()) {
            user.setRemark(casdoorUser.bio);
        }

        // 租户字段：extInfo
        user.setExtInfo(casdoorUser.owner);

        // 扩展信息：从properties中提取
        if (casdoorUser.properties != null && !casdoorUser.properties.isEmpty()) {
            // 可以将properties序列化为JSON字符串存储到thirdExtInfo
            // 这里简化处理，只提取部分关键信息
            String thirdExtInfo = casdoorUser.properties.toString();
            user.setThirdExtInfo(thirdExtInfo);
        }

        // 默认值设置
        if (user.getUserSource() == null) {
            user.setUserSource(1); // 默认用户来源为1
        }

        return user;
    }

    /**
     * 将通用 User 转换为 Casdoor User
     *
     * @param user 通用用户对象
     * @return Casdoor 用户对象
     */
    public org.casbin.casdoor.entity.User toCasdoorUser(com.iflytek.rpa.auth.core.entity.User user) {
        if (user == null) {
            return null;
        }

        org.casbin.casdoor.entity.User casdoorUser = new org.casbin.casdoor.entity.User();

        // 基本字段映射
        casdoorUser.id = user.getId();
        casdoorUser.name = user.getLoginName(); // 登录名映射到Casdoor的name
        casdoorUser.displayName = user.getName(); // 用户姓名映射到显示名称
        casdoorUser.email = user.getEmail();
        casdoorUser.phone = user.getPhone() != null ? user.getPhone() : "";

        // 头像映射
        if (user.getProfile() != null && !user.getProfile().isEmpty()) {
            casdoorUser.avatar = user.getProfile();
            casdoorUser.permanentAvatar = user.getProfile();
        }

        // 日期字段转换：Date -> String
        casdoorUser.birthday = formatDate(user.getBirthday());
        casdoorUser.createdTime = formatDateTime(user.getCreateTime());
        casdoorUser.updatedTime = formatDateTime(user.getUpdateTime());

        // 身份证号
        casdoorUser.idCard = user.getIdNumber();

        // 逻辑删除字段转换：Integer -> boolean (1 -> true, 0 -> false)
        casdoorUser.isDeleted = user.getIsDelete() != null && user.getIsDelete() == 1;

        // 状态字段转换：status (0停用 -> isForbidden=true, 1启用 -> isForbidden=false)
        casdoorUser.isForbidden = user.getStatus() != null && user.getStatus() == 0;

        // 地址字段转换：String -> String[]
        if (user.getAddress() != null && !user.getAddress().isEmpty()) {
            // 如果包含逗号，按逗号分割；否则作为单个元素
            if (user.getAddress().contains(",")) {
                casdoorUser.address = Arrays.stream(user.getAddress().split(","))
                        .map(String::trim)
                        .filter(s -> !s.isEmpty())
                        .toArray(String[]::new);
            } else {
                casdoorUser.address = new String[] {user.getAddress()};
            }
            casdoorUser.location = user.getAddress();
        }

        // 租户
        casdoorUser.owner = user.getExtInfo();

        // todo 机构（群组）映射
        casdoorUser.region = user.getOrgId();
        casdoorUser.region = user.getOrgCode();

        // 备注字段
        if (user.getRemark() != null && !user.getRemark().isEmpty()) {
            casdoorUser.bio = user.getRemark();
        }

        // 扩展信息：存储到properties中
        // 这里简化处理，如果需要更复杂的映射，可以进一步实现
        if (user.getExtInfo() != null && !user.getExtInfo().isEmpty()) {
            // properties是Map类型，这里可以根据实际需求进行解析
            // 暂时留空，需要时再实现
        }

        // 设置默认值
        casdoorUser.password = "";
        casdoorUser.passwordSalt = "";
        casdoorUser.firstName = "";
        casdoorUser.lastName = "";
        casdoorUser.affiliation = "";
        casdoorUser.title = "";
        casdoorUser.idCardType = "";
        casdoorUser.homepage = "";
        casdoorUser.tag = "";
        casdoorUser.language = "";
        casdoorUser.gender = "";
        casdoorUser.education = "";
        casdoorUser.score = 0;
        casdoorUser.karma = 0;
        casdoorUser.ranking = 0;
        casdoorUser.isDefaultAvatar = false;
        casdoorUser.isOnline = false;
        casdoorUser.isAdmin = false;
        casdoorUser.isGlobalAdmin = false;
        casdoorUser.hash = "";
        casdoorUser.preHash = "";
        casdoorUser.createdIp = "";
        casdoorUser.lastSigninTime = "";
        casdoorUser.lastSigninIp = "";

        // 第三方登录相关字段置空
        casdoorUser.github = "";
        casdoorUser.google = "";
        casdoorUser.qq = "";
        casdoorUser.wechat = "";
        casdoorUser.facebook = "";
        casdoorUser.dingtalk = "";
        casdoorUser.weibo = "";
        casdoorUser.gitee = "";
        casdoorUser.linkedin = "";
        casdoorUser.wecom = "";
        casdoorUser.lark = "";
        casdoorUser.gitlab = "";
        casdoorUser.adfs = "";
        casdoorUser.baidu = "";
        casdoorUser.alipay = "";
        casdoorUser.casdoor = "";
        casdoorUser.infoflow = "";
        casdoorUser.apple = "";
        casdoorUser.azuread = "";
        casdoorUser.slack = "";
        casdoorUser.steam = "";
        casdoorUser.bilibili = "";
        casdoorUser.okta = "";
        casdoorUser.douyin = "";
        casdoorUser.custom = "";
        casdoorUser.ldap = "";
        // 其他字段
        casdoorUser.type = "normal-user";
        return casdoorUser;
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
            // 尝试日期格式 (yyyy-MM-dd)
            if (dateTimeStr.length() >= DATE_FORMAT.length()) {
                String dStr = dateTimeStr.substring(0, DATE_FORMAT.length());
                synchronized (DATE_FORMATTER) {
                    return DATE_FORMATTER.parse(dStr);
                }
            }
        } catch (ParseException e) {
            // 解析失败，返回null
        }
        return null;
    }

    /**
     * 解析日期字符串为Date对象
     *
     * @param dateStr 日期字符串
     * @return Date对象，解析失败返回null
     */
    private Date parseDate(String dateStr) {
        if (dateStr == null || dateStr.isEmpty()) {
            return null;
        }
        try {
            synchronized (DATE_FORMATTER) {
                return DATE_FORMATTER.parse(dateStr);
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

    /**
     * 格式化Date对象为日期字符串
     *
     * @param date Date对象
     * @return 日期字符串，date为null返回空字符串
     */
    private String formatDate(Date date) {
        if (date == null) {
            return "";
        }
        synchronized (DATE_FORMATTER) {
            return DATE_FORMATTER.format(date);
        }
    }
}
