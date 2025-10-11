package com.iflytek.rpa.monitor.entity.dto;

import lombok.Data;

@Data
public class LoginDetailParam {
    private String userId; // 用户id
    private String tenantId; // 租户id
    private String terminalMac; // 终端mac
    private String terminalIp; // 终端ip
    private String terminalName; // 终端名称
    private String deptIdPath; // 部门全路径id
    private String deptName; // 部门名称
    private String accountLast; // 最后登录账号
    private String userNameLast; // 最后登录用户名
    private String action; // 操作类型

    public LoginDetailParam() {}

    public LoginDetailParam(String userId, String action, String terminalMac, String terminalIp, String terminalName) {
        this.userId = userId;
        this.action = action;
        this.terminalMac = terminalMac;
        this.terminalIp = terminalIp;
        this.terminalName = terminalName;
    }
}
