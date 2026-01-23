package com.iflytek.rpa.utils;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.util.CollectionUtils;

public class RedisUtils {
    public static RedisTemplate<String, Object> redisTemplate;

    /**
     * 指定缓存失效时间
     *
     * @param key  键
     * @param time 时间(秒)
     * @return
     */
    public static boolean expire(String key, long time) {
        try {
            if (time > 0) {
                redisTemplate.expire(key, time, TimeUnit.SECONDS);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 根据key 获取过期时间
     *
     * @param key 键 不能为null
     * @return 时间(秒) 返回0代表为永久有效
     */
    public static long getExpire(String key) {
        return redisTemplate.getExpire(key, TimeUnit.SECONDS);
    }

    /**
     * 判断key是否存在
     *
     * @param key 键
     * @return true 存在 false不存在
     */
    public static boolean hasKey(String key) {
        try {
            return redisTemplate.hasKey(key);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 删除缓存
     *
     * @param key 可以传一个值 或多个
     */
    @SuppressWarnings("unchecked")
    public static void del(String... key) {
        if (key != null && key.length > 0) {
            if (key.length == 1) {
                redisTemplate.delete(key[0]);
            } else {
                redisTemplate.delete(CollectionUtils.arrayToList(key));
            }
        }
    }

    // ============================String=============================

    /**
     * 普通缓存获取
     *
     * @param key 键
     * @return 值
     */
    public static Object get(String key) {
        return key == null ? null : redisTemplate.opsForValue().get(key);
    }

    /**
     * 普通缓存放入
     *
     * @param key   键
     * @param value 值
     * @return true成功 false失败
     */
    public static boolean set(String key, Object value) {
        try {
            redisTemplate.opsForValue().set(key, value);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 普通缓存放入并设置时间
     *
     * @param key   键
     * @param value 值
     * @param time  时间(秒) time要大于0 如果time小于等于0 将设置无限期
     * @return true成功 false 失败
     */
    public static boolean set(String key, Object value, long time) {
        try {
            if (time > 0) {
                redisTemplate.opsForValue().set(key, value, time, TimeUnit.SECONDS);
            } else {
                set(key, value);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 递增
     *
     * @param key   键
     * @param delta 要增加几(大于0)
     * @return
     */
    public static long incr(String key, long delta) {
        if (delta < 0) {
            throw new RuntimeException("递增因子必须大于0");
        }
        return redisTemplate.opsForValue().increment(key, delta);
    }

    /**
     * 尝试获取分布式锁（非重入），使用 SET NX PX/EX 语义
     * @param key     锁键
     * @param value   请求标识，避免误删（如 UUID）
     * @param timeout 超时时间
     * @param unit    时间单位
     * @return true 获取成功；false 获取失败
     */
    public static boolean tryLock(String key, String value, long timeout, TimeUnit unit) {
        try {
            Boolean ok = redisTemplate.opsForValue().setIfAbsent(key, value, timeout, unit);
            return Boolean.TRUE.equals(ok);
        } catch (Exception e) {
            LoggerUtils.error("redis加锁异常", e);
            return false;
        }
    }

    /**
     * 释放分布式锁，仅删除持有者自己的锁
     * @param key   锁键
     * @param value 请求标识
     */
    public static void unlock(String key, String value) {
        try {
            Object cached = redisTemplate.opsForValue().get(key);
            if (Objects.equals(cached, value)) {
                redisTemplate.delete(key);
            }
        } catch (Exception e) {
            LoggerUtils.error("redis解锁异常", e);
        }
    }

    /**
     * 递减
     *
     * @param key   键
     * @param delta 要减少几(小于0)
     * @return
     */
    public static long decr(String key, long delta) {
        if (delta < 0) {
            throw new RuntimeException("递减因子必须大于0");
        }
        return redisTemplate.opsForValue().increment(key, -delta);
    }

    // ================================Map=================================

    /**
     * HashGet
     *
     * @param key  键 不能为null
     * @param item 项 不能为null
     * @return 值
     */
    public static Object hget(String key, String item) {
        return redisTemplate.opsForHash().get(key, item);
    }

    /**
     * 获取hashKey对应的所有键值
     *
     * @param key 键
     * @return 对应的多个键值
     */
    public static Map<Object, Object> hmget(String key) {
        return redisTemplate.opsForHash().entries(key);
    }

    /**
     * HashSet
     *
     * @param key 键
     * @param map 对应多个键值
     * @return true 成功 false 失败
     */
    public static boolean hmset(String key, Map<String, Object> map) {
        try {
            redisTemplate.opsForHash().putAll(key, map);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * HashSet 并设置时间
     *
     * @param key  键
     * @param map  对应多个键值
     * @param time 时间(秒)
     * @return true成功 false失败
     */
    public static boolean hmset(String key, Map<String, Object> map, long time) {
        try {
            redisTemplate.opsForHash().putAll(key, map);
            if (time > 0) {
                expire(key, time);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 向一张hash表中放入数据,如果不存在将创建
     *
     * @param key   键
     * @param item  项
     * @param value 值
     * @return true 成功 false失败
     */
    public static boolean hset(String key, String item, Object value) {
        try {
            redisTemplate.opsForHash().put(key, item, value);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 向一张hash表中放入数据,如果不存在将创建
     *
     * @param key   键
     * @param item  项
     * @param value 值
     * @param time  时间(秒)  注意:如果已存在的hash表有时间,这里将会替换原有的时间
     * @return true 成功 false失败
     */
    public static boolean hset(String key, String item, Object value, long time) {
        try {
            redisTemplate.opsForHash().put(key, item, value);
            if (time > 0) {
                expire(key, time);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 删除hash表中的值
     *
     * @param key  键 不能为null
     * @param item 项 可以使多个 不能为null
     */
    public static void hdel(String key, Object... item) {
        redisTemplate.opsForHash().delete(key, item);
    }

    /**
     * 判断hash表中是否有该项的值
     *
     * @param key  键 不能为null
     * @param item 项 不能为null
     * @return true 存在 false不存在
     */
    public static boolean hHasKey(String key, String item) {
        return redisTemplate.opsForHash().hasKey(key, item);
    }

    /**
     * hash递增 如果不存在,就会创建一个 并把新增后的值返回
     *
     * @param key  键
     * @param item 项
     * @param by   要增加几(大于0)
     * @return
     */
    public static double hincr(String key, String item, double by) {
        return redisTemplate.opsForHash().increment(key, item, by);
    }

    /**
     * hash递减
     *
     * @param key  键
     * @param item 项
     * @param by   要减少记(小于0)
     * @return
     */
    public static double hdecr(String key, String item, double by) {
        return redisTemplate.opsForHash().increment(key, item, -by);
    }

    // ============================set=============================

    /**
     * 根据key获取Set中的所有值
     *
     * @param key 键
     */
    public static Set<Object> sGet(String key) {
        try {
            return redisTemplate.opsForSet().members(key);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 根据value从一个set中查询,是否存在
     *
     * @param key   键
     * @param value 值
     * @return true 存在 false不存在
     */
    public static boolean sHasKey(String key, Object value) {
        try {
            return redisTemplate.opsForSet().isMember(key, value);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 将数据放入set缓存
     *
     * @param key    键
     * @param values 值 可以是多个
     * @return 成功个数
     */
    public static long sSet(String key, Object... values) {
        try {
            return redisTemplate.opsForSet().add(key, values);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }

    /**
     * 将set数据放入缓存
     *
     * @param key    键
     * @param time   时间(秒)
     * @param values 值 可以是多个
     * @return 成功个数
     */
    public static long sSetAndTime(String key, long time, Object... values) {
        try {
            Long count = redisTemplate.opsForSet().add(key, values);
            if (time > 0) {
                expire(key, time);
            }
            return count;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }

    /**
     * 获取set缓存的长度
     *
     * @param key 键
     * @return
     */
    public static long sGetSetSize(String key) {
        try {
            return redisTemplate.opsForSet().size(key);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }

    /**
     * 移除值为value的
     *
     * @param key    键
     * @param values 值 可以是多个
     * @return 移除的个数
     */
    public static long setRemove(String key, Object... values) {
        try {
            Long count = redisTemplate.opsForSet().remove(key, values);
            return count;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }
    // ===============================list=================================

    /**
     * 获取list缓存的内容
     *
     * @param key   键
     * @param start 开始
     * @param end   结束  0 到 -1代表所有值
     * @return
     */
    public static List<Object> lGet(String key, long start, long end) {
        try {
            return redisTemplate.opsForList().range(key, start, end);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 获取list缓存的长度
     *
     * @param key 键
     * @return
     */
    public static long lGetListSize(String key) {
        try {
            return redisTemplate.opsForList().size(key);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }

    /**
     * 将list放入缓存
     *
     * @param key   键
     * @param value 值
     * @return
     */
    public static boolean lSet(String key, Object value) {
        try {
            redisTemplate.opsForList().rightPush(key, value);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 将list放入缓存
     *
     * @param key   键
     * @param value 值
     * @param time  时间(秒)
     * @return
     */
    public static boolean lSet(String key, Object value, long time) {
        try {
            redisTemplate.opsForList().rightPush(key, value);
            if (time > 0) {
                expire(key, time);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 将list放入缓存
     *
     * @param key   键
     * @param value 值
     * @return
     */
    public static boolean lSet(String key, List<Object> value) {
        try {
            redisTemplate.opsForList().rightPushAll(key, value);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 将list放入缓存
     *
     * @param key   键
     * @param value 值
     * @param time  时间(秒)
     * @return
     */
    public static boolean lSet(String key, List<Object> value, long time) {
        try {
            redisTemplate.opsForList().rightPushAll(key, value);
            if (time > 0) {
                expire(key, time);
            }
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 根据索引修改list中的某条数据
     *
     * @param key   键
     * @param index 索引
     * @param value 值
     * @return
     */
    public static boolean lUpdateIndex(String key, long index, Object value) {
        try {
            redisTemplate.opsForList().set(key, index, value);
            return true;
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    /**
     * 移除N个值为value
     *
     * @param key   键
     * @param count 移除多少个
     * @param value 值
     * @return 移除的个数
     */
    public static long lRemove(String key, long count, Object value) {
        try {
            return redisTemplate.opsForList().remove(key, count, value);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return 0;
        }
    }

    /**
     * 向有序集合添加一个或多个成员，或者更新已存在成员的分数
     *
     * @param key   键
     * @param value 值
     * @param score 分数
     */
    public static Boolean zAdd(String key, Object value, double score) {
        try {
            return redisTemplate.opsForZSet().add(key, value, score);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return false;
        }
    }

    // ===============================ZSet=================================

    /**
     * 获取有序集合的成员数
     *
     * @param key 键
     */
    public static Long zCard(String key) {
        try {
            return redisTemplate.opsForZSet().size(key);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 计算在有序集合中指定区间分数的成员数
     *
     * @param key 键
     * @param min 最小分数
     * @param max 最大分数
     */
    public static Long zCount(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().count(key, min, max);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 有序集合中对指定成员的分数加上增量
     *
     * @param key   键
     * @param value 值
     * @param delta 增量
     */
    public static Double zIncrementScore(String key, Object value, double delta) {
        try {
            return redisTemplate.opsForZSet().incrementScore(key, value, delta);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 通过索引区间返回有序集合指定区间内的成员(从小到大)
     *
     * @param key   键
     * @param start 开始索引
     * @param end   结束索引
     */
    public static Set<Object> zRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().range(key, start, end);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 通过分数返回有序集合指定区间内的成员(从小到大)
     *
     * @param key 键
     * @param min 最小分数
     * @param max 最大分数
     */
    public static Set<Object> zRangeByScore(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().rangeByScore(key, min, max);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 返回有序集合中指定成员的索引(从小到大)
     *
     * @param key   键
     * @param value 值
     */
    public static Long zRank(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().rank(key, value);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 移除有序集合中的一个或多个成员
     *
     * @param key    键
     * @param values 值
     */
    public static Long zRemove(String key, Object... values) {
        try {
            return redisTemplate.opsForZSet().remove(key, values);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 移除有序集合中给定的排名区间的所有成员
     *
     * @param key   键
     * @param start 开始索引
     * @param end   结束索引
     */
    public static Long zRemoveRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().removeRange(key, start, end);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 移除有序集合中给定的分数区间的所有成员
     *
     * @param key 键
     * @param min 最小分数
     * @param max 最大分数
     */
    public static Long zRemoveRangeByScore(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().removeRangeByScore(key, min, max);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 通过索引区间返回有序集合指定区间内的成员(从大到小)
     *
     * @param key   键
     * @param start 开始索引
     * @param end   结束索引
     */
    public static Set<Object> zReverseRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().reverseRange(key, start, end);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 返回有序集合中指定成员的索引(从大到小)
     *
     * @param key   键
     * @param value 值
     */
    public static Long zReverseRank(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().reverseRank(key, value);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 返回有序集中，成员的分数值
     *
     * @param key   键
     * @param value 值
     */
    public static Double zScore(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().score(key, value);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 计算给定的一个或多个有序集的并集，并存储在新的有序集合中
     *
     * @param key      新集合键
     * @param otherKey 其他集合键
     * @param destKey  目标集合键
     */
    public static Long zUnionAndStore(String key, String otherKey, String destKey) {
        try {
            return redisTemplate.opsForZSet().unionAndStore(key, otherKey, destKey);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 计算给定的一个或多个有序集的交集，并存储在新的有序集合中
     *
     * @param key      新集合键
     * @param otherKey 其他集合键
     * @param destKey  目标集合键
     */
    public static Long zIntersectAndStore(String key, String otherKey, String destKey) {
        try {
            return redisTemplate.opsForZSet().intersectAndStore(key, otherKey, destKey);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }

    /**
     * 通过索引 获取list中的值
     *
     * @param key   键
     * @param index 索引  index>=0时， 0 表头，1 第二个元素，依次类推；index<0时，-1，表尾，-2倒数第二个元素，依次类推
     * @return
     */
    public Object lGetIndex(String key, long index) {
        try {
            return redisTemplate.opsForList().index(key, index);
        } catch (Exception e) {
            LoggerUtils.error("redis操作异常", e);
            return null;
        }
    }
}
