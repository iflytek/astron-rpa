package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.UpdateUserPasswordDto;
import com.iflytek.rpa.auth.idp.iflytekIdentity.IflytekAuthenticationServiceImpl;
import com.iflytek.rpa.auth.idp.iflytekIdentity.task.UserSyncTask;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;

/**
 * 用户同步任务控制器
 */
@Slf4j
@RestController
@RequestMapping("/manager")
@RequiredArgsConstructor
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "saas", matchIfMissing = true)
public class ManagerController {

    private final UserSyncTask userSyncTask;
    private final IflytekAuthenticationServiceImpl authenticationService;

    /**
     * 执行用户同步任务
     *
     * @param force 是否强制执行（忽略锁），默认为false
     * @param loginNames 可选，指定要同步的用户登录名列表，为空则同步所有符合条件的用户
     * @return 同步结果
     */
    @PostMapping("/user-sync/execute")
    public AppResponse<UserSyncTask.SyncResult> executeSync(
            @RequestParam(value = "force", defaultValue = "false") boolean force,
            @RequestParam(value = "loginNames", required = false) List<String> loginNames) {
        try {
            log.info("收到用户同步任务请求，force={}，loginNames={}", force, loginNames);
            UserSyncTask.SyncResult result = userSyncTask.executeSync(force, loginNames);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("执行用户同步任务异常", e);
            // 返回错误结果
            UserSyncTask.SyncResult errorResult = new UserSyncTask.SyncResult();
            errorResult.setMessage("执行同步任务失败：" + e.getMessage());
            return AppResponse.success(errorResult);
        }
    }

    /**
     * 管理端更新用户密码
     *
     * @param requestDto 包含登录名、旧密码和新密码
     * @return 操作结果
     */
    @PostMapping("/user/password/update")
    public AppResponse<String> updateUserPassword(@RequestBody @Valid UpdateUserPasswordDto requestDto) {
        try {
            authenticationService.updateUserPassword(
                    requestDto.getLoginName(), requestDto.getOldPassword(), requestDto.getNewPassword());
            return AppResponse.success("更新密码成功");
        } catch (Exception e) {
            log.error("管理员更新用户密码失败，loginName={}", requestDto.getLoginName(), e);
            return AppResponse.error("更新密码失败：" + e.getMessage());
        }
    }

    /**
     * 查询同步任务状态
     *
     * @return 任务状态
     */
    @GetMapping("/status")
    public AppResponse<String> getStatus() {
        try {
            // 检查是否有任务正在执行
            Object lock = com.iflytek.rpa.auth.utils.RedisUtils.get("auth:user_sync_task:lock");
            if (lock != null) {
                return AppResponse.success("同步任务正在执行中");
            } else {
                return AppResponse.success("同步任务空闲中");
            }
        } catch (Exception e) {
            log.error("查询同步任务状态异常", e);
            return AppResponse.error("查询任务状态失败：" + e.getMessage());
        }
    }

    /**
     * 指定租户用户迁移到个人空间
     *
     * @param request HTTP请求
     * @param tenantId 租户ID（必填）
     * @param loginNames 可选，指定要迁移的账号列表，为空则迁移该租户下所有用户
     * @return 迁移结果
     */
    @PostMapping("/tenant/migrate")
    public AppResponse<String> migrateTenantUsers(
            HttpServletRequest request,
            @RequestParam(value = "tenantId") String tenantId,
            @RequestParam(value = "loginNames", required = false) List<String> loginNames) {
        try {
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error("租户ID不能为空");
            }
            ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
            UserSyncTask.MigrateResult result = userSyncTask.migrateTenantUsers(managementClient, tenantId, loginNames);
            if (StringUtils.isNotBlank(result.getMessage())
                    && result.getMessage().contains("失败")) {
                return AppResponse.error(result.getMessage());
            }
            return AppResponse.success(result.getMessage());
        } catch (Exception e) {
            log.error("租户用户迁移失败", e);
            return AppResponse.error("迁移失败：" + e.getMessage());
        }
    }
}
