package com.iflytek.rpa.robot.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.robot.dao.SharedSubVarDao;
import com.iflytek.rpa.robot.dao.SharedVarDao;
import com.iflytek.rpa.robot.dao.SharedVarKeyTenantDao;
import com.iflytek.rpa.robot.dao.SharedVarUserDao;
import com.iflytek.rpa.robot.entity.SharedVar;
import com.iflytek.rpa.robot.entity.SharedVarKeyTenant;
import com.iflytek.rpa.robot.entity.dto.SharedVarBatchDto;
import com.iflytek.rpa.robot.entity.enums.SharedVarTypeEnum;
import com.iflytek.rpa.robot.entity.vo.ClientSharedSubVarVo;
import com.iflytek.rpa.robot.entity.vo.ClientSharedVarVo;
import com.iflytek.rpa.robot.entity.vo.SharedSubVarVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarKeyVo;
import com.iflytek.rpa.robot.service.SharedVarService;
import com.iflytek.rpa.terminal.entity.enums.UsageTypeEnum;
import com.iflytek.rpa.utils.EncryptionUtil;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 共享变量服务实现类
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Slf4j
@Service
public class SharedVarServiceImpl extends ServiceImpl<SharedVarDao, SharedVar> implements SharedVarService {
    @Resource
    private SharedVarDao sharedVarDao;

    @Resource
    private SharedSubVarDao sharedSubVarDao;

    @Resource
    private SharedVarUserDao sharedVarUserDao;

