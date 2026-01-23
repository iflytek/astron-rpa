package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVarKeyTenant;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 共享变量租户密钥DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarKeyTenantDao extends BaseMapper<SharedVarKeyTenant> {

    @Select("SELECT id from shared_var_key_tenant WHERE deleted = 0")
    List<String> getExistsTenantIds();
    /**
     * 批量插入租户密钥
     */
    void insertBatch(@Param("entities") List<SharedVarKeyTenant> entities);

    /**
     * 根据租户ID查询密钥
     *
     * @param tenantId 租户ID
     * @return 密钥实体
     */
    SharedVarKeyTenant selectByTenantId(@Param("tenantId") String tenantId);
}
