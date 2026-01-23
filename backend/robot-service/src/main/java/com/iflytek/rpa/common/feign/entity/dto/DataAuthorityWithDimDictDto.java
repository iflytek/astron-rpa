package com.iflytek.rpa.common.feign.entity.dto;

import java.io.Serializable;
import java.util.List;

public class DataAuthorityWithDimDictDto implements Serializable {
    private static final long serialVersionUID = -7748820351070302015L;
    private String dataAuthId;
    private String dataAuthName;
    private Integer sort;
    private boolean checked;
    private List<Dim> dimList;

    public DataAuthorityWithDimDictDto() {}

    public String getDataAuthId() {
        return this.dataAuthId;
    }

    public void setDataAuthId(String dataAuthId) {
        this.dataAuthId = dataAuthId == null ? null : dataAuthId.trim();
    }

    public String getDataAuthName() {
        return this.dataAuthName;
    }

    public void setDataAuthName(String dataAuthName) {
        this.dataAuthName = dataAuthName;
    }

    public Integer getSort() {
        return this.sort;
    }

    public void setSort(Integer sort) {
        this.sort = sort;
    }

    public boolean isChecked() {
        return this.checked;
    }

    public void setChecked(boolean checked) {
        this.checked = checked;
    }

    public List<Dim> getDimList() {
        return this.dimList;
    }

    public void setDimList(List<Dim> dimList) {
        this.dimList = dimList;
    }

    public static class DimDict implements Serializable {
        private static final long serialVersionUID = -5991082020733531941L;
        private String dictId;
        private String dictName;
        private String dictValue;

        public DimDict() {}

        public DimDict(String dictId, String dictName, String dictValue) {
            this.dictId = dictId;
            this.dictName = dictName;
            this.dictValue = dictValue;
        }

        public String getDictId() {
            return this.dictId;
        }

        public void setDictId(String dictId) {
            this.dictId = dictId == null ? null : dictId.trim();
        }

        public String getDictName() {
            return this.dictName;
        }

        public void setDictName(String dictName) {
            this.dictName = dictName;
        }

        public String getDictValue() {
            return this.dictValue;
        }

        public void setDictValue(String dictValue) {
            this.dictValue = dictValue;
        }
    }

    public static class Dim implements Serializable {
        private static final long serialVersionUID = -1548982536071323814L;
        private String dimId;
        private String dimName;
        private List<DimDict> dimDictList;

        public Dim() {}

        public Dim(String dimId, String dimName, List<DimDict> list) {
            this.dimId = dimId;
            this.dimName = dimName;
            this.dimDictList = list;
        }

        public String getDimId() {
            return this.dimId;
        }

        public void setDimId(String dimId) {
            this.dimId = dimId == null ? null : dimId.trim();
        }

        public String getDimName() {
            return this.dimName;
        }

        public void setDimName(String dimName) {
            this.dimName = dimName;
        }

        public List<DimDict> getDimDictList() {
            return this.dimDictList;
        }

        public void setDimDictList(List<DimDict> dimDictList) {
            this.dimDictList = dimDictList;
        }
    }
}
