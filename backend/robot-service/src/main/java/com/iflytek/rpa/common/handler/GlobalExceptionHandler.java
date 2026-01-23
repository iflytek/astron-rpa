package com.iflytek.rpa.common.handler;

import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Optional;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.util.StringUtils;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理，将常见异常包装成统一的 AppResponse 返回。
 */
@Slf4j
@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class GlobalExceptionHandler {

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public AppResponse<String> handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
        String msg = Optional.ofNullable(ex.getBindingResult().getFieldError())
                .map(error ->
                        StringUtils.hasText(error.getDefaultMessage()) ? error.getDefaultMessage() : error.toString())
                .orElse("参数校验失败");
        log.warn("MethodArgumentNotValidException: {}", msg);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, msg);
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(BindException.class)
    public AppResponse<String> handleBindException(BindException ex) {
        String msg = Optional.ofNullable(ex.getFieldError())
                .map(error ->
                        StringUtils.hasText(error.getDefaultMessage()) ? error.getDefaultMessage() : error.toString())
                .orElse("参数绑定失败");
        log.warn("BindException: {}", msg);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, msg);
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(ConstraintViolationException.class)
    public AppResponse<String> handleConstraintViolation(ConstraintViolationException ex) {
        String msg = ex.getConstraintViolations().stream()
                .map(ConstraintViolation::getMessage)
                .filter(StringUtils::hasText)
                .findFirst()
                .orElse("参数校验失败");
        log.warn("ConstraintViolationException: {}", msg);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, msg);
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public AppResponse<String> handleHttpMessageNotReadable(HttpMessageNotReadableException ex) {
        log.warn("HttpMessageNotReadableException", ex);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_PARSE, "请求参数解析失败");
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public AppResponse<String> handleMissingParam(MissingServletRequestParameterException ex) {
        String msg = "缺少必填参数: " + ex.getParameterName();
        log.warn("MissingServletRequestParameterException: {}", msg);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, msg);
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(ServiceException.class)
    public AppResponse<String> handleServiceException(ServiceException ex) {
        log.warn("ServiceException: {}", ex.getMessage());
        return AppResponse.error(ex.getCode(), ex.getMessage());
    }

    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(Exception.class)
    public AppResponse<String> handleException(Exception ex) {
        log.error("Unhandled exception", ex);
        return AppResponse.error(ErrorCodeEnum.E_COMMON, "系统异常，请稍后重试");
    }
}
