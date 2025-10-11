package com.iflytek.rpa.monitor.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

/**
 * 全部机器人和全部终端趋势表(HisCloudBase)实体类
 *
 * @author mjren
 * @since 2023-04-12 16:45:08
 */
@Data
public class HisBase implements Serializable {
    private static final long serialVersionUID = -59852027779143864L;

    private Long id;
    /**
     * 租户id
     */
    private String tenantId;
    /**
     * 部门编码
     */
    private String deptIdPath;
    /**
     * 部门名称
     */
    private String deptName;
    /**
     * 执行成功次数
     */
    private Long executeSuccess = 0L;
    /**
     * 执行失败次数
     */
    private Long executeFail = 0L;
    /**
     * 执行中止次数
     */
    private Long executeAbort = 0L;
    /**
     * 机器人总数
     */
    private Long robotNum = 0L;
    /**
     * 机器人累计执行次数
     */
    private Long executeTotal = 0L;
    /**
     * 累计执行时长或全部终端执行时长，单位秒
     */
    private Long executeTimeTotal = 0L;

    @TableField(exist = false)
    private BigDecimal executeTimeTotalHour = new BigDecimal(0);

    /**
     * 执行成功率
     */
    private BigDecimal executeSuccessRate = new BigDecimal(0);
    /**
     * 节省人力
     */
    private Long laborSave = 0L;

    @TableField(exist = false)
    private BigDecimal laborSaveHour = new BigDecimal(0);

    public Long getLaborSaveData() {
        //        if(executeTimeTotal != null && executeTimeTotal>0){
        //            return (long)Math.ceil((double)executeTimeTotal/3600);
        //        }
        //        return 0L;
        return executeTimeTotal;
    }
    /**
     * 累计用户数量
     */
    private Long userNum = 0L;
    /**
     * 累计终端数量
     */
    private Long terminal = 0L;

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
    private Integer deleted;

    private Long executeSuccessEveryday = 0L;

    private Long executeFailEveryday = 0L;

    private Long executeAbortEveryday = 0L;

    private BigDecimal executeSuccessRateEveryday = new BigDecimal(0);

    private Long terminalExecuteTime = 0L;

    @TableField(exist = false)
    private BigDecimal terminalExecuteTimeHour = new BigDecimal(0);

    /**
     * 终端平均执行时长，单位秒
     */
    private Long terminalTimeAvg = 0L;

    @TableField(exist = false)
    private BigDecimal terminalTimeAvgHour = new BigDecimal(0);

    @TableField(exist = false)
    private Long terminalNumToday = 0L;

    public BigDecimal getExecuteSuccessRateEverydayData() {
        Long executeNumTotal = getLongValue(executeAbortEveryday)
                + getLongValue(executeFailEveryday)
                + getLongValue(executeSuccessEveryday);
        return executeNumTotal == 0
                ? null
                : (executeSuccessEveryday == null
                        ? new BigDecimal(0)
                        : new BigDecimal(((double) executeSuccessEveryday * 100) / executeNumTotal));
    }

    public Long getLongValue(Long value) {
        return value == null ? 0 : value;
    }

    public BigDecimal getSuccessRateData() {
        if (executeTotal == null || executeTotal == 0) {
            return null;
        }
        if (executeSuccess == null) {
            new BigDecimal(0);
        }
        return new BigDecimal(((double) executeSuccess * 100) / executeTotal);
    }

    public Long getAvgTerminalTimeData() {
        return (terminal == null || terminal == 0)
                ? null
                : (terminalExecuteTime == null ? 0L : (terminalExecuteTime / terminal));
    }

    public void setTotalNull() {
        this.setExecuteSuccessRate(null);
        this.setExecuteSuccess(0L);
        this.setExecuteFail(0L);
        this.setExecuteAbort(0L);
        this.setExecuteTimeTotal(0L);
        this.setExecuteTotal(0L);
    }

    public void setEveryDayNull() {
        this.setExecuteFailEveryday(0L);
        this.setExecuteSuccessEveryday(0L);
        this.setExecuteAbortEveryday(0L);
        this.setExecuteSuccessRateEveryday(null);
        this.setTerminalTimeAvg(0L);
    }
}
