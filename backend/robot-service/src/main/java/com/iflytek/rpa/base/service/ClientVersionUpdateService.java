package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.ClientVersionCheckDto;
import com.iflytek.rpa.base.entity.dto.ClientVersionUpdateDto;
import com.iflytek.rpa.base.entity.vo.ClientVersionCheckVo;
import com.iflytek.rpa.base.entity.vo.ClientVersionUpdateVo;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 客户端版本更新服务接口
 *
 * @author system
 * @since 2025-01-XX
 */
public interface ClientVersionUpdateService {

    /**
     * 新增版本信息
     *
     * @param dto 版本信息DTO
     * @return 操作结果
     */
    AppResponse<ClientVersionUpdateVo> save(ClientVersionUpdateDto dto) throws Exception;

    /**
     * 更新版本信息
     *
     * @param dto 版本信息DTO
     * @return 操作结果
     */
    AppResponse<ClientVersionUpdateVo> update(ClientVersionUpdateDto dto) throws Exception;

    /**
     * 检查客户端版本是否需要更新
     *
     * @param dto 版本检查DTO
     * @return 版本检查结果
     */
    AppResponse<ClientVersionCheckVo> checkVersion(ClientVersionCheckDto dto) throws Exception;

    /**
     * 检查客户端版本是否需要更新（简化版，仅根据版本号判断）
     *
     * @param version 当前版本号
     * @return 最新版本的下载URL，如果已是最新版本则返回null
     */
    String checkVersionSimple(String os, String arch, String version) throws Exception;
}
