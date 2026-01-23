package com.iflytek.rpa.utils.exception;

public class NoLoginException extends Exception {
    public NoLoginException() {
        super();
    }

    public NoLoginException(String message) {
        super(message);
    }

    public NoLoginException(Exception e) {
        super(e);
    }
}
