package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.OBTAINED;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.TenantUser;
import com.iflytek.rpa.market.service.AppMarketUserService;
import com.iflytek.rpa.notify.entity.dto.CreateNotifyDto;
import com.iflytek.rpa.notify.service.NotifySendService;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 团队市场-人员表，n:n的关系(AppMarketUser)表服务实现类
 *
 * @author makejava
 * @since 2024-01-19 14:41:35
 */
@Service("appMarketUserService")
public class AppMarketUserServiceImpl extends ServiceImpl<AppMarketUserDao, AppMarketUser>
        implements AppMarketUserService {
    @Resource
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private AppMarketDao appMarketDao;

    @Autowired
    private NotifySendService notifySendService;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Value("${casdoor.database.name:casdoor}")
    private String databaseName;

    @Override
    public AppResponse<?> getUserUnDeployed(MarketDto marketDto) throws NoLoginException {
        // 获取没部署的账号
        String tenantId = TenantUtils.getTenantId();

        if (StringUtils.isNotBlank(marketDto.getPhone())
                && !marketDto.getPhone().matches("[0-9]{0,10}")) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "请输入合法手机号");
        }
        if (null == marketDto.getMarketId() || null == marketDto.getAppId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少应用信息");
        }
        marketDto.setTenantId(tenantId);
        List<MarketDto> userList = appMarketUserDao.getUserUnDeployed(marketDto, databaseName);
        return AppResponse.success(userList);
    }

    @Override
    public AppResponse getUserList(MarketDto marketDto) {
        String marketId = marketDto.getMarketId();
        IPage<MarketDto> userListPage = new Page<>();
        if (null == marketId || null == marketDto.getPageNo() || null == marketDto.getPageSize()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        IPage<MarketDto> pageConfig = new Page<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
        // 根据marketId获取appId
        userListPage = appMarketUserDao.getUserList(pageConfig, marketDto, databaseName);
        if (CollectionUtils.isEmpty(userListPage.getRecords())) {
            return AppResponse.success(userListPage);
        }
        // 获取市场创建者
        String creatorId = appMarketDao.getCreator(marketId);
        if (null != creatorId) {
            for (MarketDto userInfo : userListPage.getRecords()) {
                if (creatorId.equals(userInfo.getCreatorId())) {
                    userListPage.getRecords().remove(userInfo);
                    userInfo.setIsCreator(true);
                    userListPage.getRecords().add(0, userInfo);
                    break;
                }
            }
        }
        return AppResponse.success(userListPage);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse deleteUser(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        if (null == marketId || null == marketDto.getCreatorId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String ownerId = appMarketUserDao.getOwnerByRole(marketDto.getMarketId());
        if (marketDto.getCreatorId().equals(ownerId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "不能移出创建者");
        }
        if (marketDto.getCreatorId().equals(UserUtils.nowUserId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "自己不能移出自己");
        }
        // 如果不在该市场，则无权限
        Integer result = appMarketUserDao.deleteUser(marketDto);
        if (result > 0) {
            // 若从市场中获取过应用，将待更新应用的状态置为已获取，本人，市场id
            robotExecuteDao.updateResourceStatusByMarketId(OBTAINED, marketDto.getCreatorId(), marketId);
            return AppResponse.success(true);
        }
        return AppResponse.success(false);
    }

    @Override
    public AppResponse roleSet(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        if (null == marketId || null == marketDto.getCreatorId() || null == marketDto.getUserType()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String userId = UserUtils.nowUserId();
        if (userId.equals(marketDto.getCreatorId())) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT, "无法更改自己的角色");
        }
        // 如果不在该市场，则无权限操作
        if (!isExistsInMarket(userId, marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT);
        }
        // 如果不是管理员，则无权限操作
        //        if(!isAdminInMarket(userId, marketId)){
        //            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT);
        //        }
        String ownerId = appMarketUserDao.getOwnerByRole(marketId);
        if (marketDto.getUserType().equals("owner") && !marketDto.getCreatorId().equals(ownerId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "市场只能有一个拥有者");
        }
        if (!marketDto.getUserType().equals("owner") && marketDto.getCreatorId().equals(ownerId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "创建者角色不可更改");
        }
        Integer result = appMarketUserDao.roleSet(marketDto);
        if (result > 0) {
            return AppResponse.success(true);
        }
        return AppResponse.success(false);
    }

    private Boolean isExistsInMarket(String userId, String marketId) {
        AppMarketUser appMarketUser = new AppMarketUser();
        appMarketUser.setMarketId(marketId);
        appMarketUser.setCreatorId(userId);
        appMarketUser.setDeleted(0);
        long count = appMarketUserDao.count(appMarketUser);
        return count > 0;
    }

    private Boolean isAdminInMarket(String userId, String marketId) {
        AppMarketUser appMarketUser = new AppMarketUser();
        appMarketUser.setMarketId(marketId);
        appMarketUser.setCreatorId(userId);
        appMarketUser.setDeleted(0);
        appMarketUser.setUserType("admin");
        long count = appMarketUserDao.count(appMarketUser);
        return count > 0;
    }

    @Override
    public AppResponse getUserByPhone(MarketDto marketDto) {
        String marketId = marketDto.getMarketId();
        String tenantId = TenantUtils.getTenantId();

        marketDto.setTenantId(tenantId);
        List<MarketDto> userList = appMarketUserDao.getUserByPhone(marketDto, databaseName);

        if (CollectionUtils.isEmpty(userList)) return AppResponse.success(new ArrayList<MarketDto>());

        // 过滤掉已经在市场中的用户
        List<MarketDto> userListAfterFilter = filterUserAlreadyInMarket(userList, marketId, tenantId);

        return AppResponse.success(userListAfterFilter);
    }

    @Override
    public AppResponse getUserByPhoneForOwner(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        marketDto.setTenantId(tenantId);
        List<MarketDto> userList = appMarketUserDao.getUserByPhoneForOwner(marketDto, databaseName);

        // 过滤只存在该市场的用户 且需要排除自己
        List<MarketDto> userListAfterFilter = filterUser4Leave(userList, marketId, tenantId, userId);

        return AppResponse.success(userListAfterFilter);
    }

    private List<MarketDto> filterUser4Leave(
            List<MarketDto> userList, String marketId, String tenantId, String userId) {
        List<Long> marketUserIdList = appMarketUserDao.getAllUserId(tenantId, marketId);

        // 在市场内的userList
        List<MarketDto> userListInMarket = userList.stream()
                .filter(marketDto -> marketUserIdList.contains(marketDto.getCreatorId()))
                .collect(Collectors.toList());

        // 排除自己
        List<MarketDto> userListFinal = userListInMarket.stream()
                .filter(marketDto1 -> !(marketDto1.getCreatorId().equals(userId)))
                .collect(Collectors.toList());

        return userListFinal;
    }

    private List<MarketDto> filterUserAlreadyInMarket(List<MarketDto> userList, String marketId, String tenantId) {

        List<String> userIdList = userList.stream().map(MarketDto::getCreatorId).collect(Collectors.toList());

        List<String> marketUserIdInList = appMarketUserDao.getMarketUserInList(marketId, userIdList, tenantId);

        List<MarketDto> userListAfterFilter = userList.stream()
                .filter(marketDto -> !marketUserIdInList.contains(marketDto.getCreatorId()))
                .collect(Collectors.toList());

        return userListAfterFilter;
    }

    @Override
    public AppResponse inviteUser(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        List<AppMarketUser> userInfoList = marketDto.getUserInfoList();
        if (CollectionUtils.isEmpty(userInfoList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = TenantUtils.getTenantId();
        // 判断邀请的人是否在本租户内
        List<TenantUser> tenantUserList = appMarketUserDao.getTenantUser(tenantId, userInfoList, databaseName);
        // 根据userId分组
        Map<String, String> userMap =
                tenantUserList.stream().collect(Collectors.toMap(TenantUser::getUserId, TenantUser::getTenantId));

        for (AppMarketUser userInfo : userInfoList) {
            if (null == userInfo) {
                continue;
            }
            if (null == userMap.get(userInfo.getCreatorId())) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "邀请了某些不存在该租户的用户");
            }
        }

        // 产生邀人消息，将marketId,role插入消息表
        CreateNotifyDto createNotifyDto = new CreateNotifyDto();
        createNotifyDto.setMarketUserList(userInfoList);
        createNotifyDto.setTenantId(tenantId);
        createNotifyDto.setMessageType("teamMarketInvite");
        createNotifyDto.setMarketId(marketId);
        notifySendService.createNotify(createNotifyDto);
        return AppResponse.success(true);
    }
}
