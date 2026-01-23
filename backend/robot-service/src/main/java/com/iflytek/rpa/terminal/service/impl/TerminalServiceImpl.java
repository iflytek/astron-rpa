package com.iflytek.rpa.terminal.service.impl;

import static com.iflytek.rpa.terminal.constants.TerminalConstant.*;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.terminal.dao.TerminalDao;
import com.iflytek.rpa.terminal.entity.Terminal;
import com.iflytek.rpa.terminal.entity.TerminalLoginRecord;
import com.iflytek.rpa.terminal.entity.dto.BeatDto;
import com.iflytek.rpa.terminal.entity.dto.RegistryDto;
import com.iflytek.rpa.terminal.service.TerminalLoginRecordService;
import com.iflytek.rpa.terminal.service.TerminalService;
import com.iflytek.rpa.utils.HttpUtils;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.RedisUtils;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class TerminalServiceImpl extends ServiceImpl<TerminalDao, Terminal> implements TerminalService {
    @Resource
    private TerminalDao terminalDao;

    @Autowired
    private TerminalLoginRecordService terminalLoginRecordService;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public AppResponse<String> registry(RegistryDto registryDto) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        //        根据调度模式和任务执行情况计算状态：
        String terminalStatus = calculateState(registryDto.getStatus(), registryDto.getIsDispatch());
        registryDto.setStatus(terminalStatus);

        // 处理静态数据
        processStaticData(registryDto);
        // 处理动态数据
        processDynamicData(registryDto);
        // 记录终端的登陆记录
        // 若该终端没有（有登录态，无登出态）的记录，即要么没有该终端的登录记录，要么完整登录登出。则插入新的登录记录
        Integer recordNum = terminalLoginRecordService.countUnLogoutRecordByTerminalId(registryDto.getTerminalId());
        if (recordNum == null || recordNum.equals(0)) {
            String deptId = "";
            String levelCode = "";
            AppResponse<String> deptIdRes = rpaAuthFeign.getCurrentDeptId();
            if (deptIdRes.ok()) {
                deptId = deptIdRes.getData();
            }
            AppResponse<String> currentLevelCodeRes = rpaAuthFeign.getCurrentLevelCode();
            if (currentLevelCodeRes.ok()) {
                levelCode = currentLevelCodeRes.getData();
            }
            // 插入
            TerminalLoginRecord loginRecord = new TerminalLoginRecord();
            loginRecord.setId(idWorker.nextId() + "");
            loginRecord.setTerminalId(registryDto.getTerminalId());
            loginRecord.setDeptId(deptId);
            loginRecord.setDeptIdPath(levelCode);
            loginRecord.setIp(registryDto.getIp());
            loginRecord.setLoginTime(new Date());
            loginRecord.setLogoutTime(null);
            loginRecord.setLoginStatus(1);
            loginRecord.setCreatorId(userId);
            loginRecord.setUpdaterId(userId);
            loginRecord.setCreateTime(new Date());
            loginRecord.setUpdateTime(new Date());
            loginRecord.setDeleted(0);
            terminalLoginRecordService.insertRecord(loginRecord);
        }
        // 若有登录态，但没有登出态，说明上次登陆的一直没登出，则不新增记录，不处理

        return AppResponse.success("ok");
    }

    private void processIp(Terminal terminal) {
        // 获取客户端实际连接IP（经过代理修正后的）
        terminal.setActualClientIp(getClientIp());
    }

    public String getClientIp() {
        HttpServletRequest request = HttpUtils.getRequest();
        //  优先从X-Forwarded-For获取（适用于多层代理）
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            // 尝试X-Real-IP（适用于单层代理，如Nginx）
            ip = request.getHeader("X-Real-IP");
        }
        // 处理X-Forwarded-For的多IP情况（取第一个非unknown的IP）
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }

    // 状态计算逻辑
    private String calculateState(String status, Integer isDispatch) {
        //        - 如果开启调度模式：有任务执行 -> 状态为运行中; 无任务执行 -> 状态为空闲
        //        - 未开启调度模式 -> 状态为单机中
        if (isDispatch.equals(1)) {
            if (TERMINAL_STATUS_BUSY.equals(status)) {
                return TERMINAL_STATUS_BUSY;
            } else if (TERMINAL_STATUS_FREE.equals(status)) {
                return TERMINAL_STATUS_FREE;
            } else {
                log.error("终端状态错误：{}", status);
                throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "终端状态错误");
            }
        }
        return TERMINAL_STATUS_STANDALONE;
    }

    private void processStaticData(RegistryDto registryDto) throws NoLoginException {
        Terminal terminal = new Terminal();
        BeanUtils.copyProperties(registryDto, terminal);

        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || response.getData() == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        AppResponse<String> deptIdRes = rpaAuthFeign.getCurrentDeptId();
        String deptId = null, deptIdPath = null;
        if (deptIdRes.ok()) {
            deptId = deptIdRes.getData();
            AppResponse<String> currentLevelCodeRes = rpaAuthFeign.getCurrentLevelCode();
            if (currentLevelCodeRes.ok()) {
                deptIdPath = currentLevelCodeRes.getData();
            }
        }
        terminal.setTenantId(tenantId);
        terminal.setUserId(userId);
        terminal.setDeptId(deptId);
        terminal.setDeptIdPath(deptIdPath);
        terminal.setStatus(registryDto.getStatus());
        // 处理ip
        processIp(terminal);
        // 根据设备id从mysql查询设备基本信息和状态，如果存在则更新，不存在则插入（设备名、MAC地址、IP等）；
        Terminal existingTerminal = terminalDao.getByTerminalId(terminal.getTerminalId());
        if (null == existingTerminal) {
            terminalDao.insert(terminal);
        } else {
            terminal.setId(existingTerminal.getId());
            terminal.setUpdateTime(new Date());
            terminalDao.updateById(terminal);
        }
    }

    private void processDynamicData(RegistryDto registryDto) {
        // 插入Hash：`terminal:real_time:{设备id}`，设置status、cpu、memory、disk、last_report_time（当前时间戳）、is_schedule。过期时间30分钟
        String redisKey = TERMINAL_KEY_REAL_TIME + registryDto.getTerminalId();
        Map<String, Object> terminalData = new HashMap<>();
        terminalData.put("status", registryDto.getStatus());
        terminalData.put("lastHeartbeat", System.currentTimeMillis());
        terminalData.put("isDispatch", registryDto.getIsDispatch());
        terminalData.put("cpu", registryDto.getCpu());
        terminalData.put("memory", registryDto.getMemory());
        terminalData.put("disk", registryDto.getDisk());
        RedisUtils.hmset(redisKey, terminalData, 30 * 60);
        // 插入Sorted Set：`terminal:online_status`，添加设备id，score为当前时间戳。
        RedisUtils.zAdd(TERMINAL_KEY_STATUS, registryDto.getTerminalId(), System.currentTimeMillis());
    }

    @Override
    public AppResponse<String> processBeat(BeatDto beatDto) {
        //        根据设备id从redis中查询数据，如果不存在，返回未注册，如果存在，继续下一步；
        String redisKey = TERMINAL_KEY_REAL_TIME + beatDto.getTerminalId();
        Map<Object, Object> terminalData = RedisUtils.hmget(redisKey);
        if (terminalData.isEmpty()) {
            return AppResponse.success(TERMINAL_NOT_FOUND);
        }
        // 计算状态
        String terminalStatus = calculateState(beatDto.getStatus(), beatDto.getIsDispatch());
        if (!terminalStatus.equals(terminalData.get("status"))) {
            // 若设备状态发生变更，更新mysql的状态字段
            Terminal terminal = new Terminal();
            terminal.setTerminalId(beatDto.getTerminalId());
            terminal.setStatus(terminalStatus);
            terminalDao.updateByTerminalId(terminal);
        }
        // 更新Redis：
        // 更新Hash：`device:real_time:{设备id}`，设置status、cpu、memory、disk、last_report_time（当前时间戳）、is_schedule。过期时间30分钟（防止长期积累的僵尸设备数据占用内存）
        Map<String, Object> updateData = new HashMap<>();
        updateData.put("status", terminalStatus);
        updateData.put("lastHeartbeat", System.currentTimeMillis());
        updateData.put("isDispatch", beatDto.getIsDispatch());
        updateData.put("cpu", beatDto.getCpu());
        updateData.put("memory", beatDto.getMemory());
        updateData.put("disk", beatDto.getDisk());
        RedisUtils.hmset(redisKey, updateData, 30 * 60);
        // 更新Sorted Set：`device:online_status`，添加设备id，score为当前时间戳。
        RedisUtils.zAdd(TERMINAL_KEY_STATUS, beatDto.getTerminalId(), System.currentTimeMillis());
        return AppResponse.success("ok");
    }

    @Override
    public void updateStatusByTerminalIdList(List<String> terminalIdList, String status) {
        if (!terminalIdList.isEmpty()) {
            terminalDao.updateStatusByTerminalIdList(terminalIdList, status);
        }
    }
}
