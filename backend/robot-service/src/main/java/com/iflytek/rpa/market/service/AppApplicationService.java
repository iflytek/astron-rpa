package com.iflytek.rpa.market.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.dto.*;
import com.iflytek.rpa.market.entity.vo.LatestVersionRobotVo;
import com.iflytek.rpa.market.entity.vo.MyApplicationPageListVo;
import com.iflytek.rpa.market.entity.vo.ReleasePageListVo;
import com.iflytek.rpa.market.entity.vo.UsePageListVo;
import com.iflytek.rpa.robot.entity.vo.ExecuteListVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.validation.Valid;

public interface AppApplicationService {

    AppResponse<String> auditApplication(AuditApplicationDto auditApplicationDto) throws Exception;

    AppResponse<IPage<ReleasePageListVo>> getReleasePageList(ReleasePageListDto queryDto) throws Exception;

    AppResponse<IPage<UsePageListVo>> getUsePageList(UsePageListDto queryDto) throws Exception;

    AppResponse<String> changeAudit(ChangeAuditDto changeAuditDto) throws NoLoginException, IOException;

    AppResponse<String> releaseDelete(ReleaseDeleteDto releaseDeleteDto) throws NoLoginException;

    AppResponse<String> useDelete(UseDeleteDto useDeleteDto) throws NoLoginException;

    /**
     * 启用或关闭审核功能
     *
     * @param status 审核开关状态
     * @param reason 操作原因
     * @return 操作结果
     * @throws NoLoginException
     */
    AppResponse<String> enableAudit(String status, String reason) throws NoLoginException;

    /**
     * 查询当前租户的审核开关状态
     *
     * @return 审核开关状态
     * @throws NoLoginException
     */
    AppResponse<String> getAuditStatus() throws NoLoginException;

    List<LatestVersionRobotVo> getRobotListApplicationStatus(List<LatestVersionRobotVo> voList);

    AppResponse<IPage<MyApplicationPageListVo>> getMyApplicationPageList(MyApplicationPageListDto queryDto)
            throws NoLoginException;

    AppResponse<String> cancelMyApplication(MyApplicationDto dto) throws NoLoginException;

    AppResponse<String> deleteMyApplication(MyApplicationDto dto) throws NoLoginException;

    /**
     * 获取 密级标识 和 截止时间
     *
     * @param appResourceList
     * @param resVerDtoList
     */
    void packageApplicationInfo(List<AppMarketResource> appResourceList, List<ResVerDto> resVerDtoList, String userId);

    /**
     * 客户端 - 执行器-使用权限校验
     *
     * @param ansRecords
     */
    void packageUsePermission(List<ExecuteListVo> ansRecords) throws NoLoginException;

    /**
     * 客户端使用权限检查
     *
     * @param dto
     * @return
     * @throws Exception
     */
    AppResponse<Integer> usePermissionCheck(UsePermissionCheckDto dto) throws Exception;

    /**
     * 查询当前版本机器人是否需要上架审核
     */
    AppResponse<Integer> preReleaseCheck(PreReleaseCheckDto dto) throws Exception;

    /**
     * 客户端-提交上架申请
     *
     * @param applicationDto 申请参数
     * @return 操作结果
     * @throws NoLoginException
     */
    AppResponse<String> submitReleaseApplication(ReleaseApplicationDto applicationDto) throws Exception;

    AppResponse<?> preSubmitAfterPublishCheck(@Valid PreReleaseCheckDto dto) throws NoLoginException;
    /**
     * 客户端-提交上架申请后，提交发版信息
     * @param dto
     * @return
     * @throws NoLoginException
     */
    AppResponse<String> submitAfterPublish(SubmitAfterPublishDto dto) throws Exception;

    /**
     * 客户端-新增使用申请
     *
     * @param dto
     * @return
     * @throws Exception
     */
    AppResponse<String> submitUseApplication(UsePermissionCheckDto dto) throws Exception;
}
