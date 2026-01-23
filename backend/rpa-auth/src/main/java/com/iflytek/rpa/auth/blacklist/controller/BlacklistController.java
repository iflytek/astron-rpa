package com.iflytek.rpa.auth.blacklist.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.auth.blacklist.dao.UserBlacklistDao;
import com.iflytek.rpa.auth.blacklist.dto.*;
import com.iflytek.rpa.auth.blacklist.entity.UserBlacklist;
import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import javax.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.util.StringUtils;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 黑名单管理接口
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
@RestController
@RequestMapping("/blacklist")
@RequiredArgsConstructor
public class BlacklistController {

    private final BlackListService blackListService;
    private final UserBlacklistDao userBlacklistDao;

    /**
     * 手动添加用户到黑名单
     *
     * @param dto 添加黑名单 DTO
     * @param request HTTP 请求
     * @return 黑名单记录
     */
    @PostMapping("/add")
    public AppResponse<BlacklistVo> add(@RequestBody @Validated AddBlacklistDto dto, HttpServletRequest request) {
        try {
            // 获取当前操作人
            UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
            String operator = loginUser != null ? loginUser.getLoginName() : "ADMIN";

            log.info(
                    "手动添加黑名单，userId: {}, username: {}, reason: {}, operator: {}",
                    dto.getUserId(),
                    dto.getUsername(),
                    dto.getReason(),
                    operator);

            UserBlacklist blacklist =
                    blackListService.add(dto.getUserId(), dto.getUsername(), dto.getReason(), operator);

            return AppResponse.success(convertToVo(blacklist));
        } catch (Exception e) {
            log.error("添加黑名单失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "添加黑名单失败：" + e.getMessage());
        }
    }

    /**
     * 手动解封用户
     *
     * @param dto 解封 DTO
     * @param request HTTP 请求
     * @return 是否成功
     */
    @PostMapping("/unban")
    public AppResponse<Boolean> unban(@RequestBody @Validated UnbanDto dto, HttpServletRequest request) {
        try {
            // 获取当前操作人
            UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
            String operator = loginUser != null ? loginUser.getLoginName() : "ADMIN";

            log.info("手动解封用户，userId: {}, operator: {}", dto.getUserId(), operator);

            boolean success = blackListService.unban(dto.getUserId(), operator);
            return AppResponse.success(success);
        } catch (Exception e) {
            log.error("解封用户失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "解封用户失败：" + e.getMessage());
        }
    }

    /**
     * 检查用户是否在黑名单中
     *
     * @param userId 用户ID
     * @return 黑名单信息
     */
    @GetMapping("/check")
    public AppResponse<BlacklistCacheDto> check(@RequestParam @NotBlank(message = "用户ID不能为空") String userId) {
        try {
            log.info("检查用户黑名单状态，userId: {}", userId);
            BlacklistCacheDto blacklist = blackListService.isBlocked(userId);
            return AppResponse.success(blacklist);
        } catch (Exception e) {
            log.error("检查黑名单失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "检查黑名单失败：" + e.getMessage());
        }
    }

    /**
     * 查询黑名单列表（分页）
     *
     * @param queryDto 查询条件
     * @return 黑名单列表
     */
    @PostMapping("/list")
    public AppResponse<IPage<BlacklistVo>> list(@RequestBody BlacklistQueryDto queryDto) {
        try {
            log.info("查询黑名单列表，条件: {}", queryDto);

            // 构建查询条件
            LambdaQueryWrapper<UserBlacklist> wrapper = new LambdaQueryWrapper<>();

            if (!StringUtils.isEmpty(queryDto.getUserId())) {
                wrapper.eq(UserBlacklist::getUserId, queryDto.getUserId());
            }

            if (!StringUtils.isEmpty(queryDto.getUsername())) {
                wrapper.like(UserBlacklist::getUsername, queryDto.getUsername());
            }

            if (queryDto.getStatus() != null) {
                wrapper.eq(UserBlacklist::getStatus, queryDto.getStatus());
            }

            wrapper.orderByDesc(UserBlacklist::getCreateTime);

            // 分页查询
            Page<UserBlacklist> page = new Page<>(queryDto.getPageNum(), queryDto.getPageSize());
            IPage<UserBlacklist> result = userBlacklistDao.selectPage(page, wrapper);

            // 转换为 VO
            IPage<BlacklistVo> voPage = result.convert(this::convertToVo);

            return AppResponse.success(voPage);
        } catch (Exception e) {
            log.error("查询黑名单列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询黑名单列表失败：" + e.getMessage());
        }
    }

    /**
     * 查询用户的封禁历史
     *
     * @param userId 用户ID
     * @return 封禁历史列表
     */
    @GetMapping("/history")
    public AppResponse<List<BlacklistVo>> getHistory(@RequestParam @NotBlank(message = "用户ID不能为空") String userId) {
        try {
            log.info("查询用户封禁历史，userId: {}", userId);
            List<UserBlacklist> history = blackListService.getHistory(userId);
            List<BlacklistVo> voList = history.stream().map(this::convertToVo).collect(Collectors.toList());
            return AppResponse.success(voList);
        } catch (Exception e) {
            log.error("查询封禁历史失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询封禁历史失败：" + e.getMessage());
        }
    }

    /**
     * 手动触发批量解封已过期用户
     *
     * @return 解封数量
     */
    @PostMapping("/batch-unban-expired")
    public AppResponse<Integer> batchUnbanExpired() {
        try {
            log.info("手动触发批量解封");
            int count = blackListService.batchUnbanExpired();
            return AppResponse.success(count);
        } catch (Exception e) {
            log.error("批量解封失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "批量解封失败：" + e.getMessage());
        }
    }

    /**
     * 转换为视图对象
     */
    private BlacklistVo convertToVo(UserBlacklist blacklist) {
        LocalDateTime now = LocalDateTime.now();
        long remainingSeconds = 0;
        String remainingTimeDesc = "已过期";

        if (blacklist.getStatus() == 1 && blacklist.getEndTime().isAfter(now)) {
            remainingSeconds = Duration.between(now, blacklist.getEndTime()).getSeconds();
            remainingTimeDesc = formatDuration(remainingSeconds);
        }

        return BlacklistVo.builder()
                .id(blacklist.getId())
                .userId(blacklist.getUserId())
                .username(blacklist.getUsername())
                .banReason(blacklist.getBanReason())
                .banLevel(blacklist.getBanLevel())
                .banCount(blacklist.getBanCount())
                .banDuration(blacklist.getBanDuration())
                .banDurationDesc(formatDuration(blacklist.getBanDuration()))
                .startTime(blacklist.getStartTime())
                .endTime(blacklist.getEndTime())
                .remainingSeconds(remainingSeconds)
                .remainingTimeDesc(remainingTimeDesc)
                .status(blacklist.getStatus())
                .statusDesc(blacklist.getStatus() == 1 ? "生效中" : "已解封")
                .operator(blacklist.getOperator())
                .createTime(blacklist.getCreateTime())
                .build();
    }

    /**
     * 格式化时长
     */
    private String formatDuration(long seconds) {
        if (seconds <= 0) {
            return "0秒";
        }

        long days = seconds / 86400;
        long hours = (seconds % 86400) / 3600;
        long minutes = (seconds % 3600) / 60;
        long secs = seconds % 60;

        StringBuilder sb = new StringBuilder();
        if (days > 0) {
            sb.append(days).append("天");
        }
        if (hours > 0) {
            sb.append(hours).append("小时");
        }
        if (minutes > 0) {
            sb.append(minutes).append("分钟");
        }
        if (secs > 0 && days == 0 && hours == 0) {
            sb.append(secs).append("秒");
        }

        return sb.length() > 0 ? sb.toString() : "0秒";
    }
}
