package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.SharedFile;
import com.iflytek.rpa.robot.entity.SharedFileTag;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SharedFileDao extends BaseMapper<SharedFile> {
    Integer isTenantAdmin(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    Integer deleteBatchSharedFile(@Param("ids") List<String> fileIds, @Param("tenantId") String tenantId);

    List<SharedFileTag> selectTags(String tenantId);

    Integer addTag(@Param("entity") SharedFileTag newTag);

    // 在 SharedFileDao 接口中添加
    Integer updateTagById(
            @Param("tagId") Long tagId,
            @Param("tagName") String tagName,
            @Param("updaterId") String updaterId,
            @Param("tenantId") String tenantId);

    List<SharedFile> selectFilesByTag(@Param("tagName") String tagName, @Param("tenantId") String tenantId);

    Integer updateFileTagById(@Param("fileId") String fileId, @Param("tags") String tags);

    Integer deletedTagById(@Param("tagId") Long tagId, @Param("tenantId") String tenantId);

    List<SharedFileTag> selectTagsByIds(@Param("tagIds") List<Long> tagIds, @Param("tenantId") String tenantId);

    IPage<SharedFile> selectSharedFilePageList(
            IPage<SharedFile> page, @Param("queryDto") SharedFilePageDto queryDto, @Param("tenantId") String tenantId);

    SharedFile selectFileByName(String fileName, String tenantId);

    void deleteByFileIds(List<String> fileIds);
}
