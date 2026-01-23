package com.iflytek.rpa.utils.exception;

import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import lombok.Data;

@Data
public class ServiceException extends RuntimeException {
    private String code;
    private String message;

    public ServiceException(String message) {
        super(message);
        this.message = message;
        this.code = ErrorCodeEnum.E_SERVICE.getCode();
    }

    public ServiceException(String code, String message) {
        super(message);
        this.code = code;
        this.message = message;
    }
}
