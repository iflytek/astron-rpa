package com.iflytek.rpa.market.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationEditDto;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationManageRequest;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationManageVo;
import com.iflytek.rpa.market.entity.vo.AppMarketClassificationVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;

/**
 * 应用市场分类服务接口
 *
 * @author auto-generated
 */
public interface AppMarketClassificationService {

    /**
     * 获取租户下的分类列表
     *
     * @return 分类列表
     * @throws NoLoginException 未登录异常
     */
    AppResponse<List<AppMarketClassificationVo>> getClassificationList() throws NoLoginException;

    /**
     * 分类管理-分类查询
     *
     * @param request 查询请求参数
     * @return 分类列表（按sort和创建时间排序）
     * @throws NoLoginException 未登录异常
     */
    AppResponse<List<AppMarketClassificationManageVo>> getClassificationManageList(
            AppMarketClassificationManageRequest request) throws NoLoginException, JsonProcessingException;

    /**
     * 分类管理-新增分类
     *
     * @param request 新增请求参数
     * @return 操作结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<String> addClassification(AppMarketClassificationEditDto request) throws NoLoginException;

    /**
     * 分类管理-修改分类
     *
     * @param request 修改请求参数
     * @return 操作结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<String> editClassification(AppMarketClassificationEditDto request) throws NoLoginException;

    /**
     * 分类管理-删除分类
     *
     * @param request 删除请求参数
     * @return 操作结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<String> deleteClassification(AppMarketClassificationEditDto request) throws NoLoginException;
}
