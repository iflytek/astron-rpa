package com.iflytek.rpa.auth.blacklist.config;

import java.util.ArrayList;
import java.util.List;
import javax.annotation.PostConstruct;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * 黑名单配置类
 * 配置封禁时长阶梯
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "blacklist")
public class BlacklistConfig {

    /**
     * 封禁时长配置（秒）
     * level 1 -> 1小时
     * level 2 -> 1天
     * level 3 -> 7天
     * level 4 -> 30天
     * level 5 -> 365天
     * 超过 level 5 则使用最后一个等级的时长
     */
    private List<Long> durations;

    /**
     * 密码错误次数限制
     */
    private Integer passwordErrorLimit = 5;

    /**
     * 密码错误计数过期时间（秒）
     * 使用封禁配置的第一个等级（1小时），确保与封禁时长配置一致
     */
    private Long passwordErrorExpire;

    /**
     * 敏感数据访问次数限制
     */
    private Integer sensitiveAccessLimit = 1;

    /**
     * 违规操作次数限制
     */
    private Integer violationLimit = 3;

    /**
     * 初始化默认配置
     */
    @PostConstruct
    public void init() {
        if (durations == null || durations.isEmpty()) {
            durations = new ArrayList<>();
            durations.add(3600L); // 1小时
            durations.add(86400L); // 1天
            durations.add(604800L); // 7天
            durations.add(2592000L); // 30天
            durations.add(31536000L); // 365天
        }

        // 密码错误计数过期时间使用封禁配置的第一个等级（1小时）
        if (passwordErrorExpire == null && !durations.isEmpty()) {
            passwordErrorExpire = durations.get(0);
        }
    }

    /**
     * 根据等级获取封禁时长（秒）
     *
     * @param level 封禁等级
     * @return 封禁时长（秒）
     */
    public Long getDurationByLevel(int level) {
        if (level <= 0) {
            return durations.get(0);
        }
        if (level > durations.size()) {
            // 超过最大等级，返回最后一个等级的时长（或可设置为永久封禁）
            return durations.get(durations.size() - 1);
        }
        return durations.get(level - 1);
    }

    /**
     * 获取密码错误 Redis Key
     *
     * @param userId 用户ID
     * @return Redis Key
     */
    public static String getPasswordErrorKey(String userId) {
        return "LOGIN_FAIL:" + userId;
    }

    /**
     * 获取黑名单 Redis Key
     *
     * @param userId 用户ID
     * @return Redis Key
     */
    public static String getBlacklistKey(String userId) {
        return "BL:user:" + userId;
    }
}
