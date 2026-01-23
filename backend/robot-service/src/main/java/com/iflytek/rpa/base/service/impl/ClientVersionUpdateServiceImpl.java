package com.iflytek.rpa.base.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.ClientVersionUpdateDao;
import com.iflytek.rpa.base.entity.ClientUpdateVersion;
import com.iflytek.rpa.base.entity.dto.ClientVersionCheckDto;
import com.iflytek.rpa.base.entity.dto.ClientVersionUpdateDto;
import com.iflytek.rpa.base.entity.vo.ClientVersionCheckVo;
import com.iflytek.rpa.base.entity.vo.ClientVersionUpdateVo;
import com.iflytek.rpa.base.service.ClientVersionUpdateService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 客户端版本更新服务
 */
@Service
public class ClientVersionUpdateServiceImpl extends ServiceImpl<ClientVersionUpdateDao, ClientUpdateVersion>
        implements ClientVersionUpdateService {
    @Autowired
    private IdWorker idWorker;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<ClientVersionUpdateVo> save(ClientVersionUpdateDto dto) throws Exception {
        // 转换版本号
        Integer versionNum = getVersionNum(dto.getVersion());
        // 检查版本号是否已存在
        ClientUpdateVersion existing = baseMapper.getByVersionNum(versionNum);
        if (existing != null && existing.getDeleted() == 0) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "版本号已存在");
        }
        // 创建实体对象
        ClientUpdateVersion entity = new ClientUpdateVersion();
        long id = idWorker.nextId();
        entity.setId(id);
        entity.setVersion(dto.getVersion());
        entity.setVersionNum(versionNum);
        entity.setDownloadUrl(dto.getDownloadUrl());
        entity.setUpdateInfo(dto.getUpdateInfo());
        entity.setOs(dto.getOs());
        entity.setArch(dto.getArch());
        entity.setDeleted(0);
        // 插入数据库
        int result = baseMapper.insert(entity);
        if (result <= 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "新增失败");
        }
        // 转换为VO返回
        ClientVersionUpdateVo vo = new ClientVersionUpdateVo();
        BeanUtils.copyProperties(entity, vo);
        return AppResponse.success(vo);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<ClientVersionUpdateVo> update(ClientVersionUpdateDto dto) throws Exception {
        if (dto.getId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "ID不能为空");
        }
        // 查询原记录
        ClientUpdateVersion existing = baseMapper.selectById(dto.getId());
        if (existing == null || existing.getDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "记录不存在");
        }
        String version = dto.getVersion();
        Integer versionNum = getVersionNum(version);
        // 如果版本号有变化，需要检查新版本号是否已存在
        if (!existing.getVersion().equals(dto.getVersion())) {
            ClientUpdateVersion versionCheck = baseMapper.getByVersionNum(versionNum);
            if (versionCheck != null
                    && versionCheck.getDeleted() == 0
                    && !versionCheck.getId().equals(dto.getId())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "版本号已存在");
            }
        }
        // 更新实体对象
        ClientUpdateVersion entity = new ClientUpdateVersion();
        entity.setId(dto.getId());
        entity.setVersion(dto.getVersion());
        entity.setVersionNum(versionNum);
        entity.setDownloadUrl(dto.getDownloadUrl());
        entity.setUpdateInfo(dto.getUpdateInfo());
        // 更新数据库
        int result = baseMapper.updateById(entity);
        if (result <= 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "更新失败");
        }
        // 查询更新后的记录
        ClientUpdateVersion updated = baseMapper.selectById(dto.getId());
        // 转换为VO返回
        ClientVersionUpdateVo vo = new ClientVersionUpdateVo();
        BeanUtils.copyProperties(updated, vo);
        return AppResponse.success(vo);
    }

    @Override
    public AppResponse<ClientVersionCheckVo> checkVersion(ClientVersionCheckDto dto) throws Exception {
        // 查询最新版本
        ClientUpdateVersion latestVersion = baseMapper.getLatestVersion(dto.getOs(), dto.getArch());
        // 构建返回VO
        ClientVersionCheckVo vo = new ClientVersionCheckVo();
        // 如果没有最新版本，返回不需要更新
        if (latestVersion == null) {
            vo.setNeedUpdate(0);
            vo.setVersion(null);
            vo.setUpdateInfo(null);
            vo.setDownloadUrl(null);
            return AppResponse.success(vo);
        }
        // 比较当前版本和最新版本
        String currentVersion = dto.getVersion();
        String latestVersionStr = latestVersion.getVersion();
        // 如果版本相同，不需要更新
        if (currentVersion.equals(latestVersionStr)) {
            vo.setNeedUpdate(0);
            vo.setVersion(latestVersionStr);
            vo.setOs(null);
            vo.setArch(null);
            vo.setUpdateInfo(null);
            vo.setDownloadUrl(null);
        } else {
            // 版本不同，需要更新
            vo.setNeedUpdate(1);
            vo.setVersion(latestVersionStr);
            vo.setOs(latestVersion.getOs());
            vo.setArch(latestVersion.getArch());
            vo.setUpdateInfo(latestVersion.getUpdateInfo());
            vo.setDownloadUrl(latestVersion.getDownloadUrl());
        }
        return AppResponse.success(vo);
    }

    @Override
    public String checkVersionSimple(String os, String arch, String version) throws Exception {
        // 查询全局最新版本
        ClientUpdateVersion latestVersion = baseMapper.getLatestVersion(os, arch);
        // 如果没有最新版本，返回null（表示已是最新）
        if (latestVersion == null) {
            return null;
        }
        // 比较当前版本和最新版本
        String latestVersionStr = latestVersion.getVersion();
        // 如果版本相同，返回null（表示已是最新）
        if (version.equals(latestVersionStr)) {
            return null;
        }
        // 版本不同，返回最新版本的下载URL
        return latestVersion.getDownloadUrl();
    }

    /**
     * 将版本号字符串转换为版本数字
     *
     * @param version 版本号字符串，如 "1.2.3"
     * @return 版本数字
     */
    private Integer getVersionNum(String version) {
        if (StringUtils.isBlank(version)) {
            throw new IllegalArgumentException("版本号缺失");
        }
        String[] versionSplit = version.split("\\.");
        int splitSize = versionSplit.length;
        // 确保版本号最多有3部分（major, minor, patch）
        if (splitSize > 3) {
            throw new IllegalArgumentException("版本号格式不正确");
        }
        // 初始化 major, minor, patch
        int major = 0;
        int minor = 0;
        int patch = 0;
        // 解析 major
        if (splitSize >= 1) {
            major = Integer.parseInt(versionSplit[0]);
        }
        // 解析 minor
        if (splitSize >= 2) {
            minor = Integer.parseInt(versionSplit[1]);
        }
        // 解析 patch
        if (splitSize >= 3) {
            patch = Integer.parseInt(versionSplit[2]);
        }
        // 计算转换后的版本号
        return major * 1_000_000 + minor * 1_000 + patch;
    }
}
