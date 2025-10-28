package com.iflytek.rpa.example.service.impl;

import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.example.dao.SampleTemplatesDao;
import com.iflytek.rpa.example.dao.SampleUsersDao;
import com.iflytek.rpa.example.entity.SampleTemplates;
import com.iflytek.rpa.example.entity.SampleUsers;
import com.iflytek.rpa.example.service.SampleUsersService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static com.iflytek.rpa.example.constants.ExampleConstants.TYPE_BUSINESS_CLASS_MAP;

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


    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> insertUserSample(String userId) {
        // 1. 读取sample_templates表中version最大的且is_active = 1 的所有记录
        List<SampleTemplates> latestActiveTemplates = getLatestActiveTemplates();
        if (CollectionUtils.isEmpty(latestActiveTemplates)) {
            return AppResponse.success(true);
        }

        // user_sample 表中插入记录
        addUserSamples(latestActiveTemplates, userId);

        return AppResponse.success(true);
    }

    public void addUserSamples(List<SampleTemplates> latestActiveTemplates, String userId){

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
            processTemplateDataByType(template);
        }

        // 批量插入sample_users表
        if (!CollectionUtils.isEmpty(sampleUsersList)) {
            sampleUsersDao.insertBatch(sampleUsersList);
        }

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
     * @param template 模板对象
     */
    private void processTemplateDataByType(SampleTemplates template) {
        if (template == null || StringUtils.isBlank(template.getType()) || StringUtils.isBlank(template.getData())) {
            return;
        }

        Class<?> businessClass = TYPE_BUSINESS_CLASS_MAP.get(template.getType());
        if (businessClass != null) {
            try {
                // 使用fastJson将JSON字符串转换为对应的业务对象
                Object businessObject = JSONObject.parseObject(template.getData(), businessClass);
                
                // 这里可以根据业务对象类型进行相应的数据库操作
                // 例如：businessService.insert(businessObject);
                // 实际使用时需要注入对应的业务服务并进行操作
                
                // 注意：实际项目中，这里应该调用具体的业务服务层方法来保存数据
                // 而不是直接在当前方法中执行数据库操作
            } catch (Exception e) {
                // 记录错误日志但不中断主流程
                log.error("处理模板数据失败，类型: {}, 错误信息: {}", template.getType(), e.getMessage(), e);
            }
        }
    }

}