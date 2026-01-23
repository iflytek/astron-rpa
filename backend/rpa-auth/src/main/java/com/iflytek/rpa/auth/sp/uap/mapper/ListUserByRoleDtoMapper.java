package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.ListUserByRoleDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * ListUserByRoleDto 映射器
 * 用于在 core 的 ListUserByRoleDto 与 UAP 客户端的 ListUserByRoleDto 之间转换
 *
 * 包括继承自 PageQueryDto 的分页字段
 */
@Component
public class ListUserByRoleDtoMapper {

    /**
     * 将 core 包下的 ListUserByRoleDto 转换为 UAP 客户端的 ListUserByRoleDto
     *
     * @param listUserByRoleDto core 的 ListUserByRoleDto
     * @return UAP 客户端的 ListUserByRoleDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto toUapListUserByRoleDto(
            ListUserByRoleDto listUserByRoleDto) {
        if (listUserByRoleDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto uapListUserByRoleDto =
                new com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto();
        // 复制属性，包括继承自 PageQueryDto 的 pageNum、pageSize
        BeanUtils.copyProperties(listUserByRoleDto, uapListUserByRoleDto);

        return uapListUserByRoleDto;
    }

    /**
     * 将 UAP 客户端的 ListUserByRoleDto 转换为 core 包下的 ListUserByRoleDto
     *
     * @param uapListUserByRoleDto UAP 客户端的 ListUserByRoleDto
     * @return core 的 ListUserByRoleDto
     */
    public ListUserByRoleDto fromUapListUserByRoleDto(
            com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto uapListUserByRoleDto) {
        if (uapListUserByRoleDto == null) {
            return null;
        }

        ListUserByRoleDto listUserByRoleDto = new ListUserByRoleDto();
        // 复制属性，包括继承自 PageQueryDto 的 pageNum、pageSize
        BeanUtils.copyProperties(uapListUserByRoleDto, listUserByRoleDto);

        return listUserByRoleDto;
    }
}
