package com.iflytek.rpa.auth.utils;

import java.util.Set;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class RedisUtil {
    public static void deleteRedisKeysByPrefix(String prefix) {
        try {
            Set<String> keys = RedisUtils.redisTemplate.keys(prefix + "*");
            if (!keys.isEmpty()) {
                RedisUtils.redisTemplate.delete(keys);
                log.info("成功删除{}个以'{}'为前缀的Redis键", keys.size(), prefix);
            } else {
                log.info("未找到以'{}'为前缀的Redis键", prefix);
            }
        } catch (Exception e) {
            log.error("删除Redis前缀键失败: {}", e.getMessage(), e);
        }
    }
}
