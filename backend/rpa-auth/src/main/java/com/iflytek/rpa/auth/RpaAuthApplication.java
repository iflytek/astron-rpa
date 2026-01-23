package com.iflytek.rpa.auth;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.session.data.redis.config.annotation.web.http.EnableRedisHttpSession;

@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
@EnableScheduling
@EnableRedisHttpSession(redisNamespace = "uap:session", maxInactiveIntervalInSeconds = 604800)
public class RpaAuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(RpaAuthApplication.class, args);
    }
}
