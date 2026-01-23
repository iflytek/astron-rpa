package com.iflytek.rpa.notify.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.common.feign.entity.dto.GetUserDto;
import com.iflytek.rpa.common.feign.entity.dto.UserExtendDto;
import com.iflytek.rpa.market.dao.AppMarketDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.vo.AcceptResultVo;
import com.iflytek.rpa.notify.entity.NotifySend;
import com.iflytek.rpa.notify.entity.dto.ApplicationNotifyDto;
import com.iflytek.rpa.notify.entity.dto.CreateNotifyDto;
import com.iflytek.rpa.notify.entity.dto.NotifyListDto;
import com.iflytek.rpa.notify.entity.vo.NotifyVo;
import com.iflytek.rpa.notify.mapper.NotifySendMapper;
import com.iflytek.rpa.notify.service.NotifySendService;
import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.response.QuotaCodeEnum;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Slf4j
public class NotifySendServiceImpl extends ServiceImpl<NotifySendMapper, NotifySend> implements NotifySendService {

    @Resource
    private AppMarketUserDao appMarketUserDao;

    @Resource
    private AppMarketDao appMarketDao;

    @Resource
    private NotifySendMapper notifySendMapper;

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private QuotaCheckService quotaCheckService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<?> createNotify(CreateNotifyDto createNotifyDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String inviteUserId = loginUser.getId();

        List<AppMarketUser> marketUserList = createNotifyDto.getMarketUserList();

        List<NotifySend> notifySendList = new ArrayList<>();
        for (AppMarketUser marketUser : marketUserList) {

            if (marketUser == null) continue;

            NotifySend notifySend = new NotifySend();

            // 构造消息
            String messageInfo = "";
            if (StringUtils.equals(createNotifyDto.getMessageType(), "teamMarketInvite")) {
                // 构造邀人消息体
                messageInfo = buildMessageInfo4Invite(inviteUserId, createNotifyDto.getMarketId());
            } else if (StringUtils.equals(createNotifyDto.getMessageType(), "teamMarketUserAdd")) {
                messageInfo = buildMessageInfo4UserAdd(createNotifyDto.getMarketId());
                createNotifyDto.setMessageType("teamMarketUpdate");
            } else if (StringUtils.equals(createNotifyDto.getMessageType(), "teamMarketUserRemove")) {
                messageInfo = buildMessageInfo4UserRemove(createNotifyDto.getMarketId());
                createNotifyDto.setMessageType("teamMarketUpdate");
            } else {
                // 构造应用更新的消息
                messageInfo = buildMessageInfo4AppUpdate(createNotifyDto.getMarketId(), createNotifyDto.getAppId());
            }

            // appName
            String appName = baseMapper.getAppName(createNotifyDto.getMarketId(), createNotifyDto.getAppId());

            // 数据填充
            notifySend.setTenantId(createNotifyDto.getTenantId());
            notifySend.setUserId(marketUser.getCreatorId());
            notifySend.setMessageType(createNotifyDto.getMessageType());
            notifySend.setMarketId(createNotifyDto.getMarketId());
            notifySend.setUserType(marketUser.getUserType());
            notifySend.setMessageInfo(messageInfo);
            notifySend.setOperateResult(1); // 默认为消息未读
            if (createNotifyDto.getOperateResult() != null) {
                notifySend.setOperateResult(createNotifyDto.getOperateResult());
            }
            notifySend.setAppName(appName);

            notifySendList.add(notifySend);
        }

        if (notifySendList.size() == 0) return AppResponse.success("没有消息需要通知");

        boolean b = saveBatch(notifySendList);

        if (b || marketUserList.size() == 0) {
            return AppResponse.success("产生消息成功");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
        }
    }

    private String buildMessageInfo4UserAdd(String marketId) {
        String marketName = appMarketDao.getMarketNameById(marketId);
        return "您已被企业管理员添加至团队市场：[" + marketName + "]";
    }

    private String buildMessageInfo4UserRemove(String marketId) {
        String marketName = appMarketDao.getMarketNameById(marketId);
        return "您已被企业管理员从团队市场：[" + marketName + "]中移出";
    }

    public void createNotify4Application(ApplicationNotifyDto applicationNotifyDto) {
        NotifySend notifySend = new NotifySend();
        notifySend.setTenantId(applicationNotifyDto.getTenantId());
        notifySend.setUserId(applicationNotifyDto.getUserId());
        notifySend.setMarketId(applicationNotifyDto.getMarketId());
        notifySend.setMessageType("teamMarketUpdate");
        notifySend.setUserType("admin");
        notifySend.setMessageInfo(buildMessageInfo4Application(applicationNotifyDto));
        notifySend.setOperateResult(1); // 默认为消息未读
        this.saveOrUpdate(notifySend);
    }

