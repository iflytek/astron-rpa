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

    /**
     * 按ID批量查询共享变量，限定在指定租户范围内。
     *
     * <p>必须始终按调用方自身的 tenantId 过滤：若省略该过滤，客户端可通过构造任意自增ID枚举并取回
     * 其他租户的 usage_type='all' 共享变量（包含其明文子变量值），构成跨租户敏感信息泄露。
     *
     * @param tenantId 调用方租户ID
     * @param ids      共享变量ID列表
     * @return 属于该租户的共享变量列表
     */
    List<SharedVar> getAvailableByIds(@Param("tenantId") String tenantId, @Param("ids") List<Long> ids);
}
