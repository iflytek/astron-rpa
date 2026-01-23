package com.iflytek.rpa.quota.controller;

import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 配额校验控制器
 * 提供配额校验相关的接口
 *
 * @author system
 * @since 2024-12-20
 */
@RestController
@RequestMapping("/quota")
public class QuotaController {

    @Autowired
    private QuotaCheckService quotaCheckService;

    /**
     * 校验设计器配额（designer_count）
     * 检查当前用户的设计器数量是否超限
     *
     * @return true表示未超限，false表示已超限
     * @throws NoLoginException 未登录异常
     */
    @GetMapping("/check-designer")
    public AppResponse<Boolean> checkDesignerQuota() throws NoLoginException {
        boolean result = quotaCheckService.checkDesignerQuota();
        return AppResponse.success(result);
    }

    /**
     * 校验市场加入数量配额（market_join_count）
     * 检查当前用户已加入的市场数量是否超限
     *
     * @return true表示未超限，false表示已超限
     * @throws NoLoginException 未登录异常
     */
    @GetMapping("/check-market-join")
    public AppResponse<Boolean> checkMarketJoinQuota() throws NoLoginException {
        boolean result = quotaCheckService.checkMarketJoinQuota();
        return AppResponse.success(result);
    }
}
