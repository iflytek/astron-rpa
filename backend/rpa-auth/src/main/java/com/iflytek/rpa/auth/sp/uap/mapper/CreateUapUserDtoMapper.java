package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.CreateUapUserDto;
import com.iflytek.rpa.auth.core.entity.CreateUserDto;
import com.iflytek.rpa.auth.core.entity.UapExtendPropertyDto;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * CreateUapUserDto映射器
 * 用于将core包下的CreateUapUserDto转换为UAP客户端的CreateUapUserDto
 *
 * @author xqcao2
 */
@Component
public class CreateUapUserDtoMapper {

    /**
     * 将core包下的CreateUapUserDto转换为UAP客户端的CreateUapUserDto
     *
     * @param createUapUserDto core包下的CreateUapUserDto
     * @return UAP客户端的CreateUapUserDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.CreateUapUserDto toUapCreateUapUserDto(
            CreateUapUserDto createUapUserDto) {
        if (createUapUserDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.CreateUapUserDto uapCreateUapUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.CreateUapUserDto();

        // 转换user属性
        if (createUapUserDto.getUser() != null) {
            com.iflytek.sec.uap.client.core.dto.user.CreateUserDto uapCreateUserDto =
                    toUapCreateUserDto(createUapUserDto.getUser());
            uapCreateUapUserDto.setUser(uapCreateUserDto);
        }

        // 转换extands属性
        if (createUapUserDto.getExtands() != null
                && !createUapUserDto.getExtands().isEmpty()) {
            List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto> uapExtands =
                    createUapUserDto.getExtands().stream()
                            .map(this::toUapExtendPropertyDto)
                            .collect(Collectors.toList());
            uapCreateUapUserDto.setExtands(uapExtands);
        }

        return uapCreateUapUserDto;
    }

    /**
     * 将UAP客户端的CreateUapUserDto转换为core包下的CreateUapUserDto
     *
     * @param uapCreateUapUserDto UAP客户端的CreateUapUserDto
     * @return core包下的CreateUapUserDto
     */
    public CreateUapUserDto fromUapCreateUapUserDto(
            com.iflytek.sec.uap.client.core.dto.user.CreateUapUserDto uapCreateUapUserDto) {
        if (uapCreateUapUserDto == null) {
            return null;
        }

        CreateUapUserDto createUapUserDto = new CreateUapUserDto();

        // 转换user属性
        if (uapCreateUapUserDto.getUser() != null) {
            CreateUserDto createUserDto = fromUapCreateUserDto(uapCreateUapUserDto.getUser());
            createUapUserDto.setUser(createUserDto);
        }

        // 转换extands属性
        if (uapCreateUapUserDto.getExtands() != null
                && !uapCreateUapUserDto.getExtands().isEmpty()) {
            List<UapExtendPropertyDto> extands = uapCreateUapUserDto.getExtands().stream()
                    .map(this::fromUapExtendPropertyDto)
                    .collect(Collectors.toList());
            createUapUserDto.setExtands(extands);
        }

        return createUapUserDto;
    }

    /**
     * 将core包下的CreateUserDto转换为UAP客户端的CreateUserDto
     */
    private com.iflytek.sec.uap.client.core.dto.user.CreateUserDto toUapCreateUserDto(CreateUserDto createUserDto) {
        if (createUserDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.CreateUserDto uapCreateUserDto =
                new com.iflytek.sec.uap.client.core.dto.user.CreateUserDto();
        BeanUtils.copyProperties(createUserDto, uapCreateUserDto);
        return uapCreateUserDto;
    }

    /**
     * 将UAP客户端的CreateUserDto转换为core包下的CreateUserDto
     */
    private CreateUserDto fromUapCreateUserDto(
            com.iflytek.sec.uap.client.core.dto.user.CreateUserDto uapCreateUserDto) {
        if (uapCreateUserDto == null) {
            return null;
        }

        CreateUserDto createUserDto = new CreateUserDto();
        BeanUtils.copyProperties(uapCreateUserDto, createUserDto);
        return createUserDto;
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
