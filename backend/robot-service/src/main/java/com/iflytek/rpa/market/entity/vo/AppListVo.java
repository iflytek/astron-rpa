package com.iflytek.rpa.market.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * 应用查询响应参数
 */
@Data
public class AppListVo {
    private String appId;

    private String marketId;

    /**
     * 应用名称
     */
    private String appName;

    /**
     * 所有者姓名
     */
    private String creatorName;

    /**
     * 所有者手机号
     */
    private String creatorPhone;

    /**
     * 应用分类
     */
    private String category;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 状态：已上架/已下架
     */
    private String status;

    /**
     * 详情查询
     */
    private String robotId;

    private Integer version;

    /**
     * 上架审核-密级标识
     */
    private String securityLevel;
}
