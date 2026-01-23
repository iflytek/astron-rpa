package com.iflytek.rpa.robot.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import com.iflytek.rpa.robot.entity.vo.SharedFilePageVo;
import com.iflytek.rpa.robot.service.SharedFileService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 共享文件管理
 *
 * @author yfchen40
 * @since 2025-07-21
 */
@RestController
@RequestMapping("/robot-shared-file")
public class RobotSharedFileController {
    @Autowired
    private SharedFileService sharedFileService;

    /**
     * 获取共享文件分页列表
     *
     * @param queryDto 查询条件
     * @return 分页结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/page")
    public AppResponse<IPage<SharedFilePageVo>> getSharedFilePageList(@RequestBody SharedFilePageDto queryDto)
            throws NoLoginException {
        return sharedFileService.getSharedFilePageList(queryDto);
    }
}
