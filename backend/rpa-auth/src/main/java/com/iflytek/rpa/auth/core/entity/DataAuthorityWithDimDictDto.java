package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import java.util.List;

/**
 * @author byzhou2
 * @version 1.0 角色数据权限设置页数据权限信息展示对象
 * @description
 * @create 2017/11/2 15:10
 */
public class DataAuthorityWithDimDictDto implements Serializable {

    private static final long serialVersionUID = -7748820351070302015L;
    /**
     * 数据权限id
     */
    private String dataAuthId;

    /**
     * 数据权限名称
     */
    private String dataAuthName;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 是否选中
     */
    private boolean checked;

    /**
     * 关联维度集合
     */
    private List<Dim> dimList;

    public DataAuthorityWithDimDictDto() {}

    public static class Dim implements Serializable {
        private static final long serialVersionUID = -1548982536071323814L;
        // 维度id
        private String dimId;
        // 维度名称
        private String dimName;

        private List<DimDict> dimDictList;

        public Dim() {}

        public Dim(String dimId, String dimName, List<DimDict> list) {
            this.dimId = dimId;
            this.dimName = dimName;
            this.dimDictList = list;
        }

        public String getDimId() {
            return dimId;
        }

        public void setDimId(String dimId) {
            this.dimId = dimId == null ? null : dimId.trim();
        }

        public String getDimName() {
            return dimName;
        }

        public void setDimName(String dimName) {
            this.dimName = dimName;
        }

        public List<DimDict> getDimDictList() {
            return dimDictList;
        }

        public void setDimDictList(List<DimDict> dimDictList) {
            this.dimDictList = dimDictList;
        }
    }

    public static class DimDict implements Serializable {
        private static final long serialVersionUID = -5991082020733531941L;
        // 维度字典id,针对系统内部维度,此值即为系统内数据id
        private String dictId;
        // 维度字典名称
        private String dictName;
        // 维度字典值,针对自定义维度,此值即为业务方数据id
        // 自定义维度,获取value赋值
        private String dictValue;

        public DimDict() {}

        public DimDict(String dictId, String dictName, String dictValue) {
            this.dictId = dictId;
            this.dictName = dictName;
            this.dictValue = dictValue;
        }

        public String getDictId() {
            return dictId;
        }

        public void setDictId(String dictId) {
            this.dictId = dictId == null ? null : dictId.trim();
        }

        public String getDictName() {
            return dictName;
        }

        public void setDictName(String dictName) {
            this.dictName = dictName;
        }

        public String getDictValue() {
            return dictValue;
        }

        public void setDictValue(String dictValue) {
            this.dictValue = dictValue;
        }
    }

    public String getDataAuthId() {
        return dataAuthId;
    }

    public void setDataAuthId(String dataAuthId) {
        this.dataAuthId = dataAuthId == null ? null : dataAuthId.trim();
    }

    public String getDataAuthName() {
        return dataAuthName;
    }

    public void setDataAuthName(String dataAuthName) {
        this.dataAuthName = dataAuthName;
    }

    public Integer getSort() {
        return sort;
    }

    public void setSort(Integer sort) {
        this.sort = sort;
    }

    public boolean isChecked() {
        return checked;
    }

    public void setChecked(boolean checked) {
        this.checked = checked;
    }

    public List<Dim> getDimList() {
        return dimList;
    }

    public void setDimList(List<Dim> dimList) {
        this.dimList = dimList;
    }
}
