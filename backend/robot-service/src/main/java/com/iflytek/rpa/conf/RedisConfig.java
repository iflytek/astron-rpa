package com.iflytek.rpa.conf;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.core.StringRedisTemplate;

@Configuration
@RequiredArgsConstructor
public class RedisConfig {

    private final StringRedisTemplate stringRedisTemplate;

    @Bean
    public void getRedisTemplate() {
        stringRedisTemplate.setEnableTransactionSupport(true);
    }
}
