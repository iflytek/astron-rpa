package com.iflytek.rpa.component.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.DISPATCH;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CProcessDao;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.component.dao.ComponentDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.dao.ComponentVersionDao;
import com.iflytek.rpa.component.entity.Component;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.component.entity.ComponentVersion;
import com.iflytek.rpa.component.entity.bo.ComponentRobotUseDeleteBo;
import com.iflytek.rpa.component.entity.bo.ComponentRobotUseUpdateBo;
import com.iflytek.rpa.component.entity.dto.*;
import com.iflytek.rpa.component.entity.vo.ComponentUseVo;
import com.iflytek.rpa.component.entity.vo.EditCompUseVo;
import com.iflytek.rpa.component.service.ComponentRobotUseService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * 机器人对组件引用表(ComponentRobotUse)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service("componentRobotUseService")
public class ComponentRobotUseServiceImpl extends ServiceImpl<ComponentRobotUseDao, ComponentRobotUse>
        implements ComponentRobotUseService {

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private ComponentVersionDao componentVersionDao;

    @Autowired
    private ComponentDao componentDao;

    @Autowired
    private CProcessDao cProcessDao;

    @Autowired
    private ComponentRobotUseServiceImpl self;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    private static List<ComponentUseVo> getComponentUseVos(List<ComponentRobotUse> componentRobotUses) {
        List<ComponentUseVo> componentUseVos = new ArrayList<>();
        if (componentRobotUses != null && !componentRobotUses.isEmpty()) {
            for (ComponentRobotUse componentRobotUse : componentRobotUses) {
                ComponentUseVo componentUseVo = new ComponentUseVo();
                componentUseVo.setComponentId(componentRobotUse.getComponentId());
                componentUseVo.setVersion(componentRobotUse.getComponentVersion());
                componentUseVos.add(componentUseVo);
            }
        }
        return componentUseVos;
    }

    @Override
    public AppResponse<List<ComponentUseVo>> getComponentUse(GetComponentUseDto getComponentUseDto)
            throws NoLoginException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        if (getComponentUseDto.getMode().equals(DISPATCH)) {
            getComponentUseDto.setVersion(getComponentUseDto.getRobotVersion());
        }
        Integer robotVersion = getRobotVersion(
                getComponentUseDto.getRobotId(),
                getComponentUseDto.getMode(),
                getComponentUseDto.getVersion(),
                new BaseDto());

        // 根据机器人ID和版本号查询组件引用
        List<ComponentRobotUse> componentRobotUses =
                componentRobotUseDao.getByRobotIdAndVersion(getComponentUseDto.getRobotId(), robotVersion, tenantId);
        if (CollectionUtils.isEmpty(componentRobotUses)) return AppResponse.success(Collections.EMPTY_LIST);

        List<ComponentUseVo> componentUseVos = getComponentUseVos(componentRobotUses);

        return AppResponse.success(componentUseVos);
    }

    @Override
    public AppResponse<String> addComponentUse(AddCompUseDto addCompUseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        // 获取机器人版本号
        Integer robotVersion = getRobotVersion(
                addCompUseDto.getRobotId(), addCompUseDto.getMode(), addCompUseDto.getRobotVersion(), new BaseDto());

        // 创建引用的时候默认是 最新是组件的最新版本
        Integer latestVersion = componentVersionDao.getLatestVersion(addCompUseDto.getComponentId(), tenantId);

        // 检查是否已存在相同的组件引用记录
        ComponentRobotUse existingRecord = componentRobotUseDao.getByRobotIdVersionAndComponentIdVersion(
                addCompUseDto.getRobotId(), robotVersion, addCompUseDto.getComponentId(), latestVersion, tenantId);

        if (existingRecord != null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "该机器人版本下已存在相同的组件引用记录");
        }

        // 创建组件引用记录
        ComponentRobotUse componentRobotUse = new ComponentRobotUse();
        componentRobotUse.setRobotId(addCompUseDto.getRobotId());
        componentRobotUse.setRobotVersion(robotVersion);
        componentRobotUse.setComponentId(addCompUseDto.getComponentId());
        componentRobotUse.setComponentVersion(latestVersion);
        componentRobotUse.setCreatorId(userId);
        componentRobotUse.setCreateTime(new Date());
        componentRobotUse.setUpdaterId(userId);
        componentRobotUse.setUpdateTime(new Date());
        componentRobotUse.setDeleted(0);
        componentRobotUse.setTenantId(tenantId);

        // 保存到数据库
        boolean result = this.save(componentRobotUse);
        if (result) {
            return AppResponse.success("组件引用添加成功");
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "组件引用添加失败");
        }
    }

    @Override
    public AppResponse<String> deleteComponentUse(DelComponentUseDto delComponentUseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        // 获取机器人版本号
        Integer robotVersion = getRobotVersion(
                delComponentUseDto.getRobotId(),
                delComponentUseDto.getMode(),
                delComponentUseDto.getRobotVersion(),
                new BaseDto());

        // 创建删除BO对象
        ComponentRobotUseDeleteBo deleteBo = new ComponentRobotUseDeleteBo();
        deleteBo.setRobotId(delComponentUseDto.getRobotId());
        deleteBo.setRobotVersion(robotVersion);
        deleteBo.setComponentId(delComponentUseDto.getComponentId());
        deleteBo.setTenantId(tenantId);
        deleteBo.setUpdaterId(userId);

        // 调用DAO方法执行删除操作
        int result = componentRobotUseDao.deleteComponentUse(deleteBo);

        if (result > 0) {
            return AppResponse.success("组件引用删除成功");
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "组件引用删除失败");
        }
    }

    @Override
    public AppResponse<String> updateComponentUse(UpdateComponentUseDto updateComponentUseDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        // 获取机器人版本号
        Integer robotVersion = getRobotVersion(
                updateComponentUseDto.getRobotId(),
                updateComponentUseDto.getMode(),
                updateComponentUseDto.getRobotVersion(),
                new BaseDto());

        // 获取现有组件引用记录
        ComponentRobotUse existingUse = getExistingComponentUse(updateComponentUseDto, robotVersion, userId);

        // 校验版本号
        validateComponentVersion(updateComponentUseDto, existingUse, tenantId);

        // 执行更新操作
        return executeComponentUseUpdate(updateComponentUseDto, existingUse, robotVersion, tenantId, userId);
    }

    /**
     * 获取现有组件引用记录
     */
    private ComponentRobotUse getExistingComponentUse(
            UpdateComponentUseDto updateComponentUseDto, Integer robotVersion, String userId) {
        ComponentRobotUse existingUse = componentRobotUseDao.getByRobotIdVersionAndComponentId(
                updateComponentUseDto.getRobotId(), robotVersion, updateComponentUseDto.getComponentId(), userId);

        if (existingUse == null) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "该机器人版本下未找到对应的组件引用");
        }
        return existingUse;
    }

    /**
     * 校验组件版本号
     */
    private void validateComponentVersion(
            UpdateComponentUseDto updateComponentUseDto, ComponentRobotUse existingUse, String tenantId) {
        Integer oldVersion = existingUse.getComponentVersion();
        Integer newVersion = updateComponentUseDto.getComponentVersion();

        // 校验新版本号是否大于旧版本号
        if (newVersion <= oldVersion) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "新版本号必须大于当前版本号");
        }

        // 校验新版本号在component_version表中是否存在
        ComponentVersion newComponentVersion = componentVersionDao.getVersionByComponentIdAndVersion(
                updateComponentUseDto.getComponentId(), newVersion, tenantId);
        if (newComponentVersion == null) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "指定的组件版本不存在");
        }
    }

    /**
     * 执行组件引用更新操作
     */
    private AppResponse<String> executeComponentUseUpdate(
            UpdateComponentUseDto updateComponentUseDto,
            ComponentRobotUse existingUse,
            Integer robotVersion,
            String tenantId,
            String userId) {
        // 创建更新BO对象
        ComponentRobotUseUpdateBo updateBo = new ComponentRobotUseUpdateBo();
        updateBo.setRobotId(updateComponentUseDto.getRobotId());
        updateBo.setRobotVersion(robotVersion);
        updateBo.setComponentId(updateComponentUseDto.getComponentId());
        updateBo.setOldComponentVersion(existingUse.getComponentVersion());
        updateBo.setNewComponentVersion(updateComponentUseDto.getComponentVersion());
        updateBo.setTenantId(tenantId);
        updateBo.setUpdaterId(userId);

        int result = componentRobotUseDao.updateComponentUse(updateBo);

        if (result > 0) {
            return AppResponse.success("组件引用版本更新成功");
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "组件引用版本更新失败");
        }
    }

    public Integer getRobotVersion(String robotId, String mode, Integer version, BaseDto baseDto) {
        baseDto.setMode(mode);
        baseDto.setRobotVersion(version);
        baseDto.setRobotId(robotId);

        // 解决代理不生效问题，不能用类调用自己的方法，只能用注入的方式
        self.getVersion(baseDto);

        return baseDto.getRobotVersion();
    }

    @RobotVersionAnnotation
    public void getVersion(BaseDto baseDto) {}

    @Override
    public AppResponse<String> getProcessId(String componentId, Integer componentVersion) throws NoLoginException {

        // 查询流程ID
        String processId = cProcessDao.getProcessIdByComp(componentId, componentVersion);

        if (processId == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "流程id查询为空");

        return AppResponse.success(processId);
    }

    @Override
    public AppResponse<EditCompUseVo> getEditCompUse(EditCompUseDto queryDto) throws NoLoginException {
        String componentId = queryDto.getComponentId();
        String robotId = queryDto.getRobotId();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        ComponentRobotUse componentRobotUse =
                componentRobotUseDao.getByRobotIdVersionAndComponentId(robotId, 0, componentId, userId);
        ComponentVersion componentVersion = componentVersionDao.getVersionByComponentIdAndVersion(
                componentId, componentRobotUse.getComponentVersion(), tenantId);
        Component component = componentDao.getComponentById(componentId, userId, tenantId);

        EditCompUseVo editCompUseVo = new EditCompUseVo();
        editCompUseVo.setName(component.getName());
        editCompUseVo.setIcon(componentVersion.getIcon());
        editCompUseVo.setComponentId(componentId);
        editCompUseVo.setComponentVersion(componentVersion.getVersion());

        return AppResponse.success(editCompUseVo);
    }
}
