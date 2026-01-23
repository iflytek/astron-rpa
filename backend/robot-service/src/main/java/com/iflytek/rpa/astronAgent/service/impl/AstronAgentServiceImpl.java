package com.iflytek.rpa.astronAgent.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.*;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.astronAgent.dao.AstronAgentDao;
import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotDto;
import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotResponseDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdResponseDto;
import com.iflytek.rpa.astronAgent.service.AstronAgentService;
import com.iflytek.rpa.base.dao.CParamDao;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.conf.dao.UapUserDao;
import com.iflytek.rpa.market.dao.AppMarketResourceDao;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * AstronAgent服务实现类
 */
@Service
@RequiredArgsConstructor
public class AstronAgentServiceImpl implements AstronAgentService {

    @Autowired
    private UapUserDao uapUserDao;

    @Autowired
    private AstronAgentDao astronAgentDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private AppMarketResourceDao appMarketResourceDao;

    @Autowired
    private ComponentRobotUseDao componentUseDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private CParamDao cParamDao;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<CopyRobotResponseDto> copyRobot(CopyRobotDto copyRobotDto) {
        String robotId = copyRobotDto.getRobotId();
        Integer version = copyRobotDto.getVersion();
        String targetPhone = copyRobotDto.getTargetPhone();

        // 1. 根据手机号获取用户ID
        String userId = uapUserDao.getUserIdByLoginNameOrPhone(databaseName, targetPhone, targetPhone);
        if (StringUtils.isBlank(userId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "目标账户不存在");
        }

        // 2. 判断机器人是否存在（从robot_execute表查询，加上deleted=0条件）
        RobotExecute sourceRobot = robotExecuteDao.selectOne(new LambdaQueryWrapper<RobotExecute>()
                .eq(RobotExecute::getRobotId, robotId)
                .eq(RobotExecute::getDeleted, 0)
                .last("LIMIT 1"));
        if (sourceRobot == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人不存在");
        }

        // 3. 判断机器人的creator_id是否是目标用户id，如果是则不需要复制，直接返回robotId
        if (userId.equals(sourceRobot.getCreatorId())) {
            CopyRobotResponseDto responseDto = buildCopyRobotResponse(robotId, version, sourceRobot.getName());
            return AppResponse.success(responseDto);
        }

        // 4. 根据用户ID获取租户ID列表
        List<String> tenantIds = astronAgentDao.getTenantIdsByUserId(databaseName, userId);
        if (CollectionUtils.isEmpty(tenantIds)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "目标账户未关联任何租户");
        }

        // 5. 获取个人租户ID
        String tenantId = astronAgentDao.getPersonalTenantId(databaseName, tenantIds);
        if (StringUtils.isBlank(tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "目标账户未找到个人租户");
        }

        // 6. 根据dataSource判断版本信息来源，并追溯到根机器人
        RobotVersion robotVersion = null;
        String dataSource = sourceRobot.getDataSource();
        String rootRobotId = robotId; // 默认根机器人ID就是robotId
        String rootRobotName = null; // 根机器人名称，用于后续复制

