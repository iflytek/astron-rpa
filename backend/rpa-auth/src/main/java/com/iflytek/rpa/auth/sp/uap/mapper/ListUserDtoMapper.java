package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.ListUserDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * ListUserDto映射器
 * 用于将core包下的ListUserDto转换为UAP客户端的ListUserDto
 *
 * @author xqcao2
 */
@Component
public class ListUserDtoMapper {

    /**
     * 将core包下的ListUserDto转换为UAP客户端的ListUserDto
     *
     * @param listUserDto core包下的ListUserDto
     * @return UAP客户端的ListUserDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.ListUserDto toUapListUserDto(ListUserDto listUserDto) {
        if (listUserDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.ListUserDto uapListUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.ListUserDto();
        // 使用BeanUtils复制属性（包括继承自PageQueryDto的pageNum和pageSize）
        BeanUtils.copyProperties(listUserDto, uapListUserDto);

        return uapListUserDto;
    }

    /**
     * 将UAP客户端的ListUserDto转换为core包下的ListUserDto
     *
     * @param uapListUserDto UAP客户端的ListUserDto
     * @return core包下的ListUserDto
     */
    public ListUserDto fromUapListUserDto(com.iflytek.sec.uap.client.core.dto.user.ListUserDto uapListUserDto) {
        if (uapListUserDto == null) {
            return null;
        }

        ListUserDto listUserDto = new ListUserDto();
        // 使用BeanUtils复制属性（包括继承自PageQueryDto的pageNum和pageSize）
        BeanUtils.copyProperties(uapListUserDto, listUserDto);

        return listUserDto;
    }
}
