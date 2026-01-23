package com.iflytek.rpa.base.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.vo.CAtomMetaNewVo;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;

/**
 * 新原子能力Service
 */
public interface CAtomMetaNewService {

    /**
     * 获取原子能力树
     */
    AppResponse<String> getAtomTree() throws JsonProcessingException;

    /**
     * 根据key列表获取原子能力d
     */
    AppResponse<List<CAtomMetaNewVo>> getListByKeys(List<String> keys);

    /**
     * 获取全量原子能力J
     */
    List<CAtomMetaNewVo> getAll();

    /**
     * 全量更新原子能力
     * 如果有则进行更新，没有则进行插入，如果发现新的数据库不存在则删除该记录
     */
    AppResponse<String> allUpdate(List<CAtomMetaNewVo> atomMetaNewVoList);

    AppResponse<String> updateAtomTree(String treeContent);
}
