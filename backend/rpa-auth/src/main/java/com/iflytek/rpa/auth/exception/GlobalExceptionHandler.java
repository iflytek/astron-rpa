package com.iflytek.rpa.auth.exception;

import com.iflytek.rpa.auth.blacklist.exception.ShouldBeBlackException;
import com.iflytek.rpa.auth.blacklist.exception.UserBlockedException;
import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import java.util.stream.Collectors;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 统一捕获控制层未处理的异常，确保响应体始终为 AppResponse 结构。
 */
@Slf4j
@RestControllerAdvice(basePackages = "com.iflytek.rpa.auth")
@RequiredArgsConstructor
public class GlobalExceptionHandler {

    private final BlackListService blackListService;

    /**
     * 处理应当被拉入黑名单异常
     * 捕获后自动将用户添加到黑名单
     */
    @ExceptionHandler(ShouldBeBlackException.class)
    public AppResponse<String> handleShouldBeBlackException(ShouldBeBlackException e) {
        log.warn(
                "触发封禁规则，userId: {}, username: {}, reason: {}, type: {}",
                e.getUserId(),
                e.getUsername(),
                e.getReason(),
                e.getBlackType());

        try {
            // 自动添加到黑名单
            blackListService.add(e.getUserId(), e.getUsername(), e.getReason(), "SYSTEM");
            log.info("用户已自动添加到黑名单，userId: {}", e.getUserId());
        } catch (Exception ex) {
            log.error("添加黑名单失败", ex);
        }

        return AppResponse.error(ErrorCodeEnum.E_NO_POWER, "您的账号已被封禁：" + e.getReason());
    }

    /**
     * 处理用户被封禁异常
     */
    @ExceptionHandler(UserBlockedException.class)
    public AppResponse<String> handleUserBlockedException(UserBlockedException e) {
        log.warn("用户被封禁，userId: {}, username: {}, reason: {}", e.getUserId(), e.getUsername(), e.getReason());
        return AppResponse.error(ErrorCodeEnum.E_NO_POWER, e.getMessage());
    }

    @ExceptionHandler(ServiceException.class)
    public AppResponse<String> handleServiceException(ServiceException e) {
        log.warn("业务异常: {}", e.getMessage());
        return AppResponse.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public AppResponse<String> handleMethodArgumentNotValidException(Exception e) {
        FieldError fieldError = null;
        if (e instanceof MethodArgumentNotValidException) {
            fieldError =
                    ((MethodArgumentNotValidException) e).getBindingResult().getFieldError();
        } else if (e instanceof BindException) {
            fieldError = ((BindException) e).getBindingResult().getFieldError();
        }
        String message = fieldError != null ? fieldError.getDefaultMessage() : "参数校验失败";
        log.warn("参数校验异常: {}", message);
        return AppResponse.error(ErrorCodeEnum.E_PARAM.getCode(), message);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public AppResponse<String> handleConstraintViolationException(ConstraintViolationException e) {
        String message = e.getConstraintViolations().stream()
                .map(ConstraintViolation::getMessage)
                .collect(Collectors.joining("; "));
        log.warn("参数约束异常: {}", message);
        return AppResponse.error(ErrorCodeEnum.E_PARAM.getCode(), message);
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public AppResponse<String> handleHttpMessageNotReadableException(HttpMessageNotReadableException e) {
        log.warn("请求体解析异常: {}", e.getMessage());
        return AppResponse.error(ErrorCodeEnum.E_PARAM.getCode(), "请求体解析失败");
    }

    @ExceptionHandler(Exception.class)
    public AppResponse<String> handleException(Exception e) {
        log.error("系统异常", e);
        String message = e.getMessage() == null ? "服务异常，请稍后重试" : e.getMessage();
        return AppResponse.error(ErrorCodeEnum.E_SERVICE.getCode(), message);
    }
}
