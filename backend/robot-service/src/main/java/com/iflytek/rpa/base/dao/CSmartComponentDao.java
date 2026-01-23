package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CSmartComponent;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.*;

@Mapper
public interface CSmartComponentDao extends BaseMapper<CSmartComponent> {

    /**
     * 插入新的智能组件记录（自动维护创建人信息）
     *
     * @param component 智能组件实体
     * @return 影响的行数
     */
    @Insert(
            "INSERT INTO c_smart_version (smart_id, smart_type, robot_id, robot_version, content, creator_id, updater_id) "
                    + "VALUES (#{smartId}, #{smartType}, #{robotId}, #{robotVersion}, #{content}, #{creatorId}, #{updaterId})")
    int insert(CSmartComponent component);

    /**
     * 更新智能组件内容（维护更新人信息，自动触发update_time更新）
     *
     * @param component 智能组件实体
     * @return 影响的行数：1-更新成功，0-未找到符合条件的记录或内容未变更
     */
    @Update("UPDATE c_smart_version " + "SET content = #{content}, updater_id = #{updaterId} "
            + "WHERE robot_id = #{robotId} AND smart_id = #{smartId} AND robot_version = 0 AND deleted = 0")
    int updateContent(CSmartComponent component);

    /**
     * 根据robotId和smartId查询未删除的记录
     */
    @Select(
            "SELECT *" + "FROM c_smart_version "
                    + "WHERE smart_id = #{smartId} AND robot_id = #{robotId} AND robot_version = #{robotVersion} AND deleted = 0")
    CSmartComponent getBySmartId(
            @Param("smartId") String smartId,
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion);

    /**
     * 逻辑删除智能组件（维护更新人信息）
     *
     * @param robotId   机器人ID
     * @param smartId  智能组件ID
     * @param updaterId 更新人ID
     * @return 影响的行数
     */
    @Update("UPDATE c_smart_version " + "SET deleted = 1, updater_id = #{updaterId} "
            + "WHERE robot_id = #{robotId} AND smart_id = #{smartId} AND deleted = 0")
    int delete(
            @Param("robotId") String robotId, @Param("smartId") String smartId, @Param("updaterId") String updaterId);

    /**
     * 获取市场上架的流程时，拷贝智能组件数据
     */
    Integer createSmartComponentForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    @Select("select * " + "from c_smart_version "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "order by create_time desc")
    List<CSmartComponent> getAllSmartComponentList(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("userId") String userId);

    Integer createSmartComponentForCurrentVersion(RobotVersionDto robotVersionDto);

    /**
     * 批量插入智能组件
     */
    void insertBatch(List<CSmartComponent> smartComponentList);

    /**
     * 删除旧的编辑版本（版本号为0）的智能组件数据
     * 用于版本回退时清空当前编辑态数据
     */
    @Update("update c_smart_version " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);
}
