package com.iflytek.rpa.notify.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.notify.entity.NotifySend;
import com.iflytek.rpa.notify.entity.vo.NotifyVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface NotifySendMapper extends BaseMapper<NotifySend> {

    @Select("select market_name from app_market where market_id=#{marketId} and deleted=0")
    String getMarketName(@Param("marketId") String marketId);

    @Select("select app_name " + "from app_market_resource "
            + "where deleted=0 and market_id=#{marketId} and app_id=#{appId}")
    String getAppName(@Param("marketId") String marketId, @Param("appId") String appId);

    @Select("select market_id from app_market_user where creator_id=#{userId} and tenant_id=#{tenantId} and deleted=0")
    List<String> getAllMarketId(@Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select(
            "select message_info, message_type, create_time, operate_result  " + "from notify_send "
                    + "where deleted=0 and market_id=#{marketId} and user_id=#{userId} and (operate_result=1 or operate_result=2)")
    List<NotifyVo> getNotifySend(@Param("marketId") String marketId, @Param("userId") String userId);

    @Select("select id, message_info, message_type, create_time, operate_result  " + "from notify_send "
            + "where deleted=0 and tenant_id=#{tenantId} and user_id=#{userId} and (operate_result=1 or operate_result=2) "
            + "order by create_time desc "
            + "limit #{pageNo}, #{pageSize}")
    List<NotifyVo> getNotifyListVo(
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("pageNo") Long pageNo,
            @Param("pageSize") Long pageSize);

    @Select(
            "select count(id) " + "from notify_send "
                    + "where deleted = 0 and tenant_id=#{tenantId} and user_id=#{userId} and (operate_result=1 or operate_result=2)")
    Long getNotifyCount(@Param("tenantId") String tenantId, @Param("userId") String userId);

    // 一键已读，update语句
    @Update(
            "update notify_send set operate_result=2 where user_id=#{userId} and tenant_id=#{tenantId} and operate_result=1")
    boolean allNotifyRead(@Param("userId") String userId, @Param("tenantId") String tenantId);

    @Update("update notify_send set operate_result=2 where id=#{notifyId}")
    boolean setOneRead(@Param("notifyId") Long notifyId);

    @Update("update notify_send set operate_result=4 where id=#{notifyId}")
    boolean setOneReject(@Param("notifyId") Long notifyId);

    @Update("update notify_send set operate_result=3 where id=#{notifyId}")
    boolean joinTeam(@Param("notifyId") Long notifyId);

    @Select("select market_id from app_market_user where creator_id=#{userId} and market_id=#{marketId} and deleted=0")
    String getMarketIdFromAppMarketUser(@Param("userId") String userId, @Param("marketId") String marketId);

    @Select(
            "select count(id) from notify_send where deleted=0 and user_id=#{userId} and tenant_id=#{tenantId} and operate_result=1")
    Integer getUnreadNum(@Param("userId") String userId, @Param("tenantId") String tenantId);
}
