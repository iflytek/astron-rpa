package com.iflytek.rpa.agent.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.agent.entity.Agent;
import java.util.List;
import org.apache.ibatis.annotations.*;

/**
 * Agent DAO接口
 */
@Mapper
public interface AgentDao extends BaseMapper<Agent> {

    /**
     * 插入新的Agent记录（自动维护创建人信息）
     *
     * @param agent Agent实体
     * @return 影响的行数
     */
    @Insert("INSERT INTO agent_table (agent_id, content, creator_id, updater_id) "
            + "VALUES (#{agentId}, #{content}, #{creatorId}, #{updaterId})")
    int insertAgent(Agent agent);

    /**
     * 更新Agent内容（维护更新人信息，自动触发update_time更新）
     *
     * @param agent Agent实体
     * @return 影响的行数：1-更新成功，0-未找到符合条件的记录或内容未变更
     */
    @Update("UPDATE agent_table " + "SET content = #{content}, updater_id = #{updaterId} "
            + "WHERE agent_id = #{agentId} AND deleted = 0")
    int updateContent(Agent agent);

    /**
     * 根据agentId查询未删除的记录
     *
     * @param agentId Agent ID
     * @return Agent实体，不存在则返回null
     */
    @Select("SELECT * FROM agent_table " + "WHERE agent_id = #{agentId} AND deleted = 0")
    Agent getByAgentId(@Param("agentId") String agentId);

    /**
     * 查询所有未删除的Agent记录
     *
     * @return Agent列表
     */
    @Select("SELECT * FROM agent_table WHERE deleted = 0 ORDER BY create_time DESC")
    List<Agent> listAllAgents();

    /**
     * 按创建人过滤查询未删除的Agent记录
     *
     * @param userId 创建人用户ID
     * @return Agent列表
     */
    @Select("SELECT * FROM agent_table WHERE deleted = 0 AND creator_id = #{userId} ORDER BY create_time DESC")
    List<Agent> listAgentsByUserId(@Param("userId") String userId);

    /**
     * 逻辑删除Agent（维护更新人信息）
     *
     * @param agentId   Agent ID
     * @param updaterId 更新人ID
     * @return 影响的行数
     */
    @Update("UPDATE agent_table " + "SET deleted = 1, updater_id = #{updaterId} "
            + "WHERE agent_id = #{agentId} AND deleted = 0")
    int deleteAgent(@Param("agentId") String agentId, @Param("updaterId") String updaterId);
}
