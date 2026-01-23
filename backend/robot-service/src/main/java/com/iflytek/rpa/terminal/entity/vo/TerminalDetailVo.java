package com.iflytek.rpa.terminal.entity.vo;

import lombok.Data;

@Data
public class TerminalDetailVo {
    Long id; // 终端ID
    String terminalId; // 终端唯一标识 替换MAC地址
    String name; // 终端名称
    String account; // 终端账号
    String os; // 终端操作系统
    String ip; // 终端IP
    Integer port; // 终端端口
}
