package com.iflytek.rpa.utils;

import java.util.List;
import java.util.Objects;

public class ListUtils {

    public static void dealIfHasNullElement(List<?> list) {
        boolean haveNull = list.stream().anyMatch(Objects::isNull);
        if (haveNull) {
            list.clear();
        }
    }
}
