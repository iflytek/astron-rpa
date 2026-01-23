package com.iflytek.rpa.market.controller;

import com.iflytek.rpa.market.entity.vo.AppMarketClassificationVo;
import com.iflytek.rpa.market.service.AppMarketClassificationService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 应用市场-分类
 *
 * @author auto-generated
 */
@RestController
@RequestMapping("/classification")
public class AppApplicationClassificationController {

    @Autowired
    private AppMarketClassificationService appMarketClassificationService;

    /**
     * 客户端-获取分类列表
     *
     * @return 分类列表（id和name）
     * @throws NoLoginException 未登录异常
     */
    @GetMapping("/list")
    public AppResponse<List<AppMarketClassificationVo>> getClassificationList() throws NoLoginException {
        return appMarketClassificationService.getClassificationList();
    }
}
