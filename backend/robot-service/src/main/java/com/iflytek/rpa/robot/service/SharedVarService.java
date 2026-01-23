package com.iflytek.rpa.robot.service;

import com.iflytek.rpa.robot.entity.dto.SharedVarBatchDto;
import com.iflytek.rpa.robot.entity.vo.ClientSharedVarVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarKeyVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;

/**
 * 共享变量服务接口
 *
 * @author jqfang3
 * @since 2025-07-21
 */
public interface SharedVarService {
    /**
     * 获取共享变量租户密钥
     *
     * @return 密钥信息
     * @throws NoLoginException 未登录异常
     */
    AppResponse<SharedVarKeyVo> getSharedVarKey() throws NoLoginException;

    /**
     * 客户端-查询该用户可用的所有共享变量
     *
     * @return 共享变量列表
     * @throws NoLoginException 未登录异常
     */
    AppResponse<List<ClientSharedVarVo>> getClientSharedVars() throws NoLoginException;

    AppResponse<List<ClientSharedVarVo>> getBatchSharedVar(SharedVarBatchDto updateDto) throws NoLoginException;
}
