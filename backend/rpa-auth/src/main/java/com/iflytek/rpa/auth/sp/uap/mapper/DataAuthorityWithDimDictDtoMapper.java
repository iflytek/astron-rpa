package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * DataAuthorityWithDimDictDto映射器
 * 用于将UAP客户端的DataAuthorityWithDimDictDto转换为core包下的DataAuthorityWithDimDictDto
 *
 * @author xqcao2
 */
@Component
public class DataAuthorityWithDimDictDtoMapper {

    /**
     * 将UAP客户端的DataAuthorityWithDimDictDto转换为核心实体DataAuthorityWithDimDictDto
     *
     * @param uapDataAuthorityWithDimDictDto UAP客户端的DataAuthorityWithDimDictDto
     * @return core包下的DataAuthorityWithDimDictDto
     */
    public DataAuthorityWithDimDictDto fromUapDataAuthorityWithDimDictDto(
            com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto
                    uapDataAuthorityWithDimDictDto) {
        if (uapDataAuthorityWithDimDictDto == null) {
            return null;
        }

        DataAuthorityWithDimDictDto dataAuthorityWithDimDictDto = new DataAuthorityWithDimDictDto();
        // 使用BeanUtils复制基本属性
        BeanUtils.copyProperties(uapDataAuthorityWithDimDictDto, dataAuthorityWithDimDictDto);

        // 递归转换dimList
        if (uapDataAuthorityWithDimDictDto.getDimList() != null
                && !uapDataAuthorityWithDimDictDto.getDimList().isEmpty()) {
            List<DataAuthorityWithDimDictDto.Dim> dimList = new ArrayList<>();
            for (com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto.Dim uapDim :
                    uapDataAuthorityWithDimDictDto.getDimList()) {
                DataAuthorityWithDimDictDto.Dim dim = fromUapDim(uapDim);
                if (dim != null) {
                    dimList.add(dim);
                }
            }
            dataAuthorityWithDimDictDto.setDimList(dimList);
        } else {
            dataAuthorityWithDimDictDto.setDimList(new ArrayList<>());
        }

        return dataAuthorityWithDimDictDto;
    }

    /**
     * 将UAP的Dim转换为core的Dim
     */
    private DataAuthorityWithDimDictDto.Dim fromUapDim(
            com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto.Dim uapDim) {
        if (uapDim == null) {
            return null;
        }

        DataAuthorityWithDimDictDto.Dim dim = new DataAuthorityWithDimDictDto.Dim();
        dim.setDimId(uapDim.getDimId());
        dim.setDimName(uapDim.getDimName());

        // 递归转换dimDictList
        if (uapDim.getDimDictList() != null && !uapDim.getDimDictList().isEmpty()) {
            List<DataAuthorityWithDimDictDto.DimDict> dimDictList = new ArrayList<>();
            for (com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto.DimDict uapDimDict :
                    uapDim.getDimDictList()) {
                DataAuthorityWithDimDictDto.DimDict dimDict = fromUapDimDict(uapDimDict);
                if (dimDict != null) {
                    dimDictList.add(dimDict);
                }
            }
            dim.setDimDictList(dimDictList);
        } else {
            dim.setDimDictList(new ArrayList<>());
        }

        return dim;
    }

    /**
     * 将UAP的DimDict转换为core的DimDict
     */
    private DataAuthorityWithDimDictDto.DimDict fromUapDimDict(
            com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto.DimDict uapDimDict) {
        if (uapDimDict == null) {
            return null;
        }

        DataAuthorityWithDimDictDto.DimDict dimDict = new DataAuthorityWithDimDictDto.DimDict();
        dimDict.setDictId(uapDimDict.getDictId());
        dimDict.setDictName(uapDimDict.getDictName());
        dimDict.setDictValue(uapDimDict.getDictValue());

        return dimDict;
    }

    /**
     * 批量将UAP客户端的DataAuthorityWithDimDictDto列表转换为核心实体DataAuthorityWithDimDictDto列表
     *
     * @param uapDataAuthorityWithDimDictDtos UAP客户端的DataAuthorityWithDimDictDto列表
     * @return core包下的DataAuthorityWithDimDictDto列表
     */
    public List<DataAuthorityWithDimDictDto> fromUapDataAuthorityWithDimDictDtos(
            List<com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto>
                    uapDataAuthorityWithDimDictDtos) {
        if (uapDataAuthorityWithDimDictDtos == null || uapDataAuthorityWithDimDictDtos.isEmpty()) {
            return Collections.emptyList();
        }

        return uapDataAuthorityWithDimDictDtos.stream()
                .map(this::fromUapDataAuthorityWithDimDictDto)
                .filter(dataAuthorityWithDimDictDto -> dataAuthorityWithDimDictDto != null)
                .collect(Collectors.toList());
    }
}
