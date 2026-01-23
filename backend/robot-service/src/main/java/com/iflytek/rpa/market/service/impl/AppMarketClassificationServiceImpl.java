package com.iflytek.rpa.market.service.impl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.market.dao.AppApplicationDao;
import com.iflytek.rpa.market.dao.AppMarketClassificationDao;
import com.iflytek.rpa.market.entity.AppMarketClassification;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationEditDto;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationManageRequest;
import com.iflytek.rpa.market.entity.dto.AppMarketClassificationManageVo;
import com.iflytek.rpa.market.entity.dto.MarketInfoDto;
import com.iflytek.rpa.market.entity.vo.AppMarketClassificationVo;
import com.iflytek.rpa.market.service.AppApplicationService;
import com.iflytek.rpa.market.service.AppMarketClassificationService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

/**
 * 应用市场分类服务实现类
 *
 * @author auto-generated
 */
@Slf4j
@Service
public class AppMarketClassificationServiceImpl implements AppMarketClassificationService {

    @Autowired
    private AppMarketClassificationDao appMarketClassificationDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Resource
    private AppApplicationService appApplicationService;

    @Autowired
    private AppApplicationDao appApplicationDao;

    @Override
    public AppResponse<List<AppMarketClassificationVo>> getClassificationList() throws NoLoginException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        List<AppMarketClassificationVo> classificationList =
                appMarketClassificationDao.getClassificationListByTenantId(tenantId);
        return AppResponse.success(classificationList);
    }

    @Override
    public AppResponse<List<AppMarketClassificationManageVo>> getClassificationManageList(
            AppMarketClassificationManageRequest request) throws NoLoginException, JsonProcessingException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        List<AppMarketClassificationManageVo> classificationList =
                appMarketClassificationDao.getClassificationManageList(
                        tenantId, request.getName(), request.getSource());
        // 填充引用
        packageReference(classificationList);
        return AppResponse.success(classificationList);
    }

    private void packageReference(List<AppMarketClassificationManageVo> classificationList)
            throws NoLoginException, JsonProcessingException {
        if (classificationList == null || classificationList.isEmpty()) {
            return;
        }
        // 获取分类引用统计
        List<Map> referenceCountList = appMarketClassificationDao.getCategoryReferenceCount();
        Map<Long, Integer> referenceCountMap = referenceCountList.stream()
                .collect(Collectors.toMap(
                        map -> Long.valueOf(map.get("category").toString()),
                        map -> Integer.valueOf(map.get("reference_count").toString())));

        // 开启上架审核
        AppResponse<String> auditStatus = appApplicationService.getAuditStatus();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (auditStatus.ok()) {
            Map<Long, Integer> referenceCountForPendingMap = new HashMap<>();
            List<String> pendingMarketInfoJson = appApplicationDao.getPendingMarketInfoJson(tenantId);
            for (String marketInfoJson : pendingMarketInfoJson) {
                ObjectMapper objectMapper = new ObjectMapper();
                MarketInfoDto marketInfoDto = objectMapper.readValue(marketInfoJson, MarketInfoDto.class);
                String category = marketInfoDto.getCategory();
                Long categoryId = Long.valueOf(category);
                List<String> marketIdList = marketInfoDto.getMarketIdList();
                int num = marketIdList.size();
                Integer orDefault = referenceCountForPendingMap.getOrDefault(categoryId, 0);
                referenceCountForPendingMap.put(categoryId, orDefault + num);
            }
            if (referenceCountMap.isEmpty()) {
                referenceCountMap = new HashMap<>(referenceCountForPendingMap);
            } else {
                for (Map.Entry<Long, Integer> entry : referenceCountForPendingMap.entrySet()) {
                    referenceCountMap.merge(entry.getKey(), entry.getValue(), Integer::sum);
                }
            }
        }

        // 为每个分类设置引用次数
        for (AppMarketClassificationManageVo classification : classificationList) {
            Integer referenceCount = referenceCountMap.get(classification.getId());
            classification.setReference(referenceCount != null ? referenceCount : 0);
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> addClassification(AppMarketClassificationEditDto request) throws NoLoginException {
        if (!StringUtils.hasText(request.getName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "分类名不能为空");
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();

        // 检查分类名是否已存在
        List<AppMarketClassificationVo> existingClassifications =
                appMarketClassificationDao.getClassificationListByTenantId(tenantId);
        boolean nameExists = existingClassifications.stream()
                .anyMatch(classification -> request.getName().equals(classification.getName()));
        if (nameExists) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "分类名已存在");
        }

        int maxSort = 0;
        if (!existingClassifications.isEmpty()) {
            maxSort = existingClassifications.stream()
                    .map(AppMarketClassificationVo::getSort)
                    .filter(Objects::nonNull)
                    .max(Integer::compareTo)
                    .orElse(0);
        }

        // 创建新分类
        AppMarketClassification classification = new AppMarketClassification();
        Date now = new Date();
        classification.setName(request.getName());
        classification.setSource(1); // 1-自定义
        classification.setSort(maxSort + 1); // 排序
        classification.setTenantId(tenantId);
        classification.setCreatorId(userId);
        classification.setCreateTime(now);
        classification.setUpdaterId(userId);
        classification.setUpdateTime(now);
        classification.setDeleted(0);
        int result = appMarketClassificationDao.insert(classification);
        if (result > 0) {
            return AppResponse.success("新增成功");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "新增分类失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> editClassification(AppMarketClassificationEditDto request) throws NoLoginException {
        if (request.getId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "ID不能为空");
        }
        if (!StringUtils.hasText(request.getName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "分类名不能为空");
        }

        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppMarketClassification existingClassification = appMarketClassificationDao.selectById(request.getId());
        if (existingClassification == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "分类不存在");
        }
        if (!tenantId.equals(existingClassification.getTenantId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "无权限修改该分类");
        }

        // 检查分类名是否已存在（排除当前分类）
        List<AppMarketClassificationVo> existingClassifications =
                appMarketClassificationDao.getClassificationListByTenantId(tenantId);
        boolean nameExists = existingClassifications.stream()
                .anyMatch(classification -> request.getName().equals(classification.getName()));
        if (nameExists) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "分类名已存在");
        }

        existingClassification.setName(request.getName());
        existingClassification.setUpdaterId(userId);
        Date now = new Date();
        existingClassification.setUpdateTime(now);

        int result = appMarketClassificationDao.updateById(existingClassification);
        if (result > 0) {
            return AppResponse.success("修改成功");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "修改分类失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteClassification(AppMarketClassificationEditDto request) throws NoLoginException {
        if (request.getId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "ID不能为空");
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppMarketClassification existingClassification = appMarketClassificationDao.selectById(request.getId());
        if (existingClassification == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "分类不存在");
        }
        if (!tenantId.equals(existingClassification.getTenantId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "无权限删除该分类");
        }
        existingClassification.setDeleted(1);
        existingClassification.setUpdaterId(userId);
        Date now = new Date();
        existingClassification.setUpdateTime(now);
        int result = appMarketClassificationDao.updateById(existingClassification);
        if (result > 0) {
            return AppResponse.success("删除成功");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "删除分类失败");
        }
    }
}
