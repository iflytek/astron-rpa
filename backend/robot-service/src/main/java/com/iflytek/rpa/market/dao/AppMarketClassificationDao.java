package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketClassification;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationManageVo;
import com.iflytek.rpa.market.entity.vo.AppMarketClassificationVo;
import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 应用市场分类表(AppMarketClassification)数据库访问层
 *
 * @author auto-generated
 */
@Mapper
public interface AppMarketClassificationDao extends BaseMapper<AppMarketClassification> {

    /**
     * 根据租户ID查询分类列表
     *
     * @param tenantId 租户ID
     * @return 分类列表
     */
    List<AppMarketClassificationVo> getClassificationListByTenantId(@Param("tenantId") String tenantId);

    /**
     * 分类管理-分类查询
     *
     * @param tenantId 租户ID
     * @param name 分类名
     * @param source 来源
     * @return 分类列表（按sort和创建时间排序）
     */
    List<AppMarketClassificationManageVo> getClassificationManageList(
            @Param("tenantId") String tenantId, @Param("name") String name, @Param("source") Integer source);

    List<Map> getCategoryReferenceCount();

    Integer insertDefaultClassification(@Param("tenantId") String tenantId);
}
