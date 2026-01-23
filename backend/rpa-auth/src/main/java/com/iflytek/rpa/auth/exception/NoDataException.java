package com.iflytek.rpa.auth.exception;

public class NoDataException extends Exception {

    public NoDataException() {
        super();
    }

    public NoDataException(String message) {
        super(message);
    }

    public NoDataException(Exception e) {
        super(e);
    }
}
