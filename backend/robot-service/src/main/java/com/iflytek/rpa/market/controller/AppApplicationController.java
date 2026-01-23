package com.iflytek.rpa.market.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.market.entity.dto.*;
import com.iflytek.rpa.market.entity.vo.MyApplicationPageListVo;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.CollectionUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 上架、使用申请管理
 */
@RestController
@RequestMapping("/application")
public class AppApplicationController {

    @Autowired
    private AppApplicationService appApplicationService;

    /**
     * 查询审核开关状态
     */
    @GetMapping("/get-audit-status")
    public AppResponse<String> getAuditStatus() throws NoLoginException {
        return appApplicationService.getAuditStatus();
    }

    /**
     * 客户端-我的申请列表
     *
     * @param queryDto
     * @return
     * @throws Exception
     */
    @PostMapping("/my-application-page-list")
    public AppResponse<IPage<MyApplicationPageListVo>> getMyApplicationPageList(
            @RequestBody MyApplicationPageListDto queryDto) throws Exception {
        return appApplicationService.getMyApplicationPageList(queryDto);
    }

    /**
     * 客户端-撤销 我的申请
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/my-application-cancel")
    public AppResponse<String> cancelMyApplication(@RequestBody MyApplicationDto dto) throws Exception {
        return appApplicationService.cancelMyApplication(dto);
    }

    /**
     * 客户端-删除 我的申请
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/my-application-delete")
    public AppResponse<String> deleteMyApplication(@RequestBody MyApplicationDto dto) throws Exception {
        return appApplicationService.deleteMyApplication(dto);
    }

    /**
     * 客户端-提交上架申请前，查询当前版本机器人是否需要上架审核
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/pre-release-check")
    public AppResponse<Integer> preReleaseCheck(@Valid @RequestBody PreReleaseCheckDto dto) throws Exception {
        return appApplicationService.preReleaseCheck(dto);
    }

    /**
     * 客户端-提交上架申请
     */
    @PostMapping("/submit-release-application")
    public AppResponse<String> submitReleaseApplication(@Valid @RequestBody ReleaseApplicationDto applicationDto)
            throws Exception {
        if (CollectionUtils.isEmpty(applicationDto.getMarketIdList())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场id不能为空");
        }
        return appApplicationService.submitReleaseApplication(applicationDto);
    }

    /**
     * 客户端-发版后，提交上架申请前，查询是否需要上架审核
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/pre-submit-after-publish-check")
    public AppResponse<?> preSubmitAfterPublishCheck(@Valid @RequestBody PreReleaseCheckDto dto) throws Exception {
        return appApplicationService.preSubmitAfterPublishCheck(dto);
    }

    /**
     * 客户端-发版后，提交上架申请
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/submit-after-publish")
    public AppResponse<String> submitAfterPublish(@Valid @RequestBody SubmitAfterPublishDto dto) throws Exception {
        if (CollectionUtils.isEmpty(dto.getMarketIdList())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场id不能为空");
        }
        return appApplicationService.submitAfterPublish(dto);
    }

    /**
     * 客户端-提交使用申请
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/submit-use-application")
    public AppResponse<String> submitUseApplication(@Valid @RequestBody UsePermissionCheckDto dto) throws Exception {
        return appApplicationService.submitUseApplication(dto);
    }

    /**
     * 客户端-使用前权限检查
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/use-permission-check")
    public AppResponse<Integer> usePermissionCheck(@Valid @RequestBody UsePermissionCheckDto dto) throws Exception {
        return appApplicationService.usePermissionCheck(dto);
    }
}
