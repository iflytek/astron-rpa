package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.RobotPageListDto;
import com.iflytek.rpa.robot.entity.vo.RobotPageListVo;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ResourceRobotManageDao {

    IPage<RobotPageListVo> getRobotPageList(IPage<RobotPageListVo> pageConfig, RobotPageListDto queryDto);
}
