package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CAtomMetaNew;
import com.iflytek.rpa.base.entity.vo.CAtomMetaNewVo;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 新原子能力DAO
 */
@Mapper
public interface CAtomMetaNewDao extends BaseMapper<CAtomMetaNew> {

    /**
     * 根据atomKey获取原子能力内容
     */
    String getAtomContentByKey(@Param("atomKey") String atomKey);

    /**
     * 根据key列表查询原子能力
     */
    List<CAtomMetaNewVo> getListByKeys(@Param("keys") List<String> keys);

    /**
     * 获取全部原子能力
     */
    List<CAtomMetaNewVo> getAll();

    /**
     * 根据atomKey删除记录
     */
    int deleteByAtomKey(@Param("atomKey") String atomKey);

    /**
     * 根据atomKey更新记录
     */
    int updateByAtomKey(
            @Param("atomKey") String atomKey, @Param("atomContent") String atomContent, @Param("sort") Integer sort);

    List<CAtomMetaNew> getAtomListByKeySet(Set<String> atomKeySet);
}
