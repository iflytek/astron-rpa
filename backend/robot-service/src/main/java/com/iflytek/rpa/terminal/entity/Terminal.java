package com.iflytek.rpa.terminal.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-06-10 16:38
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class Terminal {

    /**
     * 主键id，用于数据定时统计的进度管理
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 终端唯一标识，如设备mac地址
     */
    private String terminalId;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 部门ID
     */
    private String deptId;

    /**
     * 部门全路径ID
     */
    private String deptIdPath;

    /**
     * 终端名称
     */
    private String name;

    /**
     * 设备账号
     */
    private String account;

    /**
     * 操作系统
     */
    private String os;

    /**
     * ip列表
     */
    private String ip;

    /**
     * 实际连接源IP，服务端检测后的推荐ip
     */
    private String actualClientIp;

    /**
     * 用户自定义ip
     */
    private String customIp;

    /**
     * 端口号
     */
    private Integer port;
    /**
     * 用户自定义端口
     */
    private Integer customPort;
    /**
     * 当前状态，运行中busy，空闲free，离线offline，单机中standalone
     */
    private String status;

    /**
     * 终端描述
     */
    private String remark;

    /**
     * 最后登录的用户的id，用于根据姓名筛选
     */
    private String userId;

    /**
     * 信息维护：电脑设备用户名，终端账号
     */
    private String osName;

    /**
     * 信息维护：电脑设备用户密码，终端账号密码
     */
    private String osPwd;

    //    /**
    //     * CPU占用率（百分比)
    //     */
    //    @TableField(exist = false)
    //    private Integer cpu;
    //
    //    /**
    //     * 内存占用率（百分比)
    //     */
    //    @TableField(exist = false)
    //    private Integer memory;
    //
    //    /**
    //     * 硬盘占用率（百分比)
    //     */
    //    @TableField(exist = false)
    //    private Integer disk;

    /**
     * 是否调度模式 (0: 否, 1: 是)
     */
    private Integer isDispatch;

    /**
     * 视频监控URL
     */
    private String monitorUrl;

    /**
     * 终端记录创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 (0: 未删除, 1: 已删除)
     */
    private Short deleted;
}
