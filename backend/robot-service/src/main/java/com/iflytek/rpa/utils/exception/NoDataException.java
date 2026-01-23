package com.iflytek.rpa.utils.exception;

/**
 * 项目名称： com.iflytek.fuxi.common.exception
 * 类 名 称： NoDataException
 * 类 描 述： EXCEL 导出数据时
 * 创建时间： 2020/4/1 5:27 下午
 * 创 建 人： shzhang7
 **/
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
