package com.iflytek.rpa.auth.sp.casdoor.dao;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.auth.core.entity.GetMarketUserListDto;
import com.iflytek.rpa.auth.core.entity.MarketDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 市场用户数据访问接口（访问RPA业务数据库）
 * 注意：此接口的方法访问rpa数据库的app_market_user表
 *
 * @author Auto Generated
 * @create 2025/12/11
 */
@Mapper
public interface MarketUserDao {

    /**
     * 获取市场用户列表（分页）- 仅查询rpa数据库的app_market_user表
     *
     * @param page 分页对象
     * @param dto 查询条件
     * @return 市场用户分页列表（仅包含市场用户基本信息，不包含用户详细信息）
     */
    IPage<MarketDto> getMarketUserListFromRpa(
            IPage<MarketDto> page, @Param("dto") GetMarketUserListDto dto);

    /**
     * 获取市场下已存在的用户ID列表
     *
     * @param marketId 市场ID
     * @return 用户ID列表
     */
    List<String> getExistingUserIdsByMarketId(@Param("marketId") String marketId);
}

