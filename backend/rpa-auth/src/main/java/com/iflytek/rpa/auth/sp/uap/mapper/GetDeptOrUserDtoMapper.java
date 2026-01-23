package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.GetDeptOrUserDto;
import com.iflytek.rpa.auth.core.entity.Org;
import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * GetDeptOrUserDto映射器
 * 用于将UAP实体列表转换为core实体列表并构建GetDeptOrUserDto
 *
 * @author xqcao2
 */
@Component
public class GetDeptOrUserDtoMapper {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private OrgMapper orgMapper;

    /**
     * 将UAP用户和部门列表转换为core实体的GetDeptOrUserDto
     *
     * @param uapUsers UAP用户列表
     * @param uapOrgs UAP部门列表
     * @return 包含core实体的GetDeptOrUserDto
     */
    public GetDeptOrUserDto toCoreGetDeptOrUserDto(List<UapUser> uapUsers, List<UapOrg> uapOrgs) {
        GetDeptOrUserDto target = new GetDeptOrUserDto();

        // 映射用户列表
        if (uapUsers != null && !uapUsers.isEmpty()) {
            List<User> userList = uapUsers.stream()
                    .map(userMapper::fromUapUser)
                    .filter(user -> user != null)
                    .collect(Collectors.toList());
            target.setUserList(userList);
        } else {
            target.setUserList(Collections.emptyList());
        }

        // 映射部门列表
        if (uapOrgs != null && !uapOrgs.isEmpty()) {
            List<Org> orgList = uapOrgs.stream()
                    .map(orgMapper::fromUapOrg)
                    .filter(org -> org != null)
                    .collect(Collectors.toList());
            target.setDeptList(orgList);
        } else {
            target.setDeptList(Collections.emptyList());
        }

        return target;
    }
}
