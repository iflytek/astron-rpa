package com.iflytek.rpa.common.feign.entity.dto;

import com.iflytek.rpa.common.feign.entity.Org;
import com.iflytek.rpa.common.feign.entity.User;
import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-13 14:47
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class GetDeptOrUserDto {

    private List<User> userList;

    private List<Org> deptList;
}
