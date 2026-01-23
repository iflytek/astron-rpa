package com.iflytek.rpa.market.service.impl;

import static com.iflytek.rpa.utils.DeBounceUtils.deBounce;

import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.TenantExpirationDto;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketInviteDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarketInvite;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.dto.InviteLinkDto;
import com.iflytek.rpa.market.entity.enums.ExpireTypeEnum;
import com.iflytek.rpa.market.entity.vo.AcceptResultVo;
import com.iflytek.rpa.market.entity.vo.InviteInfoVo;
import com.iflytek.rpa.market.entity.vo.InviteLinkVo;
import com.iflytek.rpa.market.service.AppMarketInviteService;
import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.response.QuotaCodeEnum;
import java.util.Calendar;
import java.util.Date;
import java.util.UUID;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 团队市场-SaaS
 */
@Service("appMarketInviteService")
public class AppMarketInviteServiceImpl implements AppMarketInviteService {

    @Autowired
    private AppMarketInviteDao appMarketInviteDao;

    @Autowired
    private AppMarketDao appMarketDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Autowired
    private AppMarketInviteServiceImpl self;

    @Autowired
    private QuotaCheckService quotaCheckService;

    @Value("${market.invite.maxJoinCount:10}")
    private Integer maxJoinCount;

    @Value("${deBounce.prefix}")
    private String doBouncePrefix;

