package com.iflytek.rpa.auth.sp.uap.entity;

import lombok.Data;

/**
 * 当前操作人
 *
 * 接口或者真实用户
 *
 * @author keler
 * @date 2020/3/8
 */
@Data
public class Actor {
    /** ID */
    private Long id;

    /** 账号:用户域账号或者接口账号 */
    private String account;

    /** 名称:用户姓名或者接口名称 */
    private String name;
}
