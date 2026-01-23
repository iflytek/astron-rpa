package com.iflytek.rpa.terminal.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * @author jqfang3
 * @date 2025-06-17
 */
@Data
public class TerminalLoginRecord {

    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.ASSIGN_UUID)
    private String id;

    /**
     * 终端id
     */
    private String terminalId;

    /**
     * 部门id
     */
    private String deptId;

    /**
     * 部门全路径id
     */
    private String deptIdPath;

    /**
     * 登录IP
     */
    private String ip;

    /**
     * 登录时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date loginTime;

    /**
     * 登出时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date logoutTime;

    /**
     * 是否登录成功 (0: 登录失败, 1: 登录成功)
     */
    private Integer loginStatus;

    /**
     * 操作描述
     */
    private String remark;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 更新者id
     */
    private String updaterId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 (0: 未删除, 1: 已删除)
     */
    private Integer deleted;
}
