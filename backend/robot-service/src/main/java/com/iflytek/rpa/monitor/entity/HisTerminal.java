package com.iflytek.rpa.monitor.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Date;
import lombok.Data;

/**
 * 终端执行情况表(his_terminal)实体类
 *
 * @author jqfang3
 * @since 2025-06-10
 */
@Data
public class HisTerminal implements Serializable {
    private static final long serialVersionUID = -805869175281442869L;
    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 部门全路径id
     */
    private String deptIdPath;

    /**
     * 终端唯一标识
     */
    private String terminalId;

    /**
     * 终端每日执行次数
     */
    private Long executeNum = 0L;

    /**
     * 每日执行时长（单位秒）
     */
    private Long executeTime = 0L;

    @TableField(exist = false)
    private BigDecimal executeTimeHour = new BigDecimal(0);

    /**
     * 统计时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date countTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted = 0;

    /**
     * 获取执行时长（小时）
     */
    public BigDecimal getExecuteTimeHourData() {
        return executeTime == null
                ? BigDecimal.ZERO
                : new BigDecimal(executeTime).divide(new BigDecimal(3600), 2, RoundingMode.HALF_UP);
    }

    /**
     * 设置执行时长并同步更新小时表示
     */
    public void setExecuteTime(Long executeTime) {
        this.executeTime = executeTime;
        if (executeTime != null) {
            this.executeTimeHour = new BigDecimal(executeTime).divide(new BigDecimal(3600), 2, RoundingMode.HALF_UP);
        } else {
            this.executeTimeHour = BigDecimal.ZERO;
        }
    }
}
