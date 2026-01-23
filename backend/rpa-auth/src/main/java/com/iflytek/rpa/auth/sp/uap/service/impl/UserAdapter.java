package com.iflytek.rpa.auth.sp.uap.service.impl;

import java.lang.reflect.Field;

/**
 * @author mjren
 * @date 2025-03-19 15:21
 * @copyright Copyright (c) 2025 mjren
 */
public class UserAdapter {
    private final Object user;

    public UserAdapter(Object user) {
        this.user = user;
    }

    public String getId() throws Exception {
        Field field = user.getClass().getDeclaredField("id");
        field.setAccessible(true);
        return (String) field.get(user);
    }

    public String getName() throws Exception {
        Field field = user.getClass().getDeclaredField("name");
        field.setAccessible(true);
        return (String) field.get(user);
    }
}
