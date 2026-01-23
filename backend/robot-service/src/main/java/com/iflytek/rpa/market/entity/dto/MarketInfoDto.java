package com.iflytek.rpa.market.entity.dto;

import java.util.List;
import lombok.Data;

/**
 * 市场信息DTO
 * @author mjren
 * @date 2025-01-27
 */
@Data
public class MarketInfoDto {
    /**
     * 市场ID列表
     */
    private List<String> marketIdList;

    /**
     * 编辑权限标识
     */
    private Integer editFlag;

    /**
     * 分类
     */
    private String category;
}
