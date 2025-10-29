package com.iflytek.rpa.example.service.impl;

import static com.iflytek.rpa.example.constants.ExampleConstants.WORKFLOWS_UPSERT_URL;
import static com.iflytek.rpa.robot.constants.RobotConstant.EXECUTOR;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.dao.CProcessDao;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.base.service.handler.ExecutorModeHandler;
import com.iflytek.rpa.example.constants.ExampleConstants;
import com.iflytek.rpa.example.dao.SampleTemplatesDao;
import com.iflytek.rpa.example.dao.SampleUsersDao;
import com.iflytek.rpa.example.entity.Dto.WorkflowsUpsertDto;
import com.iflytek.rpa.example.entity.SampleTemplates;
import com.iflytek.rpa.example.entity.SampleUsers;
import com.iflytek.rpa.example.service.SampleUsersService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.utils.IdWorker;
import java.util.*;
import java.util.function.Function;
import javax.annotation.PostConstruct;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.web.client.RestTemplate;

/**
 * 用户从系统模板中注入的样例数据(SampleUsers)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service
public class SampleUsersServiceImpl extends ServiceImpl<SampleUsersDao, SampleUsers> implements SampleUsersService {

    private static final Logger log = LoggerFactory.getLogger(SampleUsersServiceImpl.class);

    @Autowired
    private SampleTemplatesDao sampleTemplatesDao;

    @Autowired
    private SampleUsersDao sampleUsersDao;

    @Autowired
    private RobotDesignDao robotDesignDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private CProcessDao cProcessDao;

    @Autowired
    private ExecutorModeHandler executorModeHandler;

    @Autowired
    private IdWorker idWorker;

    // type 到插入操作的映射
    private Map<String, Function<Object, Integer>> typeInsertMap = new HashMap<>();

    @PostConstruct
    public void initTypeInsertMap() {
        typeInsertMap.put("robot_design", (obj) -> robotDesignDao.insert((RobotDesign) obj));
        typeInsertMap.put("robot_execute", (obj) -> robotExecuteDao.insert((RobotExecute) obj));
        typeInsertMap.put("robot_version", (obj) -> robotVersionDao.insert((RobotVersion) obj));
        typeInsertMap.put("c_process", (obj) -> cProcessDao.insert((CProcess) obj));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> insertUserSample(String userId, String tenantId) {
        // 1. 读取sample_templates表中version最大的且is_active = 1 的所有记录
        List<SampleTemplates> latestActiveTemplates = getLatestActiveTemplates();
        if (CollectionUtils.isEmpty(latestActiveTemplates)) {
            return AppResponse.success(true);
        }

        // user_sample 表中插入记录
        addUserSamples(latestActiveTemplates, userId, tenantId);

        return AppResponse.success(true);
    }

    public void addUserSamples(List<SampleTemplates> latestActiveTemplates, String userId, String tenantId) {

        String processId = String.valueOf(idWorker.nextId());
        String robotId = String.valueOf(idWorker.nextId());

        // 2. 结合userId，插入多行sample_users表记录
        List<SampleUsers> sampleUsersList = new ArrayList<>();
        Date now = new Date();

        for (SampleTemplates template : latestActiveTemplates) {
            SampleUsers sampleUser = new SampleUsers();
            sampleUser.setCreatorId(userId);
            sampleUser.setSampleId(template.getSampleId());
            sampleUser.setName(template.getName());
            sampleUser.setData(template.getData());
            sampleUser.setSource("system");
            sampleUser.setVersionInjected(template.getVersion());
            sampleUser.setCreatedTime(now);
            sampleUser.setUpdatedTime(now);

            sampleUsersList.add(sampleUser);

            // 3. 根据type，把data中的json数据使用fastJson转换成对应的object，然后插入到对应的业务表中
            processTemplateDataByType(template, userId, tenantId, processId, robotId);
        }

        // 批量插入sample_users表
        sampleUsersDao.insertBatch(sampleUsersList);
    }

    /**
     * 获取最新版本的激活模板
     */
    private List<SampleTemplates> getLatestActiveTemplates() {

        List<String> versionList = sampleTemplatesDao.getVersionList();
        if (CollectionUtils.isEmpty(versionList)) return Collections.EMPTY_LIST;
        String latestVersion = getLatestVersion(versionList);

        return sampleTemplatesDao.getSamples(latestVersion);
    }

    /**
     * 获取最新的版本
     * @param versionList
     * @return
     */
    private String getLatestVersion(List<String> versionList) {
        if (versionList == null || versionList.isEmpty()) {
            return null; // 或者抛出异常，根据业务需求
        }
        String latest = versionList.get(0);

        for (int i = 1; i < versionList.size(); i++) {
            String current = versionList.get(i);
            if (compareVersions(current, latest) > 0) {
                latest = current;
            }
        }

        return latest;
    }

    // 比较两个版本号，按语义化版本规则
    // 返回值：正数表示第一个 > 第二个，0 表示相等，负数表示第一个 < 第二个
    private int compareVersions(String v1, String v2) {
        String[] parts1 = v1.split("\\.");
        String[] parts2 = v2.split("\\.");

        int maxLength = Math.max(parts1.length, parts2.length);

        for (int i = 0; i < maxLength; i++) {
            int num1 = i < parts1.length ? Integer.parseInt(parts1[i]) : 0;
            int num2 = i < parts2.length ? Integer.parseInt(parts2[i]) : 0;

            if (num1 > num2) {
                return 1;
            } else if (num1 < num2) {
                return -1;
            }
        }

        return 0;
    }

    /**
     * 根据模板类型处理数据
     * @param template
     * @param userId
     * @param tenantId
     */
    public void processTemplateDataByType(
            SampleTemplates template, String userId, String tenantId, String processId, String robotId) {
        if (template == null || StringUtils.isBlank(template.getType()) || StringUtils.isBlank(template.getData())) {
            return;
        }

        String businessType = template.getType();

        String dataJsonStr = template.getData();
        // 更新JSON中的creatorId、updaterId和tenantId字段
        dataJsonStr = updateJsonFields(dataJsonStr, userId, tenantId, processId, robotId);

        Class<?> businessClass = ExampleConstants.TYPE_BUSINESS_CLASS_MAP.get(businessType);
        if (businessClass != null) {
            try {
                // 使用fastJson将JSON字符串转换为对应的业务对象
                Object businessObject = JSONObject.parseObject(dataJsonStr, businessClass);

                // 获取对应的插入函数并执行
                Function<Object, Integer> insertFunction = typeInsertMap.get(businessType);
                if (insertFunction != null) {
                    insertFunction.apply(businessObject);
                    log.info("成功插入业务数据，类型: {}", businessType);

                    // 请求openapi接口
                    if (businessType.equals("robot_execute"))
                        sendOpenApiRequest((RobotExecute) businessObject, userId, tenantId);
                } else {
                    log.warn("未找到对应的插入方法，类型: {}", businessType);
                }

            } catch (Exception e) {
                log.error("处理模板数据失败，类型: {}, 错误信息: {}", template.getType(), e.getMessage(), e);
            }
        }
    }

    /**
     * 向openapi发送请求
     *
     * @param robotExecute
     * @param userId
     * @throws NoLoginException
     * @throws JsonProcessingException
     */
    private void sendOpenApiRequest(RobotExecute robotExecute, String userId, String tenantId)
            throws NoLoginException, JsonProcessingException {
        log.info("send request to openapi start ... ");
        QueryParamDto queryParamDto = new QueryParamDto();
        queryParamDto.setRobotId(robotExecute.getRobotId());
        queryParamDto.setMode(EXECUTOR);
        // 获取param
        log.info("start get param");
        AppResponse<List<ParamDto>> allParamResponse =
                executorModeHandler.getParamInside(queryParamDto, userId, tenantId);
        List<ParamDto> responseData = allParamResponse.getData();
        String parameters = JSON.toJSONString(responseData);
        log.info("robot params are as follows:" + parameters);

        WorkflowsUpsertDto requestDto = new WorkflowsUpsertDto();
        requestDto.setProject_id(robotExecute.getRobotId());
        requestDto.setName(robotExecute.getName());
        requestDto.setEnglish_name(robotExecute.getName());
        requestDto.setDescription("");
        requestDto.setVersion(robotExecute.getRobotVersion());
        requestDto.setStatus(1);
        requestDto.setParameters(parameters);

        // 将 requestDto 转换为 JSON 字符串
        String requestBody = JSONObject.toJSONString(requestDto);

        // 创建 RestTemplate 实例
        RestTemplate restTemplate = new RestTemplate();

        // 设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        headers.add("user_id", userId);

        // 创建请求实体
        HttpEntity<String> requestEntity = new HttpEntity<>(requestBody, headers);

        // 发起 POST 请求
        try {
            ResponseEntity<String> response =
                    restTemplate.exchange(WORKFLOWS_UPSERT_URL, HttpMethod.POST, requestEntity, String.class);

            log.info(
                    "OpenAPI 请求成功，URL: {}, 响应状态: {}, 响应体: {}",
                    WORKFLOWS_UPSERT_URL,
                    response.getStatusCode(),
                    response.getBody());
        } catch (Exception e) {
            log.error("OpenAPI 请求失败，URL: {}, 错误信息: {}", WORKFLOWS_UPSERT_URL, e.getMessage(), e);
            throw e;
        }
    }

    /**
     * 更新JSON字符串中的creatorId、updaterId和tenantId字段
     * @param jsonStr JSON字符串
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @return 更新后的JSON字符串
     */
    private String updateJsonFields(String jsonStr, String userId, String tenantId, String processId, String robotId) {
        if (StringUtils.isBlank(jsonStr)) {
            return jsonStr;
        }

        JSONObject jsonObject = JSONObject.parseObject(jsonStr);
        if (jsonObject != null) {
            // 更新creatorId和updaterId为userId
            jsonObject.put("creatorId", userId);
            jsonObject.put("updaterId", userId);
            // 更新tenantId
            jsonObject.put("tenantId", tenantId);
            // 更新robotId
            jsonObject.put("robotId", robotId);
            // 更新processId
            jsonObject.put("processId", processId);

            return jsonObject.toJSONString();
        }
        return jsonStr;
    }
}
