package com.iflytek.rpa.auth.exception;

public class NoFileException extends Exception {

    public NoFileException() {
        super();
    }

    public NoFileException(String message) {
        super(message);
    }

    public NoFileException(Exception e) {
        super(e);
    }
}
