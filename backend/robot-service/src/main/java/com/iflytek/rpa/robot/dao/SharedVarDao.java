package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVar;
import com.iflytek.rpa.robot.entity.vo.SharedSubVarVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 共享变量DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarDao extends BaseMapper<SharedVar> {

    /**
     * 根据共享变量ID获取子变量列表
     *
     * @param sharedVarIds 共享变量ID列表
     * @return 子变量列表
     */
    List<SharedSubVarVo> getSubVarListBySharedVarIds(@Param("sharedVarIds") List<Long> sharedVarIds);

    /**
     * 查询用户可用的共享变量（usage_type='all'和dept_id匹配的）
     *
     * @param tenantId     租户ID
     * @param deptId       部门ID
     * @param selectVarIds
     * @return 共享变量列表
     */
    List<SharedVar> getAvailableSharedVars(
            @Param("tenantId") String tenantId,
            @Param("deptId") String deptId,
            @Param("selectVarIds") List<String> selectVarIds);

    List<SharedVar> getAvailableByIds(@Param("ids") List<Long> ids);
}