    @Resource
    private SharedVarKeyTenantDao sharedVarKeyTenantDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    /**
     * 获取共享变量租户密钥
     *
     * @return 密钥 key
     * @throws NoLoginException
     */
    @Override
    public AppResponse<SharedVarKeyVo> getSharedVarKey() throws NoLoginException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
        if (keyTenant == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
        }
        SharedVarKeyVo result = new SharedVarKeyVo();
        result.setKey(keyTenant.getKey());
        return AppResponse.success(result);
    }

    @Override
    public AppResponse<List<ClientSharedVarVo>> getClientSharedVars() throws NoLoginException {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> deptIdRes = rpaAuthFeign.getDeptIdByUserId(userId, tenantId);

        if (!deptIdRes.ok()) return AppResponse.success(new ArrayList<>());
        String deptId = deptIdRes.getData();
        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
        if (keyTenant == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
        }
        String aesKey = keyTenant.getKey();

        // 3. 查询三种类型的共享变量
        List<String> selectVarIds = sharedVarUserDao.getAvailableSharedVarIds(userId);
        List<SharedVar> availableVars = sharedVarDao.getAvailableSharedVars(tenantId, deptId, selectVarIds);
        if (availableVars.isEmpty()) {
            return AppResponse.success(new ArrayList<>());
        }

        // 4. 封装结果
        List<ClientSharedVarVo> result = packageResultVo(availableVars, aesKey);

        return AppResponse.success(result);
    }

    private List<ClientSharedVarVo> packageResultVo(List<SharedVar> availableVars, String aesKey) {
        List<Long> sharedVarIds = availableVars.stream().map(SharedVar::getId).collect(Collectors.toList());
        List<SharedSubVarVo> subVarList = baseMapper.getSubVarListBySharedVarIds(sharedVarIds);
        Map<Long, List<SharedSubVarVo>> sharedVarId2SubVarMap =
                subVarList.stream().collect(Collectors.groupingBy(SharedSubVarVo::getSharedVarId));

        List<ClientSharedVarVo> result = new ArrayList<>();
        for (SharedVar sharedVar : availableVars) {
            ClientSharedVarVo clientVar = new ClientSharedVarVo();
            clientVar.setId(sharedVar.getId());
            clientVar.setSharedVarName(sharedVar.getSharedVarName());
            clientVar.setSharedVarType(sharedVar.getSharedVarType());

            // 子变量列表
            List<SharedSubVarVo> subVars = sharedVarId2SubVarMap.get(sharedVar.getId());
            if (subVars != null && !subVars.isEmpty()) {
                List<ClientSharedSubVarVo> clientSubVars = new ArrayList<>();

                for (SharedSubVarVo subVar : subVars) {
                    ClientSharedSubVarVo clientSubVar = new ClientSharedSubVarVo();
                    clientSubVar.setVarName(subVar.getVarName());
                    clientSubVar.setVarType(subVar.getVarType());
                    clientSubVar.setEncrypt(subVar.getEncrypt());
                    // 加密数据
                    packageEncryptValue(aesKey, subVar, clientSubVar);
                    clientSubVars.add(clientSubVar);
                }
                clientVar.setSubVarList(clientSubVars);

                // 对于非变量组类型，设置主变量的值和加密状态
                if (!SharedVarTypeEnum.GROUP.getCode().equals(sharedVar.getSharedVarType())) {
                    ClientSharedSubVarVo firstSubVar = clientSubVars.get(0);
                    clientVar.setSharedVarValue(firstSubVar.getVarValue());
                    clientVar.setEncrypt(firstSubVar.getEncrypt());
                }
            }

            result.add(clientVar);
        }
        return result;
    }

    private static void packageEncryptValue(String aesKey, SharedSubVarVo subVar, ClientSharedSubVarVo clientSubVar) {
        // 处理加密逻辑
        String varValue = subVar.getVarValue();
        if (subVar.getEncrypt() != null && subVar.getEncrypt() == 1 && varValue != null) {
            try {
                varValue = EncryptionUtil.encrypt(varValue, aesKey);
            } catch (Exception e) {
                log.error("加密变量值失败: {}", e.getMessage());
                throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "变量加密失败");
            }
        }
        clientSubVar.setVarValue(varValue);
    }

    /**
     * 生成指定长度的随机密钥
     *
     * @param length 密钥长度
     * @return 随机密钥
     */
    private String generateRandomKey(int length) {
        final String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        SecureRandom random = new SecureRandom();
        StringBuilder key = new StringBuilder();
        for (int i = 0; i < length; i++) {
            key.append(chars.charAt(random.nextInt(chars.length())));
        }
        return key.toString();
    }

    @Override
    public AppResponse<List<ClientSharedVarVo>> getBatchSharedVar(SharedVarBatchDto updateDto) throws NoLoginException {
        List<Long> ids = updateDto.getIds();
        if (ids.isEmpty()) {
            return AppResponse.success(new ArrayList<>());
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
        if (keyTenant == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
        }
        String aesKey = keyTenant.getKey();
        List<SharedVar> availableVars = sharedVarDao.getAvailableByIds(ids);
        if (availableVars.isEmpty()) {
            return AppResponse.success(new ArrayList<>());
        }

        checkUsePermission(availableVars);

        // 4. 封装结果
        List<ClientSharedVarVo> result = packageResultVo(availableVars, aesKey);

        return AppResponse.success(result);
    }

    private void checkUsePermission(List<SharedVar> availableVars) throws NoLoginException {
        Iterator<SharedVar> iterator = availableVars.iterator();
        while (iterator.hasNext()) {
            SharedVar availableVar = iterator.next();
            if (availableVar.getUsageType().equals(UsageTypeEnum.ALL.getCode())) {
                continue;
            }
            AppResponse<User> response = rpaAuthFeign.getLoginUser();
            if (response == null || response.getData() == null) {
                throw new ServiceException("用户信息获取失败");
            }
            User uapUser = response.getData();
            if (availableVar.getUsageType().equals(UsageTypeEnum.DEPT.getCode())) {
                String orgId = uapUser.getOrgId();
                if (!availableVar.getDeptId().equals(orgId)) {
                    iterator.remove();
                    continue;
                }
            }
            if (availableVar.getUsageType().equals(UsageTypeEnum.SELECT.getCode())) {
                String userId = uapUser.getId();
                List<String> availableSharedVarIds = sharedVarUserDao.getAvailableSharedVarIds(userId);
                if (!availableSharedVarIds.contains(String.valueOf(availableVar.getId()))) {
                    iterator.remove();
                }
            }
        }
    }
}
