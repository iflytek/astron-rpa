package com.iflytek.rpa.starter.exception;

import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;

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

    public String getCode() {
        return this.code;
    }

    public void setCode(final String code) {
        this.code = code;
    }

    public String getMessage() {
        return this.message;
    }

    public void setMessage(final String message) {
        this.message = message;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof ServiceException)) {
            return false;
        } else {
            ServiceException other = (ServiceException) o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                Object this$code = this.getCode();
                Object other$code = other.getCode();
                if (this$code == null) {
                    if (other$code != null) {
                        return false;
                    }
                } else if (!this$code.equals(other$code)) {
                    return false;
                }

                Object this$message = this.getMessage();
                Object other$message = other.getMessage();
                if (this$message == null) {
                    return other$message == null;
                } else return this$message.equals(other$message);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof ServiceException;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $code = this.getCode();
        result = result * 59 + ($code == null ? 43 : $code.hashCode());
        Object $message = this.getMessage();
        result = result * 59 + ($message == null ? 43 : $message.hashCode());
        return result;
    }

    public String toString() {
        return "ServiceException(code=" + this.getCode() + ", message=" + this.getMessage() + ")";
    }
}
