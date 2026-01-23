package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.OBTAINED;

import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.TenantExpirationDto;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketDictDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.market.entity.AppMarketDo;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.service.AppMarketService;
import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 团队市场-团队表(AppMarket)表服务实现类
 *
 * @author makejava
 * @since 2024-01-19 14:41:34
 */
@Service("appMarketService")
public class AppMarketServiceImpl implements AppMarketService {
    @Resource
    private AppMarketDao appMarketDao;

    @Autowired
    private AppMarketDictDao appMarketDictDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @Autowired
    private QuotaCheckService quotaCheckService;

    @Value("${market.maxCreateCount:3}")
    private Integer maxCreateCount;

    @Override
    public AppResponse getAppType() {

        return AppResponse.success(appMarketDictDao.getAppType());
    }

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse getListForPublish() throws NoLoginException {
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
        List<AppMarket> joinedMarketList = appMarketDao.getJoinedMarketList(userId);
        List<AppMarket> createdMarketList = appMarketDao.getCreatedMarketList(tenantId, userId);
        AppMarketDo appMarketDo = new AppMarketDo();
        appMarketDo.setJoinedMarketList(joinedMarketList);
        appMarketDo.setCreatedMarketList(createdMarketList);
        appMarketDo.setNoMarket(
                CollectionUtils.isEmpty(joinedMarketList) && CollectionUtils.isEmpty(createdMarketList));
        return AppResponse.success(appMarketDo);
    }

    @Override
    public AppResponse getMarketList() throws NoLoginException {
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

        List<AppMarket> marketList = appMarketDao.getMarketList(tenantId, userId);

        return AppResponse.success(marketList);
    }

