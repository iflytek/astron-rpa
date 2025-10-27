package com.iflytek.rpa.example.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.example.dao.SampleUsersDao;
import com.iflytek.rpa.example.entity.SampleUsers;
import com.iflytek.rpa.example.service.SampleUsersService;
import org.springframework.stereotype.Service;

/**
 * 用户从系统模板中注入的样例数据(SampleUsers)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service
public class SampleUsersServiceImpl extends ServiceImpl<SampleUsersDao, SampleUsers> implements SampleUsersService {

    // 用户自行实现方法
}