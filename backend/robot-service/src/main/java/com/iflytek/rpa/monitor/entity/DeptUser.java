package com.iflytek.rpa.monitor.entity;

import java.io.Serializable;
import lombok.Data;

/**
 * (DeptUser)实体类
 *
 * @author mjren
 * @since 2023-04-12 16:51:49
 */
@Data
public class DeptUser implements Serializable {
    private static final long serialVersionUID = -20954202161378002L;

    /**
     * 用户id
     */
    private String userId;

    private String deptIdPath;
}
