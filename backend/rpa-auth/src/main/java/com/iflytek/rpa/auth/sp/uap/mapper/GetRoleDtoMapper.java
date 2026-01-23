package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.sec.uap.client.core.dto.role.GetRoleDto;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/25 16:32
 */
@Component
public class GetRoleDtoMapper {

    /**
     * 将核心实体GetRoleDto转换为UAP客户端的GetRoleDto
     */
    public GetRoleDto toUapGetRoleDto(com.iflytek.rpa.auth.core.entity.GetRoleDto source) {
        if (source == null) {
            return null;
        }

        GetRoleDto target = new GetRoleDto();

        // 使用BeanUtils复制属性（字段完全一致）
        BeanUtils.copyProperties(source, target);

        return target;
    }

    /**
     * 将UAP客户端的GetRoleDto转换为核心实体GetRoleDto
     */
    public com.iflytek.rpa.auth.core.entity.GetRoleDto toCoreGetRoleDto(GetRoleDto source) {
        if (source == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.GetRoleDto target = new com.iflytek.rpa.auth.core.entity.GetRoleDto();

        // 使用BeanUtils复制属性（字段完全一致）
        BeanUtils.copyProperties(source, target);

        return target;
    }

    /**
     * 批量将核心实体GetRoleDto列表转换为UAP客户端的GetRoleDto列表
     */
    public List<GetRoleDto> toUapGetRoleDtos(List<com.iflytek.rpa.auth.core.entity.GetRoleDto> sourceList) {
        if (sourceList == null) {
            return null;
        }

        return sourceList.stream().map(this::toUapGetRoleDto).collect(Collectors.toList());
    }

    /**
     * 批量将UAP客户端的GetRoleDto列表转换为核心实体GetRoleDto列表
     */
    public List<com.iflytek.rpa.auth.core.entity.GetRoleDto> toCoreGetRoleDtos(List<GetRoleDto> sourceList) {
        if (sourceList == null) {
            return null;
        }

        return sourceList.stream().map(this::toCoreGetRoleDto).collect(Collectors.toList());
    }
}
