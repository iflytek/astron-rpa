package com.iflytek.rpa.base.entity.dto;

import com.alibaba.fastjson.annotation.JSONField;
import java.io.Serializable;
import java.util.List;
import lombok.Data;

/**
 * 资源配置DTO
 * 用于JSON序列化和反序列化
 * 存储时保存type、base、final字段
 * 使用时从版本默认配置中补充urls、parent等完整信息
 */
@Data
public class ResourceConfigDto implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 资源类型：QUOTA（配额）或 SWITCH（开关）
     */
    @JSONField(name = "type")
    private String type;

    /**
     * 基础值（版本默认值）
     */
    @JSONField(name = "base")
    private Integer base;

    /**
     * 最终值（直接存储，不计算差值）
     */
    @JSONField(name = "final")
    private Integer finalValue;

    /**
     * URL路由模式列表（从版本默认配置中获取，不存储在数据库extraConfigJson中，但需要存储在Redis缓存中）
     */
    @JSONField(serialize = true, deserialize = true)
    private List<String> urls;

    /**
     * 父级资源代码（从版本默认配置中获取，不存储在数据库extraConfigJson中，但需要存储在Redis缓存中）
     */
    @JSONField(serialize = true, deserialize = true)
    private String parent;
}
