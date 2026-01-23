package com.iflytek.rpa.conf.service;

import com.iflytek.rpa.conf.entity.vo.UserRegisterVo;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 用户注册服务接口
 */
public interface UserRegisterService {

    /**
     * 用户注册
     * @param phone 手机号
     * @return 注册结果，包含账号和密码
     */
    AppResponse<UserRegisterVo> register(String phone);
}