    @Value("${deBounce.window}")
    private Long deBounceWindow;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<InviteLinkVo> generateInviteLink(InviteLinkDto inviteLinkDto) throws NoLoginException {
        // 参数校验
        if (inviteLinkDto == null || StringUtils.isBlank(inviteLinkDto.getMarketId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "市场ID不能为空");
        }
        if (StringUtils.isBlank(inviteLinkDto.getExpireType())) {
            inviteLinkDto.setExpireType(ExpireTypeEnum.TWENTY_FOUR_HOURS.getCode());
        }
        // 获取当前登录用户信息
        AppResponse<User> userResponse = rpaAuthFeign.getLoginUser();
        if (userResponse == null || !userResponse.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = userResponse.getData();
        String userId = loginUser.getId();

        AppResponse<TenantExpirationDto> resp = rpaAuthFeign.getExpiration();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        TenantExpirationDto data = resp.getData();
        String tenantType = data.getTenantType();

        // 检查用户权限：只有admin才能进行链接分享
        String userType = appMarketUserDao.getUserTypeForCheck(userId, inviteLinkDto.getMarketId());
        if (userType == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "市场中不存在该人员");
        }
        if (!"admin".equals(userType) && !"owner".equals(userType)) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_POWER_LIMIT, "无权限进行链接分享");
        }
        // 查询是否已存在邀请链接
        AppMarketInvite existingInvite =
                appMarketInviteDao.selectByMarketIdAndInviterId(inviteLinkDto.getMarketId(), userId);
        Date now = new Date();

        if (existingInvite != null) {
            // 过期生成新的邀请链接
            if (existingInvite.getExpireTime() != null
                    && existingInvite.getExpireTime().before(now)) {
                AppMarketInvite newInvite = new AppMarketInvite();
                BeanUtils.copyProperties(existingInvite, newInvite);
                existingInvite.setDeleted(1);
                appMarketInviteDao.cancelById(existingInvite.getId());
                String inviteKey = UUID.randomUUID().toString().replace("-", "").substring(0, 8);
                newInvite.setInviteKey(inviteKey);
                newInvite.setCurrentJoinCount(existingInvite.getCurrentJoinCount());
                newInvite.setMaxJoinCount(existingInvite.getMaxJoinCount());
                if (tenantType.equals("personal")) {
                    newInvite.setMaxJoinCount(maxJoinCount);
                } else {
                    newInvite.setMaxJoinCount(-1);
                }
                newInvite.setExpireType(inviteLinkDto.getExpireType());
                ExpireTypeEnum expireTypeEnum = ExpireTypeEnum.getByCode(inviteLinkDto.getExpireType());
                Date expireTime = calculateExpireTime(expireTypeEnum);
                newInvite.setExpireTime(expireTime);
                newInvite.setUpdateTime(now);
                newInvite.setCreateTime(now);
                newInvite.setDeleted(0);
                appMarketInviteDao.insert(newInvite);

                InviteLinkVo responseVo = getInviteLinkVo(newInvite);
                return AppResponse.success(responseVo);
            }
            // 如果已存在，直接返回已存在的链接
            InviteLinkVo responseVo = getInviteLinkVo(existingInvite);
            return AppResponse.success(responseVo);
        }
        // 如果不存在，创建新记录
        AppMarketInvite appMarketInvite = new AppMarketInvite();

        appMarketInvite.setMarketId(inviteLinkDto.getMarketId());
        // 生成随机字符串作为inviteKey
        String inviteKey = UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        appMarketInvite.setInviteKey(inviteKey);
        // 设置邀请人ID
        appMarketInvite.setInviterId(userId);
        // 计算失效时间
        ExpireTypeEnum expireTypeEnum = ExpireTypeEnum.getByCode(inviteLinkDto.getExpireType());
        if (expireTypeEnum == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "无效的失效时间类型，支持：4H、24H、7D、30D");
        }
        Date expireTime = calculateExpireTime(expireTypeEnum);
        appMarketInvite.setExpireTime(expireTime);
        // 设置失效时间类型
        appMarketInvite.setExpireType(inviteLinkDto.getExpireType());
        // 最大加入人数
        if (tenantType.equals("personal")) {
            appMarketInvite.setMaxJoinCount(maxJoinCount);
        } else {
            appMarketInvite.setMaxJoinCount(-1);
        }
        appMarketInvite.setCurrentJoinCount(0);
        appMarketInvite.setCreatorId(userId);
        appMarketInvite.setCreateTime(now);
        appMarketInvite.setUpdaterId(userId);
        appMarketInvite.setUpdateTime(now);
        appMarketInvite.setDeleted(0);
        int i = appMarketInviteDao.insert(appMarketInvite);
        if (i > 0) {
            InviteLinkVo responseVo = new InviteLinkVo();
            responseVo.setInviteKey(inviteKey);
            responseVo.setExpireType(inviteLinkDto.getExpireType());
            responseVo.setExpireTime(expireTime);
            responseVo.setOverNumLimit(0);
            return AppResponse.success(responseVo);
        }
        return null;
    }

    private static InviteLinkVo getInviteLinkVo(AppMarketInvite existingInvite) {
        InviteLinkVo responseVo = new InviteLinkVo();
        responseVo.setInviteKey(existingInvite.getInviteKey());
        responseVo.setExpireTime(existingInvite.getExpireTime());
        responseVo.setExpireType(existingInvite.getExpireType());

        if (existingInvite.getMaxJoinCount() > 0) {
            if (existingInvite.getCurrentJoinCount() >= existingInvite.getMaxJoinCount()) {
                responseVo.setOverNumLimit(1);
            } else {
                responseVo.setOverNumLimit(0);
            }
        }
        return responseVo;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<InviteLinkVo> resetInviteLink(InviteLinkDto inviteLinkDto) throws NoLoginException {
        // 参数校验
        if (inviteLinkDto == null || StringUtils.isBlank(inviteLinkDto.getMarketId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "市场ID不能为空");
        }
        if (StringUtils.isBlank(inviteLinkDto.getExpireType())) {
            inviteLinkDto.setExpireType(ExpireTypeEnum.TWENTY_FOUR_HOURS.getCode());
        }
        // 获取当前登录用户信息
        AppResponse<User> userResponse = rpaAuthFeign.getLoginUser();
        if (userResponse == null || !userResponse.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        AppResponse<TenantExpirationDto> resp = rpaAuthFeign.getExpiration();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        TenantExpirationDto data = resp.getData();
        String tenantType = data.getTenantType();
        User loginUser = userResponse.getData();
        String userId = loginUser.getId();
        // 查询是否存在邀请链接
        AppMarketInvite existingInvite =
                appMarketInviteDao.selectByMarketIdAndInviterId(inviteLinkDto.getMarketId(), userId);
        if (existingInvite == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "该市场尚未生成邀请链接，请先生成邀请链接");
        }
        AppMarketInvite newInvite = new AppMarketInvite();
        BeanUtils.copyProperties(existingInvite, newInvite);
        existingInvite.setDeleted(1);
        appMarketInviteDao.cancelById(existingInvite.getId());
        String inviteKey = UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        Date now = new Date();
        newInvite.setInviteKey(inviteKey);
        newInvite.setCurrentJoinCount(existingInvite.getCurrentJoinCount());
        newInvite.setMaxJoinCount(existingInvite.getMaxJoinCount());
        if (tenantType.equals("personal")) {
            newInvite.setMaxJoinCount(maxJoinCount);
        } else {
            newInvite.setMaxJoinCount(-1);
        }
        newInvite.setExpireType(inviteLinkDto.getExpireType());
        ExpireTypeEnum expireTypeEnum = ExpireTypeEnum.getByCode(inviteLinkDto.getExpireType());
        Date expireTime = calculateExpireTime(expireTypeEnum);
        newInvite.setExpireTime(expireTime);
        newInvite.setUpdateTime(now);
        newInvite.setCreateTime(now);
        newInvite.setDeleted(0);
        appMarketInviteDao.insert(newInvite);
        // 构建响应
        InviteLinkVo responseVo = new InviteLinkVo();
        responseVo.setInviteKey(inviteKey);
        responseVo.setExpireType(inviteLinkDto.getExpireType());
        responseVo.setExpireTime(expireTime);
        responseVo.setOverNumLimit(0);
        return AppResponse.success(responseVo);
    }

    @Override
    public AppResponse<InviteInfoVo> getInviteInfoByInviteKey(String inviteKey) {
        // 参数校验
        if (StringUtils.isBlank(inviteKey)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "邀请key不能为空");
        }
        // 根据inviteKey查询邀请信息
        AppMarketInvite invite = appMarketInviteDao.selectByInviteKey(inviteKey);
        if (invite == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "邀请链接不存在");
        }
        if (invite.getDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "邀请链接已失效");
        }
        // 检查邀请是否过期
        Date now = new Date();
        if (invite.getExpireTime() != null && invite.getExpireTime().before(now)) {
            InviteInfoVo resultVo = new InviteInfoVo();
            resultVo.setResultCode(QuotaCodeEnum.E_EXPIRE.getResultCode());
            return AppResponse.success(resultVo);
        }
        // 检查当前已加入人数是否超过限制人数
        Integer currentJoinCount = invite.getCurrentJoinCount() == null ? 0 : invite.getCurrentJoinCount();
        if (invite.getMaxJoinCount() > 0) {
            if (currentJoinCount >= invite.getMaxJoinCount()) {
                InviteInfoVo resultVo = new InviteInfoVo();
                resultVo.setResultCode(QuotaCodeEnum.E_OVER_MARKET_USER_NUM_LIMIT.getResultCode());
                return AppResponse.success(resultVo);
            }
        }
        // 获取邀请人姓名
        String inviterName = "";
        if (StringUtils.isNotBlank(invite.getInviterId())) {
            AppResponse<String> response = rpaAuthFeign.getNameById(invite.getInviterId());
            if (response == null || response.getData() == null) {
                throw new ServiceException("获取用户姓名失败");
            }
            inviterName = response.getData();
        }

        // 获取团队名称
        String marketName = "";
        if (StringUtils.isNotBlank(invite.getMarketId())) {
            marketName = appMarketDao.getMarketNameById(invite.getMarketId());
            if (marketName == null) {
                marketName = "";
            }
        }
        // 构建响应
        InviteInfoVo inviteInfoVo = new InviteInfoVo();
        inviteInfoVo.setInviterName(inviterName);
        inviteInfoVo.setMarketName(marketName);

        // 获取当前登录用户信息
        AppResponse<User> userResponse = rpaAuthFeign.getLoginUser();
        if (userResponse != null && userResponse.ok()) {
            User loginUser = userResponse.getData();
            if (null != loginUser) {
                String userId = loginUser.getId();
                if (!StringUtils.isEmpty(userId)) {
                    AppMarketUser existingUser = appMarketUserDao.getMarketUser(invite.getMarketId(), userId);
                    if (existingUser != null) {
                        inviteInfoVo.setResultCode(QuotaCodeEnum.S_REPEAT_JOIN.getResultCode());
                    }
                }
            }
        }
        return AppResponse.success(inviteInfoVo);
    }

    @Override
    public AppResponse<AcceptResultVo> acceptInvite(String inviteKey) throws NoLoginException {
        // 参数校验
        if (StringUtils.isBlank(inviteKey)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "邀请key不能为空");
        }
        // 根据inviteKey查询邀请信息
        AppMarketInvite invite = appMarketInviteDao.selectByInviteKey(inviteKey);
        if (invite == null) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_EXPIRE);
            return AppResponse.success(resultVo);
        }
        if (invite.getDeleted() == 1) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "邀请链接已失效");
        }
        // 检查邀请是否过期
        Date now = new Date();
        if (invite.getExpireTime() != null && invite.getExpireTime().before(now)) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_EXPIRE);
            return AppResponse.success(resultVo);
        }
        // 检查当前已加入人数是否超过限制人数
        Integer currentJoinCount = invite.getCurrentJoinCount() == null ? 0 : invite.getCurrentJoinCount();
        if (invite.getMaxJoinCount() > 0) {
            if (currentJoinCount >= invite.getMaxJoinCount()) {
                AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_OVER_MARKET_USER_NUM_LIMIT);
                return AppResponse.success(resultVo);
            }
        }
        // 获取当前登录用户信息
        AppResponse<User> userResponse = rpaAuthFeign.getLoginUser();
        if (userResponse == null || !userResponse.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = userResponse.getData();
        String userId = loginUser.getId();
        String marketId = invite.getMarketId();
        String createCompVerKey = doBouncePrefix + inviteKey + marketId + userId;
        // 防抖处理
        deBounce(createCompVerKey, deBounceWindow);
        // 检查用户是否已经在该市场中
        AppMarketUser existingUser = appMarketUserDao.getMarketUser(marketId, userId);
        if (existingUser != null) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.S_REPEAT_JOIN);
            return AppResponse.success(resultVo);
        }
        // 校验市场加入数量配额
        if (!quotaCheckService.checkMarketJoinQuota()) {
            AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_OVER_LIMIT);
            return AppResponse.success(resultVo);
        }
        return self.doAcceptInviteInTransaction(invite, userId, marketId);
    }

    @Transactional(rollbackFor = Exception.class)
    public AppResponse<AcceptResultVo> doAcceptInviteInTransaction(
            AppMarketInvite invite, String userId, String marketId) {
        Date now = new Date();
        // 插入用户关系
        AppMarketUser appMarketUser = buildAppMarketUser(marketId, userId, now);
        appMarketUserDao.insert(appMarketUser);
        // 更新邀请计数
        invite.setCurrentJoinCount(invite.getCurrentJoinCount() + 1);
        invite.setUpdaterId(userId);
        invite.setUpdateTime(now);
        appMarketInviteDao.updateById(invite);
        return AppResponse.success(new AcceptResultVo(QuotaCodeEnum.S_SUCCESS));
    }

    private AppMarketUser buildAppMarketUser(String marketId, String userId, Date now) {
        AppMarketUser appMarketUser = new AppMarketUser();
        appMarketUser.setMarketId(marketId);
        appMarketUser.setUserType("acquirer");
        AppResponse<String> tenantIdRes = rpaAuthFeign.getTenantId();
        if (tenantIdRes == null || !tenantIdRes.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        String tenantId = tenantIdRes.getData();
        // 目标租户id
        appMarketUser.setTenantId(tenantId);
        appMarketUser.setCreatorId(userId);
        appMarketUser.setCreateTime(now);
        appMarketUser.setUpdaterId(userId);
        appMarketUser.setUpdateTime(now);
        appMarketUser.setDeleted(0);
        return appMarketUser;
    }

    /**
     * 根据失效时间类型计算失效时间
     *
     * @param expireTypeEnum 失效时间类型枚举
     * @return 失效时间
     */
    private Date calculateExpireTime(ExpireTypeEnum expireTypeEnum) {
        if (expireTypeEnum == null) {
            return null;
        }
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(new Date());

        switch (expireTypeEnum) {
            case FOUR_HOURS:
                calendar.add(Calendar.HOUR_OF_DAY, 4);
                break;
            case TWENTY_FOUR_HOURS:
                calendar.add(Calendar.HOUR_OF_DAY, 24);
                break;
            case SEVEN_DAYS:
                calendar.add(Calendar.DAY_OF_MONTH, 7);
                break;
            case THIRTY_DAYS:
                calendar.add(Calendar.DAY_OF_MONTH, 30);
                break;
            default:
                return null;
        }

        return calendar.getTime();
    }
}
