package com.iflytek.rpa.utils;

import java.util.List;
import java.util.function.Consumer;

/**
 * @author mjren
 * @date 2025-01-15 16:32
 * @copyright Copyright (c) 2025 mjren
 * 一般用于批量更新和插入数据
 */
public class ListBatchUtil {
    /**
     * 批量操作列表数据
     *
     * @param dataList        数据列表
     * @param batchSize       每批次大小
     * @param operationMethod 数据操作的函数
     * @param <T>             数据类型
     */
    public static <T> void process(List<T> dataList, int batchSize, Consumer<List<T>> operationMethod) {
        if (dataList == null || dataList.isEmpty()) {
            throw new IllegalArgumentException("Data list must not be null or empty.");
        }
        if (batchSize <= 0) {
            throw new IllegalArgumentException("Batch size must be positive.");
        }

        int totalSize = dataList.size();

        // 使用 for 循环分批次处理
        for (int fromIndex = 0; fromIndex < totalSize; fromIndex += batchSize) {
            int toIndex = Math.min(fromIndex + batchSize, totalSize);
            List<T> batchList = dataList.subList(fromIndex, toIndex);
            operationMethod.accept(batchList); // 执行插入操作
        }
    }
}
