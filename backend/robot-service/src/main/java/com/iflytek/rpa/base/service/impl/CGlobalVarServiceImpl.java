package com.iflytek.rpa.base.service.impl;

import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CGlobalVarDao;
import com.iflytek.rpa.base.entity.CGlobalVar;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CGlobalDto;
import com.iflytek.rpa.base.service.CGlobalVarService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 客户端-全局变量(CGlobalVar)表服务实现类
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Service("cGlobalVarService")
public class CGlobalVarServiceImpl implements CGlobalVarService {
    @Resource
    private CGlobalVarDao globalVarDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    RpaAuthFeign rpaAuthFeign;

    @Override
    @RobotVersionAnnotation
    public AppResponse<?> getGlobalVarInfoList(BaseDto baseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        baseDto.setCreatorId(userId);
        List<CGlobalVar> processNameList = globalVarDao.getGlobalVarInfoList(baseDto);
        return AppResponse.success(processNameList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> createGlobalVar(CGlobalDto globalDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        globalDto.setCreatorId(userId);
        globalDto.setUpdaterId(userId);
        int count = globalVarDao.countVarByName(globalDto);
        if (count > 0) {
            return AppResponse.error("当前工程存在同名变量，请重新命名");
        }
        String globalId = String.valueOf(idWorker.nextId());
        globalDto.setGlobalId(globalId);
        boolean result = globalVarDao.createGlobalVar(globalDto);
        return AppResponse.success(result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> saveGlobalVar(CGlobalDto globalDto) {
        // 判断是否重名
        CGlobalVar globalVar = globalVarDao.getGlobalVarOne(globalDto);
        String globalId = globalDto.getGlobalId();
        if (globalVar != null && !globalId.equals(globalVar.getGlobalId())) {
            return AppResponse.error("存在同名变量，请重新命名");
        }
        boolean result = globalVarDao.saveGlobalVar(globalDto);
        return AppResponse.success(result);
    }

    @Override
    public AppResponse<?> getGlobalVarNameList(String robotId) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        List<CGlobalVar> globalVarNameList = globalVarDao.getGlobalVarNameList(userId, robotId);
        return AppResponse.success(globalVarNameList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> deleteGlobalVar(CGlobalDto globalDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        globalDto.setCreatorId(userId);
        boolean result = globalVarDao.deleteGlobalVar(globalDto);
        return AppResponse.success(result);
    }
}
