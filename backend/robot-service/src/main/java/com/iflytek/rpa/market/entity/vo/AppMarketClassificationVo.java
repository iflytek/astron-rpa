package com.iflytek.rpa.market.entity.vo;

import java.io.Serializable;
import lombok.Data;

/**
 * 应用市场分类VO
 *
 * @author auto-generated
 */
@Data
public class AppMarketClassificationVo implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 分类ID
     */
    private String id;

    /**
     * 分类名
     */
    private String name;

    private Integer sort;
}
