package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.OBTAINED;

import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketDictDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.market.entity.AppMarketDo;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.service.AppMarketService;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.List;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
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

    //    @Autowired
    //    private AppMarketResourceDao appMarketResourceDao;

    //    @Autowired
    //    private AppMarketVersionDao appMarketVersionDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Override
    public AppResponse getAppType() {

        return AppResponse.success(appMarketDictDao.getAppType());
    }

    @Override
    public AppResponse getListForPublish() throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        List<AppMarket> joinedMarketList = appMarketDao.getJoinedMarketList(tenantId, userId);
        List<AppMarket> createdMarketList = appMarketDao.getCreatedMarketList(tenantId, userId);
        AppMarketDo appMarketDo = new AppMarketDo();
        appMarketDo.setJoinedMarketList(joinedMarketList);
        appMarketDo.setCreatedMarketList(createdMarketList);
        if (CollectionUtils.isEmpty(joinedMarketList) && CollectionUtils.isEmpty(createdMarketList)) {
            appMarketDo.setNoMarket(true);
        } else {
            appMarketDo.setNoMarket(false);
        }
        return AppResponse.success(appMarketDo);
    }

    @Override
    public AppResponse getMarketList() throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        List<AppMarket> marketList = appMarketDao.getMarketList(tenantId, userId);
        return AppResponse.success(marketList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse addMarket(AppMarket appMarket) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        String marketName = appMarket.getMarketName();
        marketName = marketName.trim();
        appMarket.setMarketName(marketName);
        if (StringUtils.isBlank(marketName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "市场名称不能为空");
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
        appMarketUser.setTenantId(tenantId);
        appMarketUser.setCreatorId(userId);
        appMarketUser.setUpdaterId(userId);
        appMarketUserDao.addDefaultUser(appMarketUser);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse getMarketInfo(String marketId) throws NoLoginException {
        if (null == marketId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = TenantUtils.getTenantId();
        AppMarket appMarket = appMarketDao.getMarketInfo(tenantId, marketId);
        if (null == appMarket || null == appMarket.getCreatorId()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL);
        }
        String userName = UserUtils.getRealNameById(appMarket.getCreatorId());
        appMarket.setUserName(userName);
        String userId = UserUtils.nowUserId();
        // 获取角色
        String userType = appMarketUserDao.getUserTypeForCheck(userId, marketId);
        appMarket.setUserType(userType);
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
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

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

        if (CollectionUtils.isEmpty(marketListAfterFilter)) return false;
        else return true;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse leaveTeamMarket(AppMarket appMarket) throws NoLoginException {

        if (null == appMarket || null == appMarket.getMarketId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String oldOwnerId = UserUtils.nowUserId();
        appMarket.setCreatorId(oldOwnerId);

        // 如果自己是所有者，且离开的时候没有移交所有权， 直接报错
        String userType = appMarketUserDao.getUserType(appMarket.getMarketId(), UserUtils.nowUserId());
        if (userType.equals("owner") && StringUtils.isBlank(appMarket.getNewOwner())) {
            return AppResponse.error("您已经为团队所有者，已为您刷新页面");
        }

        if (StringUtils.isNotBlank(appMarket.getNewOwner())) {
            String newOwnerId = UserUtils.getRealNameByPhone(appMarket.getNewOwner());
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
