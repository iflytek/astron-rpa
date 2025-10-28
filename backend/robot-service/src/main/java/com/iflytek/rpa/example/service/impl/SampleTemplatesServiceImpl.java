package com.iflytek.rpa.example.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.example.dao.SampleTemplatesDao;
import com.iflytek.rpa.example.entity.SampleTemplates;
import com.iflytek.rpa.example.service.SampleTemplatesService;
import org.springframework.stereotype.Service;

/**
 * 系统预定义的模板库(SampleTemplates)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service
public class SampleTemplatesServiceImpl extends ServiceImpl<SampleTemplatesDao, SampleTemplates>
        implements SampleTemplatesService {

    // 用户自行实现方法
}
