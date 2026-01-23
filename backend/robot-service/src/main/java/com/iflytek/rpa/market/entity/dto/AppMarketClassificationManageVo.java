package com.iflytek.rpa.market.entity.dto;

import java.io.Serializable;
import lombok.Data;

/**
 * 应用市场分类管理查询响应DTO
 *
 * @author auto-generated
 */
@Data
public class AppMarketClassificationManageVo implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 分类ID
     */
    private Long id;

    /**
     * 分类名
     */
    private String name;

    /**
     * 来源: 0-系统预置, 1-自定义
     */
    private Integer source;

    /**
     * 被引用次数
     */
    private Integer reference;
}