        if (CREATE.equals(dataSource)) {
            // create类型：robotId就是根机器人ID
            rootRobotId = robotId;
            robotVersion = robotVersionDao.getVersion(robotId, version);
            if (null == robotVersion) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "该版本机器人不存在");
            }
        } else if (MARKET.equals(dataSource)) {
            // market类型：需要通过appId和marketId追溯到根机器人
            String appId = sourceRobot.getAppId();
            String marketId = sourceRobot.getMarketId();
            if (StringUtils.isBlank(appId) || StringUtils.isBlank(marketId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场机器人信息不完整");
            }
            // 查询app_market_resource获取根机器人ID
            MarketDto marketDto = new MarketDto();
            marketDto.setAppId(appId);
            marketDto.setMarketId(marketId);
            AppMarketResource appResource = appMarketResourceDao.getAppInfoByAppId(marketDto);
            if (appResource == null || StringUtils.isBlank(appResource.getRobotId())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "无法追溯到根机器人");
            }
            rootRobotId = appResource.getRobotId();
            // 使用根机器人ID和指定version查询版本信息
            robotVersion = robotVersionDao.getVersion(rootRobotId, version);
            if (null == robotVersion) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "该版本机器人不存在");
            }
        } else if (DEPLOY.equals(dataSource)) {
            // deploy类型：appId就是根机器人ID
            String appId = sourceRobot.getAppId();
            if (StringUtils.isBlank(appId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "部署机器人信息不完整");
            }
            rootRobotId = appId;
            // 使用根机器人ID和指定version查询版本信息
            robotVersion = robotVersionDao.getVersion(rootRobotId, version);
            if (null == robotVersion) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "该版本机器人不存在");
            }
        } else {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "不支持的数据源类型");
        }

        // 获取根机器人名称（从robot_execute表查询根机器人）
        RobotExecute rootRobot = robotExecuteDao.selectOne(new LambdaQueryWrapper<RobotExecute>()
                .eq(RobotExecute::getRobotId, rootRobotId)
                .eq(RobotExecute::getDeleted, 0)
                .last("LIMIT 1"));
        if (rootRobot != null && StringUtils.isNotBlank(rootRobot.getName())) {
            rootRobotName = rootRobot.getName();
        }

        // 7. 构建机器人名称（自动处理重名，添加序号后缀）
        String baseRobotName;
        if (StringUtils.isNotBlank(rootRobotName)) {
            baseRobotName = rootRobotName + "-智能体复制机器人";
        } else {
            baseRobotName = "智能体复制机器人";
        }
        String robotName = generateUniqueRobotName(baseRobotName, userId, tenantId, null);

        // 8. 查询该机器人是否已复制过（通过dataSource为deploy且appId为rootRobotId，加上deleted=0条件）
        RobotExecute existingRobot = robotExecuteDao.selectOne(new LambdaQueryWrapper<RobotExecute>()
                .eq(RobotExecute::getAppId, rootRobotId)
                .eq(RobotExecute::getCreatorId, userId)
                .eq(RobotExecute::getTenantId, tenantId)
                .eq(RobotExecute::getDataSource, DEPLOY)
                .eq(RobotExecute::getDeleted, 0)
                .last("LIMIT 1"));

        String newRobotId;
        if (existingRobot != null) {
            // 如果版本不同，更新
            if (!version.equals(existingRobot.getAppVersion())) {
                // 更新时重新生成唯一名称（排除当前机器人本身）
                robotName = generateUniqueRobotName(baseRobotName, userId, tenantId, existingRobot.getRobotId());

                existingRobot.setName(robotName);
                existingRobot.setAppVersion(version);
                existingRobot.setUpdateTime(new Date());
                existingRobot.setUpdaterId(userId);
                existingRobot.setResourceStatus(null);
                existingRobot.setDataSource(DEPLOY);
                existingRobot.setAppId(rootRobotId);
                existingRobot.setMarketId(null);
                robotExecuteDao.updateById(existingRobot);
                newRobotId = existingRobot.getRobotId();
            } else {
                // 版本相同，直接返回
                newRobotId = existingRobot.getRobotId();
            }
        } else {
            // 插入新记录
            newRobotId = idWorker.nextId() + "";
            RobotExecute robotExecute = new RobotExecute();
            robotExecute.setRobotId(newRobotId);
            robotExecute.setName(robotName);
            robotExecute.setCreatorId(userId);
            robotExecute.setUpdaterId(userId);
            robotExecute.setTenantId(tenantId);
            robotExecute.setAppId(rootRobotId);
            robotExecute.setAppVersion(version);
            robotExecute.setMarketId(null);
            robotExecute.setResourceStatus(null);
            robotExecute.setDataSource(DEPLOY);
            robotExecute.setUpdateTime(new Date());
            robotExecuteDao.insertObtainedRobot(robotExecute);

            // 组件的引用也需要插入一下（根机器人有版本表记录，需要复制组件引用）
            addCompUseList(newRobotId, version, robotVersion, tenantId, userId);
        }

        CopyRobotResponseDto responseDto = buildCopyRobotResponse(newRobotId, version, robotName);

        return AppResponse.success(responseDto);
    }

    /**
     * 构建复制机器人响应DTO
     * @param robotId 机器人ID
     * @param version 版本号
     * @return CopyRobotResponseDto
     */
    private CopyRobotResponseDto buildCopyRobotResponse(String robotId, Integer version, String robotName) {
        CopyRobotResponseDto responseDto = new CopyRobotResponseDto();
        responseDto.setRobotId(robotId);
        responseDto.setName(robotName);
        responseDto.setEnglishName("");
        responseDto.setDescription("");
        responseDto.setVersion(version != null ? version.toString() : "1.0.0");
        responseDto.setStatus(1);

        // 调用getAllParams获取参数（无需认证）
        try {
            List<ParamDto> params = getAllParamsWithoutAuth(robotId, null, null);
            responseDto.setParameters(params);
        } catch (Exception e) {
            // 如果获取参数失败，设置为空列表
            responseDto.setParameters(new ArrayList<>());
        }

        return responseDto;
    }

    /**
     * 生成唯一的机器人名称（如果重名则添加序号后缀）
     * @param baseName 基础名称
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @param excludeRobotId 排除的机器人ID（更新时使用，排除当前机器人本身）
     * @return 唯一的机器人名称
     */
    private String generateUniqueRobotName(String baseName, String userId, String tenantId, String excludeRobotId) {
        // 一次性查询所有相同基础名称的机器人（支持基础名称和带数字后缀的名称）
        LambdaQueryWrapper<RobotExecute> queryWrapper = new LambdaQueryWrapper<RobotExecute>()
                .eq(RobotExecute::getCreatorId, userId)
                .eq(RobotExecute::getTenantId, tenantId)
                .eq(RobotExecute::getDeleted, 0)
                .and(wrapper -> {
                    // 匹配基础名称或基础名称+数字后缀的格式
                    wrapper.eq(RobotExecute::getName, baseName).or().likeRight(RobotExecute::getName, baseName);
                });

        // 如果是指定要排除的机器人ID（更新场景），则排除它
        if (StringUtils.isNotBlank(excludeRobotId)) {
            queryWrapper.ne(RobotExecute::getRobotId, excludeRobotId);
        }

        List<RobotExecute> existingRobots = robotExecuteDao.selectList(queryWrapper);

        // 如果基础名称不存在，直接返回
        boolean baseNameExists = existingRobots.stream().anyMatch(robot -> baseName.equals(robot.getName()));
        if (!baseNameExists) {
            return baseName;
        }

        // 找出所有带数字后缀的名称，提取最大序号
        int maxSuffix = 0;
        for (RobotExecute robot : existingRobots) {
            String name = robot.getName();
            if (name.startsWith(baseName) && name.length() > baseName.length()) {
                // 检查后缀是否为纯数字
                String suffixStr = name.substring(baseName.length());
                try {
                    int suffix = Integer.parseInt(suffixStr);
                    if (suffix > maxSuffix) {
                        maxSuffix = suffix;
                    }
                } catch (NumberFormatException e) {
                    // 忽略格式不正确的名称（不是纯数字后缀）
                }
            }
        }

        // 生成新的唯一名称（直接在名字后跟数字）
        return baseName + (maxSuffix + 1);
    }

    /**
     * 添加组件引用列表
     */
    private void addCompUseList(
            String newRobotId,
            Integer newRobotVersion,
            RobotVersion authorRobotVersion,
            String tenantId,
            String userId) {
        String authorRobotId = authorRobotVersion.getRobotId();
        Integer authorVersion = authorRobotVersion.getVersion();
        List<ComponentRobotUse> compUseListAuth =
                componentUseDao.getByRobotIdAndVersion(authorRobotId, authorVersion, tenantId);

        List<ComponentRobotUse> newCompUseList = new ArrayList<>();

        for (ComponentRobotUse compRobotUse : compUseListAuth) {
            ComponentRobotUse newCompUse = new ComponentRobotUse();
            BeanUtils.copyProperties(compRobotUse, newCompUse);
            newCompUse.setRobotId(newRobotId);
            newCompUse.setRobotVersion(newRobotVersion);
            newCompUse.setCreatorId(userId);
            newCompUse.setUpdaterId(userId);
            newCompUse.setTenantId(tenantId);
            newCompUse.setCreateTime(new Date());
            newCompUse.setUpdateTime(new Date());

            newCompUseList.add(newCompUse);
        }
        if (!newCompUseList.isEmpty()) {
            componentUseDao.insertBatch(newCompUseList);
        }
    }

    @Override
    public AppResponse<GetUserIdResponseDto> getUserIdByPhone(GetUserIdDto getUserIdDto) {
        String phone = getUserIdDto.getPhone();

        // 根据手机号获取用户ID
        String userId = uapUserDao.getUserIdByLoginNameOrPhone(databaseName, phone, phone);
        if (StringUtils.isBlank(userId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "用户不存在");
        }

        GetUserIdResponseDto responseDto = new GetUserIdResponseDto();
        responseDto.setUserId(userId);

        return AppResponse.success(responseDto);
    }

    /**
     * 无需认证获取机器人参数（复制自ExecutorModeHandler，修改为不需要认证）
     * @param robotId 机器人ID
     * @param processId 流程ID（可选）
     * @param moduleId 模块ID（可选）
     * @return 参数列表
     */
    private List<ParamDto> getAllParamsWithoutAuth(String robotId, String processId, String moduleId)
            throws JsonProcessingException {
        // 使用不需要认证的方法获取机器人信息
        RobotExecute executeInfo = robotExecuteDao.getRobotExecuteByRobotId(robotId);
        if (executeInfo == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "无法获取执行器机器人信息");
        }

        return handleDataSource(executeInfo, processId, moduleId, null);
    }

    /**
     * 处理不同数据源的参数获取
     */
    private List<ParamDto> handleDataSource(
            RobotExecute executeInfo, String processId, String moduleId, Integer robotVersion)
            throws JsonProcessingException {
        if (robotVersion != null) {
            executeInfo.setAppVersion(robotVersion);
            executeInfo.setRobotVersion(robotVersion);
        }
        if (CREATE.equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, processId, moduleId);
        } else if (MARKET.equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, processId, moduleId);
        } else if (DEPLOY.equals(executeInfo.getDataSource())) {
            return handleDeploySource(executeInfo, processId, moduleId);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    /**
     * 处理部署来源的参数
     */
    private List<ParamDto> handleDeploySource(RobotExecute executeInfo, String processId, String moduleId) {
        String originRobotId = cParamDao.getDeployOriginalRobotId(executeInfo);

        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return deployModuleHandle(executeInfo, moduleId, originRobotId);
        }

        return deployProcessHandle(executeInfo, processId, originRobotId);
    }

    /**
     * 处理部署来源的模块参数
     */
    private List<ParamDto> deployModuleHandle(RobotExecute executeInfo, String moduleId, String originRobotId) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, originRobotId, executeInfo.getAppVersion());
        return convertParams(params);
    }

    /**
     * 处理部署来源的流程参数
     */
    private List<ParamDto> deployProcessHandle(RobotExecute executeInfo, String processId, String originRobotId) {
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return convertParams(params);
    }

    /**
     * 处理市场来源的参数
     */
    private List<ParamDto> handleMarketSource(RobotExecute executeInfo, String processId, String moduleId) {
        validateMarketInfo(executeInfo);
        String originRobotId = cParamDao.getMarketRobotId(executeInfo);
        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return marketModuleHandle(executeInfo, moduleId, originRobotId);
        }
        // 流程
        return marketProcessHandle(executeInfo, processId, originRobotId);
    }

    /**
     * 处理市场来源的模块参数
     */
    private List<ParamDto> marketModuleHandle(RobotExecute executeInfo, String moduleId, String originRobotId) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, originRobotId, executeInfo.getAppVersion());
        return convertParams(params);
    }

    /**
     * 处理市场来源的流程参数
     */
    private List<ParamDto> marketProcessHandle(RobotExecute executeInfo, String processId, String originRobotId) {
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return convertParams(params);
    }

    /**
     * 处理创建来源的参数
     */
    private List<ParamDto> handleCreateSource(RobotExecute executeInfo, String processId, String moduleId)
            throws JsonProcessingException {
        Integer enabledVersion = cParamDao.getRobotVersion(executeInfo.getRobotId());
        if (executeInfo.getRobotVersion() != null) {
            enabledVersion = executeInfo.getRobotVersion();
        }
        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return createModuleHandle(executeInfo, moduleId, enabledVersion);
        }
        // 流程
        return createProcessHandle(executeInfo, processId, enabledVersion);
    }

    /**
     * 处理创建来源的模块参数
     */
    private List<ParamDto> createModuleHandle(RobotExecute executeInfo, String moduleId, Integer enabledVersion) {
        List<CParam> params = cParamDao.getSelfRobotParamByModuleId(executeInfo.getRobotId(), moduleId, enabledVersion);
        return convertParams(params);
    }

    /**
     * 处理创建来源的流程参数
     */
    private List<ParamDto> createProcessHandle(RobotExecute executeInfo, String processId, Integer enabledVersion)
            throws JsonProcessingException {
        String mainProcessId = cParamDao.getMianProcessId(executeInfo.getRobotId(), enabledVersion);
        if (mainProcessId.equals(processId)) {
            if (executeInfo.getParamDetail() != null) {
                return parseCustomParams(executeInfo.getParamDetail());
            }
        } else {
            processId = mainProcessId;
        }
        List<CParam> params = cParamDao.getSelfRobotParam(executeInfo.getRobotId(), processId, enabledVersion);
        return convertParams(params);
    }

    /**
     * 验证市场信息
     */
    private void validateMarketInfo(RobotExecute executeInfo) {
        if (StringUtils.isAnyBlank(executeInfo.getMarketId(), executeInfo.getAppId())
                || executeInfo.getAppVersion() == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "机器人市场信息异常");
        }
    }

    /**
     * 解析自定义参数
     */
    private List<ParamDto> parseCustomParams(String paramDetail) throws JsonProcessingException {
        List<CParam> params = objectMapper.readValue(paramDetail, new TypeReference<List<CParam>>() {});
        return convertParams(params);
    }

    /**
     * 转换参数实体为DTO
     */
    private List<ParamDto> convertParams(List<CParam> params) {
        if (CollectionUtils.isEmpty(params)) {
            return Collections.emptyList();
        }
        return params.stream()
                .map(p -> {
                    ParamDto dto = new ParamDto();
                    BeanUtils.copyProperties(p, dto);
                    return dto;
                })
                .collect(Collectors.toList());
    }
}
