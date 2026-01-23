package com.iflytek.rpa.base.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.dto.CAtomMetaNewListDto;
import com.iflytek.rpa.base.entity.vo.CAtomMetaNewVo;
import com.iflytek.rpa.base.service.CAtomMetaNewService;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 新原子能力接口
 */
@RestController
@RequestMapping("/atom-new")
public class CAtomMetaNewController {

    @Autowired
    private CAtomMetaNewService cAtomMetaNewService;

    /**
     * 获取原子能力树
     */
    @PostMapping("/tree")
    public AppResponse<String> getAtomTree() throws JsonProcessingException {
        return cAtomMetaNewService.getAtomTree();
    }

    /**
     * 更新原子能力树
     */
    @PostMapping("/update-tree")
    public AppResponse<String> updateAtomTree(@RequestBody String treeContent) {
        return cAtomMetaNewService.updateAtomTree(treeContent);
    }

    /**
     * 根据key列表获取原子能力
     */
    @PostMapping("/list")
    public AppResponse<List<CAtomMetaNewVo>> getListByKeys(@Valid @RequestBody CAtomMetaNewListDto dto) {
        return cAtomMetaNewService.getListByKeys(dto.getKeys());
    }

    /**
     * 获取全量原子能力
     */
    @PostMapping("/all")
    public List<CAtomMetaNewVo> getAll() {
        return cAtomMetaNewService.getAll();
    }

    /**
     * 全量更新原子能力
     * 如果有则进行更新，没有则进行插入，如果发现新的数据库不存在则删除该记录
     */
    @PostMapping("/all-update")
    public AppResponse<String> allUpdate(@RequestBody List<CAtomMetaNewVo> atomMetaNewVoList) {
        return cAtomMetaNewService.allUpdate(atomMetaNewVoList);
    }
}
