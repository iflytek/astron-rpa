package com.iflytek.rpa.auth.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/16 19:28
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result {

    private Integer code;

    private String status;

    private Object data;

    public static Result success(Object data) {
        return new Result(200, "ok", data);
    }

    public static Result failure(String status) {
        return new Result(500, status, null);
    }
}
