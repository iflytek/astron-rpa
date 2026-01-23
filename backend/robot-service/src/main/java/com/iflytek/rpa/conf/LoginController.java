package com.iflytek.rpa.conf;

import static com.iflytek.rpa.terminal.constants.TerminalConstant.TERMINAL_KEY_REAL_TIME;
import static com.iflytek.rpa.terminal.constants.TerminalConstant.TERMINAL_STATUS_OFFLINE;

import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.conf.service.UserRegisterService;
import com.iflytek.rpa.terminal.entity.TerminalLoginRecord;
import com.iflytek.rpa.terminal.service.TerminalLoginRecordService;
import com.iflytek.rpa.terminal.service.TerminalService;
import com.iflytek.rpa.utils.RedisUtils;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
;

/**
 * 客户端登陆登出相关
 */
@RestController
public class LoginController {

    @Autowired
    private TerminalLoginRecordService terminalLoginRecordService;

    @Autowired
    private TerminalService terminalService;

    @Value("${uap-redirect-url:}")
    private String redirectUrl;

    @Autowired
    private UserRegisterService userRegisterService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    /**
     * 查询登录状态
     *
     * @param request
     * @return
     */
    @GetMapping("/login-status")
    public AppResponse<?> loginStatus(HttpServletRequest request) {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        if (null != loginUser) {
            return AppResponse.success(true);
        }
        return AppResponse.success(false);
    }

    /**
     * 退出登录
     *
     * @param request
     * @param response
     * @throws IOException
     */
    @PostMapping(value = "/logout")
    public void logout(HttpServletRequest request, HttpServletResponse response) throws IOException, NoLoginException {
        AppResponse<User> resp = rpaAuthFeign.getLoginUser();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = resp.getData();
        String userId = loginUser.getId();

        // 查询该用户的登陆记录
        TerminalLoginRecord record = terminalLoginRecordService.selectLogoutCandidates(userId);
        if (null != record) {
            // 更新登陆记录的登出时间
            TerminalLoginRecord loginRecord = new TerminalLoginRecord();
            loginRecord.setLogoutTime(new Date());
            loginRecord.setCreatorId(userId);
            terminalLoginRecordService.setLogout(loginRecord);

            // 删除离线的终端数据
            String redisKey = TERMINAL_KEY_REAL_TIME + record.getTerminalId();
            RedisUtils.redisTemplate.delete(redisKey);
            // 状态同步到MySQL
            List<String> terminalIdList = new ArrayList<>();
            terminalService.updateStatusByTerminalIdList(terminalIdList, TERMINAL_STATUS_OFFLINE);
        }

        // 执行登出逻辑
        rpaAuthFeign.logout();
    }

    /**
     * 查询当前登录的用户信息
     *
     * @param request
     * @return
     */
    @GetMapping("/user/info")
    public AppResponse<User> getUserInfo(HttpServletRequest request) {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null) {
            throw new ServiceException("用户信息获取失败");
        }
        return AppResponse.success(response.getData());
    }

    /**
     * 用户注册接口
     *
     * @param phone 手机号
     * @return
     */
    @PostMapping("/register")
    public AppResponse<?> register(@RequestParam String phone) {
        return userRegisterService.register(phone);
    }
}
