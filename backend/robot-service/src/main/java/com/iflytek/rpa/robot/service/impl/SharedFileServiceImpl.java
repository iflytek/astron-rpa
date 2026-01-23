package com.iflytek.rpa.robot.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.CollectionUtils;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.Authority;
import com.iflytek.rpa.common.feign.entity.Org;
import com.iflytek.rpa.common.feign.entity.Role;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.robot.dao.SharedFileDao;
import com.iflytek.rpa.robot.entity.SharedFile;
import com.iflytek.rpa.robot.entity.SharedFileTag;
import com.iflytek.rpa.robot.entity.dto.SharedFileDto;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import com.iflytek.rpa.robot.entity.enums.FileIndexStatus;
import com.iflytek.rpa.robot.entity.vo.SharedFilePageVo;
import com.iflytek.rpa.robot.service.SharedFileService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 共享文件服务实现类
 *
 * @author yfchen40
 * @since 2025-07-21
 */
@Slf4j
@Service
public class SharedFileServiceImpl extends ServiceImpl<SharedFileDao, SharedFile> implements SharedFileService {
    @Autowired
    private IdWorker idWorker;

    @Autowired
    private SharedFileDao sharedFileDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    //    @Transactional(readOnly = true)
    public AppResponse<IPage<SharedFilePageVo>> getSharedFilePageList(SharedFilePageDto queryDto) {
        // 创建分页对象
        IPage<SharedFile> page = new Page<>(queryDto.getPageNo(), queryDto.getPageSize());
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        // 使用 XML 分页查询方式
        IPage<SharedFile> sharedFilePage = baseMapper.selectSharedFilePageList(page, queryDto, tenantId);

        if (sharedFilePage.getSize() == 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "未查询到符合条件的文件");
        }

        // 转换为 VO 对象
        IPage<SharedFilePageVo> resultPage = sharedFilePage.convert(sharedFile -> {
            SharedFilePageVo vo = new SharedFilePageVo();
            BeanUtils.copyProperties(sharedFile, vo);
            // 设置额外的 VO 字段
            vo.setFileId(sharedFile.getFileId());
            if (StringUtils.isNotBlank(sharedFile.getTags())) {
                // 设置标签ID列表
                List<Long> tagIds = Arrays.stream(sharedFile.getTags().split(","))
                        .map(Long::valueOf)
                        .collect(Collectors.toList());

                // 查询并设置标签名称列表
                List<SharedFileTag> tags = baseMapper.selectTagsByIds(tagIds, tenantId);
                List<String> tagNames =
                        tags.stream().map(SharedFileTag::getTagName).collect(Collectors.toList());
                vo.setTagsNames(tagNames);
            }
            if (sharedFile.getTags() != null && !sharedFile.getTags().isEmpty()) {
                vo.setTags(Arrays.asList(sharedFile.getTags().split(",")));
            } else {
                vo.setTags(null);
            }
            vo.setFilePath("/api/resource/file/download?fileId=" + sharedFile.getFileId());
            // 填充creatorName, phone(账号), deptId, deptName
            String creatorId = sharedFile.getCreatorId();
            AppResponse<String> deptIdRes = rpaAuthFeign.getDeptIdByUserId(creatorId, tenantId);
            if (!deptIdRes.ok()) throw new ServiceException("rpa-auth 服务位响应");
            String deptId = deptIdRes.getData();

            AppResponse<String> realNameResp = rpaAuthFeign.getNameById(sharedFile.getCreatorId());
            if (realNameResp == null || realNameResp.getData() == null) {
                throw new ServiceException("用户名获取失败");
            }
            String creatorName = realNameResp.getData();
            vo.setCreatorName(creatorName);

            AppResponse<User> userResp = rpaAuthFeign.getUserInfoById(creatorId);
            if (userResp == null || userResp.getData() == null) {
                throw new ServiceException("获取用户信息获取失败");
            }
            User loginUser = userResp.getData();
            vo.setPhone(loginUser.getPhone());
            vo.setDeptId(deptId);
            AppResponse<Org> deptInfoByDeptIdRes = rpaAuthFeign.getDeptInfoByDeptId(deptId);
            if (!deptInfoByDeptIdRes.ok()) throw new ServiceException("rpa-auth 服务未响应");
            Org dept = deptInfoByDeptIdRes.getData();
            if (dept != null) {
                vo.setDeptName(dept.getName());
            }
            return vo;
        });

