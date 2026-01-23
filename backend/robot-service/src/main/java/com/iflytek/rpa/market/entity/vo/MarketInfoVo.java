package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

import java.util.List;

@Data
public class MarketInfoVo {
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