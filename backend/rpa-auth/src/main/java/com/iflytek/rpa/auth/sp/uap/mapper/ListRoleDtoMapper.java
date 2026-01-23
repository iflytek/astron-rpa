package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.ListRoleDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * ListRoleDto映射器
 * 用于将core包下的ListRoleDto转换为UAP客户端的ListRoleDto
 *
 * @author xqcao2
 */
@Component
public class ListRoleDtoMapper {

    /**
     * 将core包下的ListRoleDto转换为UAP客户端的ListRoleDto
     *
     * @param listRoleDto core包下的ListRoleDto
     * @return UAP客户端的ListRoleDto
     */
    public com.iflytek.sec.uap.client.core.dto.role.ListRoleDto toUapListRoleDto(ListRoleDto listRoleDto) {
        if (listRoleDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.role.ListRoleDto uapListRoleDto =
                new com.iflytek.sec.uap.client.core.dto.role.ListRoleDto();
        // 使用BeanUtils复制属性（包括继承自PageQueryDto的pageNum和pageSize）
        BeanUtils.copyProperties(listRoleDto, uapListRoleDto);

        return uapListRoleDto;
    }

    /**
     * 将UAP客户端的ListRoleDto转换为core包下的ListRoleDto
     *
     * @param uapListRoleDto UAP客户端的ListRoleDto
     * @return core包下的ListRoleDto
     */
    public ListRoleDto fromUapListRoleDto(com.iflytek.sec.uap.client.core.dto.role.ListRoleDto uapListRoleDto) {
        if (uapListRoleDto == null) {
            return null;
        }

        ListRoleDto listRoleDto = new ListRoleDto();
        // 使用BeanUtils复制属性（包括继承自PageQueryDto的pageNum和pageSize）
        BeanUtils.copyProperties(uapListRoleDto, listRoleDto);

        return listRoleDto;
    }
}
