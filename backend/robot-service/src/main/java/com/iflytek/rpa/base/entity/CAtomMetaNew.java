package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.util.Date;
import lombok.Data;

/**
 * 新原子能力元数据
 */
@Data
@TableName("c_atom_meta_new")
public class CAtomMetaNew {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String atomKey;

    private String atomContent;

    private Integer sort;

    private Date createTime;

    private Date updateTime;
}