    @Override
    public AppResponse<?> notifyList(NotifyListDto notifyListDto) throws NoLoginException {

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
        Long pageNo = notifyListDto.getPageNo();
        Long pageSize = notifyListDto.getPageSize();

        IPage<NotifySend> page = new Page<>(pageNo, pageSize);
        LambdaQueryWrapper<NotifySend> wrapper = new LambdaQueryWrapper<>();

        Date date = new Date();

        wrapper.eq(NotifySend::getDeleted, 0);
        wrapper.eq(NotifySend::getUserId, userId);
        wrapper.eq(NotifySend::getTenantId, tenantId);
        wrapper.last(" and create_time >= DATE_SUB(NOW(), INTERVAL 6 MONTH) " + "order by create_time desc");

        IPage<NotifySend> rePage = this.page(page, wrapper);

        // 结果拼接
        List<NotifySend> records = rePage.getRecords();
        List<NotifyVo> newRecords = new ArrayList<>();
        for (NotifySend record : records) {
            NotifyVo notifyVo = new NotifyVo();
            notifyVo.setId(record.getId());
            notifyVo.setCreateTime(record.getCreateTime());
            notifyVo.setOperateResult(record.getOperateResult());
            notifyVo.setMessageType(record.getMessageType());
            notifyVo.setMessageInfo(record.getMessageInfo());
            notifyVo.setAppName(record.getAppName());
            notifyVo.setMarketId(record.getMarketId());
            newRecords.add(notifyVo);
        }

        IPage<NotifyVo> res = new Page<>(pageNo, pageSize);
        res.setRecords(newRecords);
        res.setTotal(rePage.getTotal());
        res.setPages(rePage.getPages());
        res.setSize(rePage.getSize());
        res.setCurrent(rePage.getCurrent());

        return AppResponse.success(res);
    }

    @Override
    public AppResponse<?> hasNotify() throws NoLoginException {

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

        Integer unreadNum = notifySendMapper.getUnreadNum(userId, tenantId);

        if (unreadNum >= 1) return AppResponse.success("1");
        else return AppResponse.success("0");
    }

    @Override
    public AppResponse<?> setAllNotifyRead() throws NoLoginException {

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

        boolean b = baseMapper.allNotifyRead(userId, tenantId);
        if (b) return AppResponse.success("一键已读成功");

        return response;
    }

    @Override
    public AppResponse<?> setSelectedNotifyRead(Long notifyId) throws NoLoginException {

        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        boolean b = baseMapper.setOneRead(notifyId);
        if (b) {
            return AppResponse.success("已读成功");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
        }
    }

    @Override
    public AppResponse<?> rejectJoinTeam(Long notifyId) throws NoLoginException {

        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        boolean b = baseMapper.setOneReject(notifyId);
        if (b) {
            return AppResponse.success("成功拒绝");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
        }
    }

    @Transactional
    @Override
    public AppResponse<?> acceptJoinTeam(Long notifyId) throws NoLoginException {

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

        NotifySend notifySend = baseMapper.selectById(notifyId);
        if (notifySend == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
        }
        if (!userId.equals(notifySend.getUserId())) {
            return AppResponse.error("越权访问");
        }

        if (notifySend.getOperateResult().equals(3)
                || notifySend.getOperateResult().equals(4)) {
            return AppResponse.error("已经操作，请勿重复动作");
        }

        // 判断是否已经在该市场中
        String marketId = baseMapper.getMarketIdFromAppMarketUser(userId, notifySend.getMarketId());
        if (marketId != null) {
            baseMapper.joinTeam(notifyId);
            return AppResponse.error("已经在团队当中，无需重复加入");
        } else {
            // 校验市场加入数量配额
            if (!quotaCheckService.checkMarketJoinQuota()) {
                AcceptResultVo resultVo = new AcceptResultVo(QuotaCodeEnum.E_OVER_LIMIT);
                return AppResponse.success(resultVo);
            }

            AppMarketUser appMarketUser = new AppMarketUser();
            appMarketUser.setMarketId(notifySend.getMarketId());
            appMarketUser.setUserType(notifySend.getUserType());
            appMarketUser.setCreatorId(userId);
            appMarketUser.setUpdaterId(userId);

            int insert = appMarketUserDao.insert(appMarketUser);
            boolean b = baseMapper.joinTeam(notifyId);

            if (insert > 0 && b) {
                return AppResponse.success("加入团队成功");
            } else {
                return AppResponse.error("加入团队失败");
            }
        }
    }

    private String buildMessageInfo4Invite(String userId, String marketId) {
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        GetUserDto getUserDto = new GetUserDto();
        getUserDto.setUserId(userId);
        AppResponse<UserExtendDto> userExtendInfoRes = rpaAuthFeign.getUserExtendInfo(tenantId, getUserDto);
        UserExtendDto data = userExtendInfoRes.getData();
        String userName = data.getUser().getName();
        String marketName = baseMapper.getMarketName(marketId);

        String res = "[" + userName + "]" + "邀请你加入团队市场：" + "[" + marketName + "]" + "," + "确认是否加入？";
        return res;
    }

    private String buildMessageInfo4AppUpdate(String marketId, String appId) {
        String marketName = baseMapper.getMarketName(marketId);
        String appName = baseMapper.getAppName(marketId, appId);

        String res = "你在团队市场[" + marketName + "]获取的应用/模板/组件[" + appName + "]有更新，去看看吧";
        return res;
    }

    private String buildMessageInfo4Application(ApplicationNotifyDto applicationNotifyDto) {
        String statusStr = "";
        String status = applicationNotifyDto.getStatus();
        if ("approved".equals(status)) {
            statusStr = "批准";
        } else if ("rejected".equals(status)) {
            statusStr = "驳回";
        }
        String applicationTypeStr = "";
        String applicationType = applicationNotifyDto.getApplicationType();
        if ("use".equals(applicationType)) {
            applicationTypeStr = "使用";
        } else if ("release".equals(applicationType)) {
            applicationTypeStr = "上架";
        }
        RobotExecute robotExecute = robotExecuteDao.queryByRobotId(
                applicationNotifyDto.getRobotId(),
                applicationNotifyDto.getUserId(),
                applicationNotifyDto.getTenantId());
        String robotStr = robotExecute != null ? robotExecute.getName() : "";

        return String.format("您的%s机器人%s申请流程%s，请至应用市场查看", robotStr, applicationTypeStr, statusStr);
    }
}
