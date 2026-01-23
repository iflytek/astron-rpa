package com.iflytek.rpa.auth.conf;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;
import com.iflytek.rpa.auth.utils.RedisUtils;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.Jackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

/**
 * Redis配置类
 * 用于配置RedisTemplate并注入到RedisUtils
 */
@Configuration
public class RedisConfig {

    /**
     * 创建RedisTemplate Bean
     * 并在创建后立即设置到RedisUtils的静态字段
     *
     * @param factory Redis连接工厂，Spring会自动注入
     * @return 配置好的RedisTemplate实例
     */
    @Bean(name = "rpaRedisTemplate")
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        // 配置连接工厂
        template.setConnectionFactory(factory);

        // 使用Jackson2JsonRedisSerializer来序列化和反序列化redis的value值
        Jackson2JsonRedisSerializer<Object> jackson2JsonRedisSerializer =
                new Jackson2JsonRedisSerializer<>(Object.class);
        ObjectMapper om = new ObjectMapper();
        // 指定要序列化的域，field,get和set,以及修饰符范围，ANY是都有包括private和public
        om.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        // 指定序列化输入的类型，类必须是非final修饰的，final修饰的类，比如String,Integer等会抛出异常
        // 使用新版本API（Jackson 2.10+），旧版本的enableDefaultTyping已废弃且存在安全风险
        om.activateDefaultTyping(LaissezFaireSubTypeValidator.instance, ObjectMapper.DefaultTyping.NON_FINAL);
        jackson2JsonRedisSerializer.setObjectMapper(om);

        // 使用StringRedisSerializer来序列化和反序列化redis的key值
        StringRedisSerializer stringRedisSerializer = new StringRedisSerializer();
        template.setKeySerializer(stringRedisSerializer);
        // 值采用json序列化
        template.setValueSerializer(jackson2JsonRedisSerializer);
        // 设置hash key 和value序列化模式
        template.setHashKeySerializer(stringRedisSerializer);
        template.setHashValueSerializer(jackson2JsonRedisSerializer);

        // 开启事务支持（如果需要Redis事务功能，取消注释下面这行）
        // template.setEnableTransactionSupport(true);

        template.afterPropertiesSet();

        // 将RedisTemplate设置到RedisUtils的静态字段
        RedisUtils.redisTemplate = template;

        return template;
    }

    /**
     * 创建UAP兼容的RedisTemplate Bean
     * 使用与UAP相同的JDK序列化方式，用于存储UAP的token
     *
     * @param factory Redis连接工厂，Spring会自动注入
     * @return 配置好的UAP兼容RedisTemplate实例
     */
    @Bean(name = "uapCompatibleRedisTemplate")
    public RedisTemplate<String, Object> uapCompatibleRedisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        // 配置连接工厂
        template.setConnectionFactory(factory);

        // 使用StringRedisSerializer来序列化key（与UAP一致）
        StringRedisSerializer stringRedisSerializer = new StringRedisSerializer();

        // 使用JdkSerializationRedisSerializer来序列化value（与UAP一致）
        org.springframework.data.redis.serializer.JdkSerializationRedisSerializer jdkSerializer =
                new org.springframework.data.redis.serializer.JdkSerializationRedisSerializer();

        template.setKeySerializer(stringRedisSerializer);
        template.setValueSerializer(jdkSerializer);
        template.setHashKeySerializer(stringRedisSerializer);
        template.setHashValueSerializer(jdkSerializer);

        template.afterPropertiesSet();

        return template;
    }
}
