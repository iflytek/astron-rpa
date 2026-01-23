package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.GetUserDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * GetUserDto 映射器
 * 用于在 core 的 GetUserDto 与 UAP 客户端的 GetUserDto 之间转换
 *
 * 两边结构完全一致，仅包名不同
 */
@Component
public class GetUserDtoMapper {

    /**
     * 将 core 包下的 GetUserDto 转换为 UAP 客户端的 GetUserDto
     *
     * @param getUserDto core 的 GetUserDto
     * @return UAP 客户端的 GetUserDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.GetUserDto toUapGetUserDto(GetUserDto getUserDto) {
        if (getUserDto == null) {
            return null;
        }
        com.iflytek.sec.uap.client.core.dto.user.GetUserDto uapGetUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.GetUserDto();
        BeanUtils.copyProperties(getUserDto, uapGetUserDto);
        return uapGetUserDto;
    }

    /**
     * 将 UAP 客户端的 GetUserDto 转换为 core 包下的 GetUserDto
     *
     * @param uapGetUserDto UAP 客户端的 GetUserDto
     * @return core 的 GetUserDto
     */
    public GetUserDto fromUapGetUserDto(com.iflytek.sec.uap.client.core.dto.user.GetUserDto uapGetUserDto) {
        if (uapGetUserDto == null) {
            return null;
        }
        GetUserDto getUserDto = new GetUserDto();
        BeanUtils.copyProperties(uapGetUserDto, getUserDto);
        return getUserDto;
    }
}
