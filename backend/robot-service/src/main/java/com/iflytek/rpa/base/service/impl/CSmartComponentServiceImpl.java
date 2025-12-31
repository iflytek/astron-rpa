package com.iflytek.rpa.base.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.google.common.collect.Lists;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CSmartComponentDao;
import com.iflytek.rpa.base.entity.CSmartComponent;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CSmartComponentDto;
import com.iflytek.rpa.base.entity.vo.SmartComponentVo;
import com.iflytek.rpa.base.service.CSmartComponentService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.UserUtils;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.utils.IdWorker;
import com.mysql.cj.xdevapi.JsonArray;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;


@Service
public class CSmartComponentServiceImpl implements CSmartComponentService {

    @Resource
    private IdWorker idWorker;

    @Resource
    private CSmartComponentDao cSmartComponentDao;

    @Override
    public AppResponse<SmartComponentVo> save(CSmartComponentDto smartComponentDto) throws NoLoginException {
        String robotId = smartComponentDto.getRobotId();
        String smartId = smartComponentDto.getSmartId();
        String userId = UserUtils.nowUserId();

        CSmartComponent smartComponent = new CSmartComponent()
                .setSmartId(smartId)
                .setSmartType(smartComponentDto.getSmartType())
                .setRobotId(robotId)
                .setContent(JSON.toJSONString(smartComponentDto.getDetail()))
                .setUpdaterId(userId);

        // smartId不存在，则创建新的smartId
        if (StringUtils.isEmpty(smartId)) {
            smartId = String.valueOf(idWorker.nextId());
            smartComponent
                    .setCreatorId(userId)
                    .setSmartId(smartId)
                    .setRobotVersion(0);
            create(smartComponent);
            return AppResponse.success(new SmartComponentVo().setSmartId(smartId));
        }

        // smartId存在，则更新已有的智能组件
        int result = cSmartComponentDao.updateContent(smartComponent);
        if (result != 1) {
            throw new RuntimeException("Failed to update smart component");
        }

        return AppResponse.success(new SmartComponentVo().setSmartId(smartId));
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<SmartComponentVo> getBySmartId(BaseDto baseDto, String smartId) throws NoLoginException {
        String robotId = baseDto.getRobotId();
        Integer robotVersion = baseDto.getRobotVersion();
        CSmartComponent smartComponent = cSmartComponentDao.getBySmartId(smartId, robotId, robotVersion);
        if (smartComponent == null) {
            throw new RuntimeException("Smart component not found");
        }

        CSmartComponentDto.SmartDetail smartDetail = JSON.parseObject(smartComponent.getContent(), CSmartComponentDto.SmartDetail.class);

        SmartComponentVo smartComponentVo = new SmartComponentVo()
                .setRobotId(robotId)
                .setSmartId(smartId)
                .setSmartType(smartComponent.getSmartType())
                .setDetail(smartDetail);

        return AppResponse.success(smartComponentVo);
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<SmartComponentVo> getBySmartIdAndVersion(BaseDto baseDto, String smartId, Integer version) throws NoLoginException {
        String robotId = baseDto.getRobotId();
        Integer robotVersion = baseDto.getRobotVersion();
        CSmartComponent smartComponent = cSmartComponentDao.getBySmartId(smartId, robotId, robotVersion);
        if (smartComponent == null) {
            throw new RuntimeException("Smart component not found");
        }

        CSmartComponentDto.SmartDetail smartDetail = JSON.parseObject(smartComponent.getContent(), CSmartComponentDto.SmartDetail.class);

        // 过滤出指定版本的智能组件信息
        List<JSONObject> versionList = Optional.ofNullable(smartDetail.getVersionList())
                .orElse(Collections.emptyList());

        JSONObject smartInfoByVersion = versionList.stream()
                .filter(item -> Objects.equals(version, item.getInteger("version")))
                .findFirst()
                .orElse(null);

        if (smartInfoByVersion != null) {
            smartDetail.setVersionList(Collections.singletonList(smartInfoByVersion));
        } else {
            smartDetail.setVersionList(Collections.emptyList());
        }

        SmartComponentVo smartComponentVo = new SmartComponentVo()
                .setRobotId(robotId)
                .setSmartId(smartId)
                .setSmartType(smartComponent.getSmartType())
                .setDetail(smartDetail);

        return AppResponse.success(smartComponentVo);
    }

    @Override
    public AppResponse<Integer> delete(CSmartComponentDto smartComponentDto) throws NoLoginException {
        String robotId = smartComponentDto.getRobotId();
        String smartId = smartComponentDto.getSmartId();
        String userId = UserUtils.nowUserId();

        int result = cSmartComponentDao.delete(robotId, smartId, userId);

        if (result != 1) {
            throw new RuntimeException("Failed to delete smart component");
        }
        return AppResponse.success(1);
    }

    /**
     * 创建新的智能组件
     */
    private Integer create(CSmartComponent smartComponent) {
        int insert = cSmartComponentDao.insert(smartComponent);

        if (insert != 1) {
            throw new RuntimeException("Failed to create smart component");
        }

        return insert;
    }
}
