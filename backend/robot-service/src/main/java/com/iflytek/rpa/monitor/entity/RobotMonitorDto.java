package com.iflytek.rpa.monitor.entity;

import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import javax.validation.constraints.NotBlank;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class RobotMonitorDto {
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    @NotBlank(message = "截止时间不能为空")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private Date deadline;

    private Integer version;

    private Long executeTotal = 0L;

    private Long executeRunning = 0L;

    private BigDecimal executeRunningRate = new BigDecimal(0);
    /**
     * 执行成功次数
     */
    private Long executeSuccess = 0L;

    private BigDecimal executeSuccessRate = new BigDecimal(0);


    /**
     * 执行失败次数
     */
    private Long executeFail = 0L;

    private BigDecimal executeFailRate = new BigDecimal(0);

    /**
     * 执行中止次数
     */
    private Long executeAbort = 0L;

    private BigDecimal executeAbortRate = new BigDecimal(0);
}
