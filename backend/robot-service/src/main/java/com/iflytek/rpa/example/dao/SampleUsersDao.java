package com.iflytek.rpa.example.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.example.entity.SampleUsers;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 用户从系统模板中注入的样例数据(SampleUsers)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface SampleUsersDao extends BaseMapper<SampleUsers> {

    /**
     * 批量插入
     *
     * @param entities 实体列表
     * @return 插入行数
     */
    int insertBatch(@Param("entities") List<SampleUsers> entities);

    /**
     * 批量更新
     *
     * @param entities 实体列表
     * @return 更新行数
     */
    int updateBatch(@Param("entities") List<SampleUsers> entities);

    /**
     * 根据用户ID和样例ID查询
     *
     * @param creatorId 用户ID
     * @param sampleId 样例ID
     * @return 用户样例实体
     */
    SampleUsers selectByCreatorIdAndSampleId(@Param("creatorId") String creatorId, @Param("sampleId") String sampleId);

    /**
     * 根据用户ID查询所有样例
     *
     * @param creatorId 用户ID
     * @return 用户样例列表
     */
    List<SampleUsers> selectByCreatorId(@Param("creatorId") String creatorId);
}
