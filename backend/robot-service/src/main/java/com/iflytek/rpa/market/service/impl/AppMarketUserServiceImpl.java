package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.OBTAINED;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.common.feign.entity.dto.GetMarketTenantUserListDto;
import com.iflytek.rpa.common.feign.entity.dto.GetMarketUserByPhoneDto;
import com.iflytek.rpa.common.feign.entity.dto.GetMarketUserByPhoneForOwnerDto;
import com.iflytek.rpa.common.feign.entity.dto.GetMarketUserListByPublicDto;
import com.iflytek.rpa.common.feign.entity.dto.GetMarketUserListDto;
import com.iflytek.rpa.common.feign.entity.dto.GetUserUnDeployedDto;
import com.iflytek.rpa.common.feign.entity.dto.PageDto;
import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.TenantUser;
import com.iflytek.rpa.market.service.AppMarketUserService;
import com.iflytek.rpa.notify.entity.dto.CreateNotifyDto;
import com.iflytek.rpa.notify.service.NotifySendService;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
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

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<?> getUserUnDeployed(MarketDto marketDto) throws NoLoginException {
        // 获取没部署的账号
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        if (StringUtils.isNotBlank(marketDto.getPhone())
                && !marketDto.getPhone().matches("[0-9]{0,10}")) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "请输入合法手机号");
        }
        if (null == marketDto.getMarketId() || null == marketDto.getAppId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少应用信息");
        }

        // 通过Feign调用rpa-auth服务获取未部署用户列表
        GetUserUnDeployedDto queryDto = new GetUserUnDeployedDto();
        queryDto.setMarketId(marketDto.getMarketId());
        queryDto.setAppId(marketDto.getAppId());
        queryDto.setTenantId(tenantId);
        queryDto.setPhone(marketDto.getPhone());

        AppResponse<List<com.iflytek.rpa.common.feign.entity.MarketDto>> response =
                rpaAuthFeign.getUserUnDeployed(queryDto);

        List<MarketDto> userList = new ArrayList<>();
        if (response == null || !response.ok()) {
            return AppResponse.success(userList);
        }
        List<com.iflytek.rpa.common.feign.entity.MarketDto> feignUserList = response.getData();

        // 转换为本地MarketDto
        if (feignUserList != null) {
            for (com.iflytek.rpa.common.feign.entity.MarketDto feignDto : feignUserList) {
                MarketDto localDto = new MarketDto();
                localDto.setPhone(feignDto.getPhone());
                localDto.setRealName(feignDto.getRealName());
                localDto.setCreatorId(feignDto.getCreatorId());
                userList.add(localDto);
            }
        }
        return AppResponse.success(userList);
    }

    @Override
    public AppResponse getUserList(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        IPage<MarketDto> userListPage = new Page<>();
        if (null == marketId || null == marketDto.getPageNo() || null == marketDto.getPageSize()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        IPage<MarketDto> pageConfig = new Page<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
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
        String nowUserid = loginUser.getId();

        AppMarket appMarket = appMarketDao.getMarketInfo(marketId);
        if (!appMarket.getMarketType().equals("public")) {
            // 通过Feign调用rpa-auth服务获取市场用户列表
            GetMarketUserListDto queryDto = new GetMarketUserListDto();
            queryDto.setMarketId(marketDto.getMarketId());
            queryDto.setTenantId(tenantId);
            queryDto.setUserName(marketDto.getUserName());
            queryDto.setRealName(marketDto.getRealName());
            queryDto.setSortBy(marketDto.getSortBy());
            queryDto.setSortType(marketDto.getSortType());
            queryDto.setPageNo(marketDto.getPageNo());
            queryDto.setPageSize(marketDto.getPageSize());

            AppResponse<PageDto<com.iflytek.rpa.common.feign.entity.MarketDto>> feignResponse =
                    rpaAuthFeign.getMarketUserList(queryDto);
            if (feignResponse == null || !feignResponse.ok()) {
                userListPage = new Page<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
            } else {
                PageDto<com.iflytek.rpa.common.feign.entity.MarketDto> pageDto = feignResponse.getData();
                // 转换为IPage
                userListPage = new Page<>(pageDto.getCurrentPageNo(), pageDto.getPageSize(), pageDto.getTotalCount());
                List<MarketDto> records = new ArrayList<>();
                if (pageDto.getResult() != null) {
                    for (com.iflytek.rpa.common.feign.entity.MarketDto feignDto : pageDto.getResult()) {
                        MarketDto localDto = new MarketDto();
                        localDto.setId(feignDto.getId());
                        localDto.setUserType(feignDto.getUserType());
                        localDto.setCreatorId(feignDto.getCreatorId());
                        localDto.setCreateTime(feignDto.getCreateTime());
                        localDto.setUserName(feignDto.getUserName());
                        localDto.setRealName(feignDto.getRealName());
                        localDto.setEmail(feignDto.getEmail());
                        localDto.setPhone(feignDto.getPhone());
                        records.add(localDto);
                    }
                }
                userListPage.setRecords(records);
            }
        } else {
            // 通过Feign调用rpa-auth服务获取公共市场用户列表
            GetMarketUserListByPublicDto queryDto = new GetMarketUserListByPublicDto();
            queryDto.setMarketId(marketDto.getMarketId());
            queryDto.setTenantId(tenantId);
            queryDto.setNowUserid(nowUserid);
            queryDto.setUserName(marketDto.getUserName());
            queryDto.setRealName(marketDto.getRealName());
            queryDto.setSortBy(marketDto.getSortBy());
            queryDto.setSortType(marketDto.getSortType());
            queryDto.setPageNo(marketDto.getPageNo());
            queryDto.setPageSize(marketDto.getPageSize());

            AppResponse<PageDto<com.iflytek.rpa.common.feign.entity.MarketDto>> feignResponse =
                    rpaAuthFeign.getMarketUserListByPublic(queryDto);
            if (feignResponse == null || !feignResponse.ok()) {
                userListPage = new Page<>(marketDto.getPageNo(), marketDto.getPageSize(), true);
            } else {
                PageDto<com.iflytek.rpa.common.feign.entity.MarketDto> pageDto = feignResponse.getData();
                // 转换为IPage
                userListPage = new Page<>(pageDto.getCurrentPageNo(), pageDto.getPageSize(), pageDto.getTotalCount());
                List<MarketDto> records = new ArrayList<>();
                if (pageDto.getResult() != null) {
                    for (com.iflytek.rpa.common.feign.entity.MarketDto feignDto : pageDto.getResult()) {
                        MarketDto localDto = new MarketDto();
                        localDto.setId(feignDto.getId());
                        localDto.setUserType(feignDto.getUserType());
                        localDto.setCreatorId(feignDto.getCreatorId());
                        localDto.setCreateTime(feignDto.getCreateTime());
                        localDto.setUserName(feignDto.getUserName());
                        localDto.setRealName(feignDto.getRealName());
                        localDto.setEmail(feignDto.getEmail());
                        localDto.setPhone(feignDto.getPhone());
                        records.add(localDto);
                    }
                }
                userListPage.setRecords(records);
            }
        }
        if (CollectionUtils.isEmpty(userListPage.getRecords())) {
            return AppResponse.success(userListPage);
        }
        // 如果是企业公共市场 不查询创建者
        if (!appMarket.getMarketType().equals("public")) {
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

        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String nowUserId = loginUser.getId();
        if (marketDto.getCreatorId().equals(nowUserId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "自己不能移出自己");
        }
        String id = appMarketUserDao.getIdByMarketIdAndCreatorId(marketId, marketDto.getCreatorId());
        if (StringUtils.isNotBlank(id)) {
            Integer i = appMarketUserDao.deleteById(id);
            if (i > 0) {
                // 若从市场中获取过应用，将待更新应用的状态置为已获取，本人，市场id
                robotExecuteDao.updateResourceStatusByMarketId(OBTAINED, marketDto.getCreatorId(), marketId);
                return AppResponse.success(true);
            }
        }
        return AppResponse.success(false);
    }

    @Override
    public AppResponse roleSet(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
        if (null == marketId || null == marketDto.getCreatorId() || null == marketDto.getUserType()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        if (userId.equals(marketDto.getCreatorId())) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT, "无法更改自己的角色");
        }
        // 如果不在该市场，则无权限操作
        if (!isExistsInMarket(userId, marketId)) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT);
        }
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

    @Override
    public AppResponse getUserByPhone(GetMarketUserByPhoneDto marketDto) {
        String marketId = marketDto.getMarketId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        // 通过Feign调用rpa-auth服务根据手机号查询市场用户
        marketDto.setTenantId(tenantId);

        AppResponse<List<com.iflytek.rpa.common.feign.entity.MarketDto>> feignResponse =
                rpaAuthFeign.getMarketUserByPhone(marketDto);

        List<MarketDto> userList = new ArrayList<>();
        if (feignResponse == null || !feignResponse.ok()) {
            return AppResponse.success(userList);
        }

        List<com.iflytek.rpa.common.feign.entity.MarketDto> feignUserList = feignResponse.getData();

        // 转换为本地MarketDto
        if (feignUserList != null) {
            for (com.iflytek.rpa.common.feign.entity.MarketDto feignDto : feignUserList) {
                MarketDto localDto = new MarketDto();
                localDto.setPhone(feignDto.getPhone());
                localDto.setRealName(feignDto.getRealName());
                localDto.setCreatorId(feignDto.getCreatorId());
                userList.add(localDto);
            }
        }

        if (CollectionUtils.isEmpty(userList)) return AppResponse.success(new ArrayList<MarketDto>());

        // 过滤掉已经在市场中的用户
        List<MarketDto> userListAfterFilter = filterUserAlreadyInMarket(userList, marketId, tenantId);

        return AppResponse.success(userListAfterFilter);
    }

    @Override
    public AppResponse getUserByPhoneForOwner(MarketDto marketDto) throws NoLoginException {
        String marketId = marketDto.getMarketId();
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

        // 通过Feign调用rpa-auth服务根据手机号查询市场中的用户（排除自己）
        GetMarketUserByPhoneForOwnerDto queryDto = new GetMarketUserByPhoneForOwnerDto();
        queryDto.setMarketId(marketId);
        queryDto.setTenantId(tenantId);
        queryDto.setPhone(marketDto.getPhone());
        queryDto.setUserId(userId);

        AppResponse<List<com.iflytek.rpa.common.feign.entity.MarketDto>> feignResponse =
                rpaAuthFeign.getMarketUserByPhoneForOwner(queryDto);

        List<MarketDto> userList = new ArrayList<>();
        if (feignResponse == null || !feignResponse.ok()) {
            return AppResponse.success(userList);
        }

        List<com.iflytek.rpa.common.feign.entity.MarketDto> feignUserList = feignResponse.getData();

        // 转换为本地MarketDto
        if (feignUserList != null) {
            for (com.iflytek.rpa.common.feign.entity.MarketDto feignDto : feignUserList) {
                MarketDto localDto = new MarketDto();
                localDto.setPhone(feignDto.getPhone());
                localDto.setRealName(feignDto.getRealName());
                localDto.setCreatorId(feignDto.getCreatorId());
                userList.add(localDto);
            }
        }

        return AppResponse.success(userList);
    }

    private List<MarketDto> filterUser4Leave(
            List<MarketDto> userList, String marketId, String tenantId, String userId) {
        List<String> marketUserIdList = appMarketUserDao.getAllUserId(tenantId, marketId);

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
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        // 判断邀请的人是否在本租户内
        // 通过Feign调用rpa-auth服务查询租户用户列表
        List<String> userIdList = userInfoList.stream()
                .map(AppMarketUser::getCreatorId)
                .filter(creatorId -> creatorId != null)
                .collect(Collectors.toList());

        GetMarketTenantUserListDto queryDto = new GetMarketTenantUserListDto();
        queryDto.setTenantId(tenantId);
        queryDto.setUserIdList(userIdList);

        AppResponse<List<com.iflytek.rpa.common.feign.entity.TenantUser>> feignResponse =
                rpaAuthFeign.getMarketTenantUserList(queryDto);

        List<TenantUser> tenantUserList = new ArrayList<>();
        if (feignResponse != null && feignResponse.ok() && feignResponse.getData() != null) {
            for (com.iflytek.rpa.common.feign.entity.TenantUser feignTenantUser : feignResponse.getData()) {
                TenantUser localTenantUser = new TenantUser();
                localTenantUser.setTenantId(feignTenantUser.getTenantId());
                localTenantUser.setUserId(feignTenantUser.getUserId());
                tenantUserList.add(localTenantUser);
            }
        }

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
