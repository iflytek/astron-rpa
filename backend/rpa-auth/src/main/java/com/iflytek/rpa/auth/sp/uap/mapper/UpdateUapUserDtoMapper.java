package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.UapExtendPropertyDto;
import com.iflytek.rpa.auth.core.entity.UpdateUapUserDto;
import com.iflytek.rpa.auth.core.entity.UpdateUserDto;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * UpdateUapUserDto映射器
 * 用于将core包下的UpdateUapUserDto转换为UAP客户端的UpdateUapUserDto
 *
 * @author xqcao2
 */
@Component
public class UpdateUapUserDtoMapper {

    /**
     * 将core包下的UpdateUapUserDto转换为UAP客户端的UpdateUapUserDto
     *
     * @param updateUapUserDto core包下的UpdateUapUserDto
     * @return UAP客户端的UpdateUapUserDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.UpdateUapUserDto toUapUpdateUapUserDto(
            UpdateUapUserDto updateUapUserDto) {
        if (updateUapUserDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.UpdateUapUserDto uapUpdateUapUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.UpdateUapUserDto();

        // 转换user属性
        if (updateUapUserDto.getUser() != null) {
            com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto uapUpdateUserDto =
                    toUapUpdateUserDto(updateUapUserDto.getUser());
            uapUpdateUapUserDto.setUser(uapUpdateUserDto);
        }

        // 转换extands属性
        if (updateUapUserDto.getExtands() != null
                && !updateUapUserDto.getExtands().isEmpty()) {
            List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto> uapExtands =
                    updateUapUserDto.getExtands().stream()
                            .map(this::toUapExtendPropertyDto)
                            .collect(Collectors.toList());
            uapUpdateUapUserDto.setExtands(uapExtands);
        }

        return uapUpdateUapUserDto;
    }

    /**
     * 将UAP客户端的UpdateUapUserDto转换为core包下的UpdateUapUserDto
     *
     * @param uapUpdateUapUserDto UAP客户端的UpdateUapUserDto
     * @return core包下的UpdateUapUserDto
     */
    public UpdateUapUserDto fromUapUpdateUapUserDto(
            com.iflytek.sec.uap.client.core.dto.user.UpdateUapUserDto uapUpdateUapUserDto) {
        if (uapUpdateUapUserDto == null) {
            return null;
        }

        UpdateUapUserDto updateUapUserDto = new UpdateUapUserDto();

        // 转换user属性
        if (uapUpdateUapUserDto.getUser() != null) {
            UpdateUserDto updateUserDto = fromUapUpdateUserDto(uapUpdateUapUserDto.getUser());
            updateUapUserDto.setUser(updateUserDto);
        }

        // 转换extands属性
        if (uapUpdateUapUserDto.getExtands() != null
                && !uapUpdateUapUserDto.getExtands().isEmpty()) {
            List<UapExtendPropertyDto> extands = uapUpdateUapUserDto.getExtands().stream()
                    .map(this::fromUapExtendPropertyDto)
                    .collect(Collectors.toList());
            updateUapUserDto.setExtands(extands);
        }

        return updateUapUserDto;
    }

    /**
     * 将core包下的UpdateUserDto转换为UAP客户端的UpdateUserDto
     */
    private com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto toUapUpdateUserDto(UpdateUserDto updateUserDto) {
        if (updateUserDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto uapUpdateUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto();
        BeanUtils.copyProperties(updateUserDto, uapUpdateUserDto);
        return uapUpdateUserDto;
    }

    /**
     * 将UAP客户端的UpdateUserDto转换为core包下的UpdateUserDto
     */
    private UpdateUserDto fromUapUpdateUserDto(
            com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto uapUpdateUserDto) {
        if (uapUpdateUserDto == null) {
            return null;
        }

        UpdateUserDto updateUserDto = new UpdateUserDto();
        BeanUtils.copyProperties(uapUpdateUserDto, updateUserDto);
        return updateUserDto;
    }

    /**
     * 将core包下的UapExtendPropertyDto转换为UAP客户端的UapExtendPropertyDto
     */
    private com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto toUapExtendPropertyDto(
            UapExtendPropertyDto uapExtendPropertyDto) {
        if (uapExtendPropertyDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto uapExtendProperty =
                new com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto();
        BeanUtils.copyProperties(uapExtendPropertyDto, uapExtendProperty);
        return uapExtendProperty;
    }

    /**
     * 将UAP客户端的UapExtendPropertyDto转换为core包下的UapExtendPropertyDto
     */
    private UapExtendPropertyDto fromUapExtendPropertyDto(
            com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto uapExtendPropertyDto) {
        if (uapExtendPropertyDto == null) {
            return null;
        }

        UapExtendPropertyDto uapExtendProperty = new UapExtendPropertyDto();
        BeanUtils.copyProperties(uapExtendPropertyDto, uapExtendProperty);
        return uapExtendProperty;
    }
}
