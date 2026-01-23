package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVarUser;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 共享变量用户关系DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarUserDao extends BaseMapper<SharedVarUser> {

    /**
     * 批量插入用户关系
     *
     * @param entities 用户关系列表
     * @return 影响行数
     */
    Integer insertBatch(@Param("entities") List<SharedVarUser> entities);

    List<String> getAvailableSharedVarIds(String userId);
}
