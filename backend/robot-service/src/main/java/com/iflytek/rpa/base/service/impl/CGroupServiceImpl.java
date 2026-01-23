package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.iflytek.rpa.base.dao.CElementDao;
import com.iflytek.rpa.base.dao.CGroupDao;
import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.base.service.CGroupService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import javax.annotation.Resource;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 元素或图像的分组(CGroup)表服务实现类
 *
 * @author mjren
 * @since 2024-12-04 10:28:54
 */
@Service("cGroupService")
public class CGroupServiceImpl implements CGroupService {
    @Resource
    private CGroupDao cGroupDao;

    @Autowired
    private CElementDao celementDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<?> createGroup(ServerBaseDto serverBaseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        CGroup cGroup = new CGroup();
        BeanUtils.copyProperties(serverBaseDto, cGroup);
        cGroup.setCreatorId(userId);

        CGroup existedGroup = cGroupDao.getGroupSameName(cGroup);
        if (null != existedGroup) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "分组名称已存在");
        }
        cGroup.setGroupId(idWorker.nextId() + "");
        cGroup.setUpdaterId(userId);
        cGroupDao.insertGroup(cGroup);
        return AppResponse.success(true);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> renameGroup(ServerBaseDto serverBaseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        serverBaseDto.setCreatorId(userId);
        CGroup cGroup = new CGroup();
        BeanUtils.copyProperties(serverBaseDto, cGroup);
        CGroup existedGroup = cGroupDao.getGroupSameName(cGroup);
        if (null != existedGroup) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "分组名称已存在");
        }
        cGroupDao.updateGroup(cGroup);

        // robotDesign 变成editing状态
        robotDesignDao.updateTransformStatus(userId, serverBaseDto.getRobotId(), null, EDITING);

        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> deleteGroup(ServerBaseDto serverBaseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        serverBaseDto.setCreatorId(userId);
        CGroup cGroup = new CGroup();
        BeanUtils.copyProperties(serverBaseDto, cGroup);
        cGroupDao.deleteGroup(cGroup);
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        celementDao.deleteByGroupId(cElement);
        return AppResponse.success(true);
    }
}