        // 返回成功响应
        return AppResponse.success(resultPage);
    }

    // 判断用户有无文件处理权限
    private boolean hasFileManagementPermission(HttpServletRequest request) throws NoLoginException {
        // 如果是租户管理员，直接返回true
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        // 通过Feign调用rpa-auth服务获取租户用户类型
        AppResponse<Integer> tenantUserTypeResponse = rpaAuthFeign.getTenantUserType(userId, tenantId);
        Integer tenantUserType = null;
        if (tenantUserTypeResponse != null && tenantUserTypeResponse.ok() && tenantUserTypeResponse.getData() != null) {
            tenantUserType = tenantUserTypeResponse.getData();
        }
        if (tenantUserType != null && tenantUserType == 1) {
            return true;
        }
        AppResponse<List<Role>> roleResponse = rpaAuthFeign.getUserRoleList();
        if (roleResponse == null || roleResponse.getData() == null) {
            throw new ServiceException("用户角色信息获取失败");
        }
        List<Role> roleList = roleResponse.getData();
        List<Authority> authList = roleList.stream()
                .map(Role::getId)
                .flatMap(roleId -> {
                    AppResponse<List<Authority>> listAppResponse =
                            rpaAuthFeign.queryAuthorityListByRoleId(tenantId, roleId);
                    if (!listAppResponse.ok()) throw new ServiceException("rpa-auth服务响应异常");
                    List<Authority> authorities = listAppResponse.getData();
                    return authorities != null ? authorities.stream() : Stream.empty();
                })
                .collect(Collectors.toList());
        return authList.stream().anyMatch(auth -> "文件管理".equals(auth.getName()));
    }

    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> addSharedFileInfo(HttpServletRequest request, SharedFileDto dto) throws NoLoginException {
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> deptIdRes = rpaAuthFeign.getDeptIdByUserId(userId, tenantId);
        if (!deptIdRes.ok()) throw new ServiceException("rpa-auth 服务未响应");
        String deptId = deptIdRes.getData();
        String fileId = dto.getFileId();
        String fileName = dto.getFileName();

        SharedFile file = baseMapper.selectFileByName(fileName, tenantId);
        if (file != null) {
            return AppResponse.error("请勿上传同名文件");
        }
        // 检查标签是否存在并去重
        List<Long> uniqueTagIds = new ArrayList<>();
        if (CollectionUtils.isNotEmpty(dto.getTags())) {
            // 去重
            uniqueTagIds = dto.getTags().stream().distinct().collect(Collectors.toList());
            // 查询这些标签是否都存在
            List<SharedFileTag> existingTags = baseMapper.selectTagsByIds(uniqueTagIds, tenantId);
            List<Long> existingTagIds =
                    existingTags.stream().map(SharedFileTag::getTagId).collect(Collectors.toList());
            // 检查是否有不存在的标签
            List<Long> nonExistingTagIds = uniqueTagIds.stream()
                    .filter(tagId -> !existingTagIds.contains(tagId))
                    .collect(Collectors.toList());

            if (CollectionUtils.isNotEmpty(nonExistingTagIds)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签不存在: " + nonExistingTagIds);
            }
        } else {
            uniqueTagIds = new ArrayList<>();
        }
        String tagsString = uniqueTagIds.stream().map(String::valueOf).collect(Collectors.joining(","));
        // 构造sharedFile对象
        SharedFile sharedFile = new SharedFile();
        sharedFile.setId(idWorker.nextId());
        sharedFile.setFileId(fileId);
        sharedFile.setFileName(fileName);
        sharedFile.setDeptId(deptId);
        sharedFile.setFileType(dto.getFileType());
        sharedFile.setFileIndexStatus(FileIndexStatus.START.getValue());
        AppResponse<String> res = rpaAuthFeign.getTenantId();
        if (res == null || res.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String nowTenantId = resp.getData();
        sharedFile.setTenantId(nowTenantId);
        sharedFile.setTags(tagsString);
        sharedFile.setUpdaterId(userId);
        sharedFile.setUpdateTime(new Date());
        sharedFile.setCreatorId(userId);
        sharedFile.setCreateTime(new Date());
        sharedFile.setDeleted(0);
        this.save(sharedFile);
        return AppResponse.success("新增成功");
    }
}
