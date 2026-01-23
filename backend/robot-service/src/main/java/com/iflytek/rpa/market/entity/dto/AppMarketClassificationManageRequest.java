package com.iflytek.rpa.market.entity.dto;

import java.io.Serializable;
import lombok.Data;

/**
 * 应用市场分类管理查询请求DTO
 *
 * @author auto-generated
 */
@Data
public class AppMarketClassificationManageRequest implements Serializable {
    /**
     * 分类名
     */
    private String name;

    /**
     * 来源: 0-系统预置, 1-自定义
     */
    private Integer source;
}
