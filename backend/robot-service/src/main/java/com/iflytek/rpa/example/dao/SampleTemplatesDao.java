package com.iflytek.rpa.example.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.example.entity.SampleTemplates;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 系统预定义的模板库(SampleTemplates)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface SampleTemplatesDao extends BaseMapper<SampleTemplates> {

    /**
     * 批量插入
     *
     * @param entities 实体列表
     * @return 插入行数
     */
    int insertBatch(@Param("entities") List<SampleTemplates> entities);

    /**
     * 批量更新
     *
     * @param entities 实体列表
     * @return 更新行数
     */
    int updateBatch(@Param("entities") List<SampleTemplates> entities);

    /**
     * 根据样例ID查询
     *
     * @param sampleId 样例ID
     * @return 模板实体
     */
    SampleTemplates selectBySampleId(@Param("sampleId") String sampleId);

    /**
     * 根据类型查询有效模板
     *
     * @param type 模板类型
     * @return 模板列表
     */
    List<SampleTemplates> selectActiveByType(@Param("type") String type);

    @Select("select version from sample_templates where is_deleted = 0 and is_active = 1")
    List<String> getVersionList();

    @Select("select * from sample_templates where is_deleted = 0 and is_active = 1 and version = #{version}")
    List<SampleTemplates> getSamples(@Param("version") String version);
}
