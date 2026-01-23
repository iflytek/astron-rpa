package com.iflytek.rpa.auth.exception;

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
