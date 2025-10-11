package com.iflytek.rpa.monitor.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

/**
 * 单个机器人趋势表(HisCloudRobot)实体类
 *
 * @author mjren
 * @since 2023-04-12 16:45:08
 */
@Data
public class HisRobot implements Serializable {
    private static final long serialVersionUID = 512058420442741592L;

    private Long id;
    /**
     * 租户id
     */
    private String tenantId;

    /**用户id*/
    private String userId;
    /**
     * 部门编码
     */
    private String deptIdPath;
    /**
     * 部门名称
     */

    /**
     * 当日执行总次数
     */
    private Long executeNumTotal = 0L;
    /**
     * 成功次数
     */
    private Long executeSuccess = 0L;
    /**
     * 失败次数
     */
    private Long executeFail = 0L;
    /**
     * 中止次数
     */
    private Long executeAbort = 0L;

    private Long executeTime = 0L;
    /**
     * 成功率
     */
    private BigDecimal executeSuccessRate = new BigDecimal(0);
    /**
     * 统计时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date countTime;
    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

    private String robotId;

    public HisRobot() {}

    public HisRobot(
            String robotId,
            String tenantId,
            String deptIdPath,
            String deptName,
            Long executeNumTotal,
            Long executeSuccess,
            Long executeFail,
            Long executeAbort,
            double executeSuccessRate,
            Date countTime,
            Date updateTime,
            Long executeTime) {
        this.robotId = robotId;
        this.tenantId = tenantId;
        this.deptIdPath = deptIdPath;
        this.executeNumTotal = executeNumTotal;
        this.executeSuccess = executeSuccess;
        this.executeFail = executeFail;
        this.executeAbort = executeAbort;
        this.executeTime = executeTime;
        this.executeSuccessRate = BigDecimal.valueOf(executeSuccessRate);
        this.countTime = countTime;
        this.updateTime = updateTime;
        this.deleted = 0;
    }

    public BigDecimal getSuccessRateData() {
        if (executeNumTotal == null || executeNumTotal == 0 || executeSuccess == null) {
            return null;
        }
        return new BigDecimal(((double) executeSuccess * 100) / executeNumTotal);
    }
}