    public AppResponse<Integer> marketNumCheck() throws NoLoginException {
        AppResponse<TenantExpirationDto> resp = rpaAuthFeign.getExpiration();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        TenantExpirationDto data = resp.getData();
        String tenantId = data.getTenantId();
        String tenantType = data.getTenantType();
        // 个人版  团队市场创建次数限制
        if (tenantType.equals("personal")) {
            Integer marketCount = appMarketDao.getMarketCount(tenantId);
            if (marketCount > maxCreateCount) {
                return AppResponse.success(0);
            }
        }
        return AppResponse.success(1);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse addMarket(AppMarket appMarket) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<TenantExpirationDto> resp = rpaAuthFeign.getExpiration();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        TenantExpirationDto data = resp.getData();
        String tenantId = data.getTenantId();

        String marketName = appMarket.getMarketName();
        marketName = marketName.trim();
        appMarket.setMarketName(marketName);
        if (StringUtils.isBlank(marketName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场名称不能为空");
        }

        // 校验市场加入数量配额
        if (!quotaCheckService.checkMarketJoinQuota()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "已加入的市场数量已达上限，无法创建更多团队市场");
        }

        appMarket.setCreatorId(userId);
        appMarket.setUpdaterId(userId);
        Integer marketCount = appMarketDao.getMarketNameByName(tenantId, appMarket.getMarketName());
        if (marketCount > 0) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "该租户内存在同名市场，请重新命名");
        }
        // 产生marketId
        String marketId = idWorker.nextId() + "";
        appMarket.setMarketId(marketId);
        appMarket.setTenantId(tenantId);
        appMarketDao.addMarket(appMarket);
        // 加默认成员
        AppMarketUser appMarketUser = new AppMarketUser();
        appMarketUser.setMarketId(marketId);
        appMarketUser.setCreatorId(userId);
        appMarketUser.setUpdaterId(userId);
        appMarketUser.setTenantId(tenantId);
        appMarketUserDao.addDefaultUser(appMarketUser);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse getMarketInfo(String marketId) throws NoLoginException {
        if (null == marketId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        AppMarket appMarket = appMarketDao.getMarketInfo(marketId);
        if (null == appMarket || null == appMarket.getCreatorId()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL);
        }

        AppResponse<String> realNameResp = rpaAuthFeign.getNameById(appMarket.getCreatorId());
        if (realNameResp == null || realNameResp.getData() == null) {
            throw new ServiceException("用户名获取失败");
        }
        String userName = realNameResp.getData();

        appMarket.setUserName(userName);

        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        // 获取角色
        String userType = appMarketUserDao.getUserTypeForCheck(userId, marketId);
        appMarket.setUserType(userType);

        // 如果是企业公共市场 不查询创建者
        if (appMarket.getMarketType().equals("public")) {
            appMarket.setUserName("系统默认创建");
            // 租户创建时间

            // UapTenant uapTenant = tenantDao.getTenantById(databaseName,tenantId);
            Date createTime = new Date();
            appMarket.setCreateTime(createTime);
            appMarket.setMarketDescribe("该市场为企业共享市场");
        }
        return AppResponse.success(appMarket);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse editTeamMarket(AppMarket appMarket) throws NoLoginException {
        if (null == appMarket) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String marketId = appMarket.getMarketId();
        if (null == marketId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
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

        // marketName 不为空时，判断重名
        if (StringUtils.isNotBlank(appMarket.getMarketName())) {
            boolean b = isMarketNameRepeat(appMarket.getMarketName(), appMarket.getMarketId(), userId, tenantId);
            if (b) return AppResponse.error("团队市场名称重复, 请修改");
        }

        appMarket.setUpdaterId(userId);
        appMarket.setTenantId(tenantId);
        appMarketDao.updateTeamMarket(appMarket);
        return AppResponse.success(true);
    }

    private boolean isMarketNameRepeat(String marketName, String marketId, String userId, String tenantId) {
        List<AppMarket> marketList = appMarketDao.getTenantMarketList(tenantId);
        List<AppMarket> marketListAfterFilter = marketList.stream()
                .filter(appMarket -> (appMarket.getMarketName().equals(marketName)
                        && !appMarket.getMarketId().equals(marketId)))
                .collect(Collectors.toList());

        return !CollectionUtils.isEmpty(marketListAfterFilter);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse leaveTeamMarket(AppMarket appMarket) throws NoLoginException {

        if (null == appMarket || null == appMarket.getMarketId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        AppResponse<User> resp = rpaAuthFeign.getLoginUser();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = resp.getData();
        String userId = loginUser.getId();

        String oldOwnerId = userId;
        appMarket.setCreatorId(oldOwnerId);

        // 如果自己是所有者，且离开的时候没有移交所有权， 直接报错
        String userType = appMarketUserDao.getUserType(appMarket.getMarketId(), userId);
        if (userType.equals("owner") && StringUtils.isBlank(appMarket.getNewOwner())) {
            return AppResponse.error("您已经为团队所有者，已为您刷新页面");
        }

        if (StringUtils.isNotBlank(appMarket.getNewOwner())) {

            AppResponse<User> userResp = rpaAuthFeign.getUserInfoByPhone(appMarket.getNewOwner());
            if (userResp == null || userResp.getData() == null) {
                throw new ServiceException("获取用户信息获取失败");
            }
            User user = userResp.getData();
            String newOwnerId = Optional.ofNullable(user).map(User::getId).orElse(null);
            if (null == newOwnerId) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "新团队负责人不存在");
            }
            // 更新团队表
            appMarketDao.updateTeamMarketOwner(appMarket.getMarketId(), newOwnerId);
            // 更新团队人员表
            appMarketUserDao.updateToOwner(appMarket.getMarketId(), newOwnerId);
        }
        // 离开团队市场
        appMarketUserDao.leaveTeamMarket(appMarket);
        // 若从市场中获取过应用，将待更新应用的状态置为已获取
        robotExecuteDao.updateResourceStatusByMarketId(OBTAINED, appMarket.getCreatorId(), appMarket.getMarketId());
        return AppResponse.success(true);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse dissolveTeamMarket(AppMarket appMarket) {

        if (null == appMarket || null == appMarket.getMarketId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String marketName = appMarketDao.getMarketNameById(appMarket.getMarketId());
        if (StringUtils.isBlank(marketName)) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "团队市场不存在");
        }
        if (!marketName.equals(appMarket.getMarketName())) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "团队市场名称不正确");
        }
        // 删除市场,删除关联的应用，删除关联的成员
        appMarketDao.deleteMarket(appMarket.getMarketId());
        appMarketUserDao.deleteAllUser(appMarket.getMarketId());

        // TODO : v 5.0 后续添加  删除所有的resource 和 关联的version
        //        appMarketResourceDao.deleteResource(appMarket.getMarketId());
        //        appMarketVersionDao.deletVersion(appMarket.getMarketId());

        return AppResponse.success(true);
    }
}
