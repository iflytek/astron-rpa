package com.iflytek.rpa.utils.response;

import java.io.Serializable;
import org.springframework.util.StringUtils;

/**
 * @author wyzhou3
 * @version 1.0
 * @description 返回类
 **/
public class AppResponse<T> implements Serializable {
    /**
     * 请求返回码
     */
    private String code;
    /**
     * 请求返回数据
     */
    private T data;
    /**
     * 描述信息
     */
    private String message;

    private AppResponse() {}

    /**
     * 返回错误信息
     *
     * @param codeEnum 错误信息码
     * @return AppResponse
     */
    public static <T> AppResponse<T> error(ErrorCodeEnum codeEnum) {
        return error(codeEnum, null);
    }

    /**
     * 返回错误信息
     *
     * @param codeEnum 错误信息码
     * @param message  错误信息
     * @return AppResponse
     */
    public static <T> AppResponse<T> error(ErrorCodeEnum codeEnum, String message) {
        if (StringUtils.isEmpty(message)) {
            message = codeEnum.getFlag();
        }

        AppResponse<T> response = new AppResponse<>();
        response.setCode(codeEnum.getCode());
        response.setData(null);
        response.setMessage(message);
        return response;
    }

    /**
     * 返回错误信息
     *
     * @param code    错误信息码
     * @param message 错误信息
     * @return AppResponse
     */
    public static AppResponse<String> error(String code, String message) {
        AppResponse<String> response = new AppResponse<>();
        response.setCode(code);
        response.setData("");
        response.setMessage(message);
        return response;
    }

    /**
     * 返回错误信息
     *
     * @param message 错误信息
     * @return AppResponse
     */
    public static AppResponse<String> error(String message) {
        return error(ErrorCodeEnum.E_COMMON.getCode(), message);
    }

    /**
     * 成功请求信息
     *
     * @param data 请求数据
     * @return AppResponse
     */
    public static <T> AppResponse<T> success(T data) {
        AppResponse<T> response = new AppResponse<T>();
        response.setCode(ErrorCodeEnum.S_SUCCESS.getCode());
        response.setData(data);
        response.setMessage("");
        return response;
    }

    /**
     * 请求是否成功
     *
     * @return boolean
     */
    public boolean ok() {
        return this.code.equals(ErrorCodeEnum.S_SUCCESS.getCode());
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
