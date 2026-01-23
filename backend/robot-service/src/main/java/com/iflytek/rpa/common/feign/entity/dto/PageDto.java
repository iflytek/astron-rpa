package com.iflytek.rpa.common.feign.entity.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.io.Serializable;
import java.util.Collections;
import java.util.List;

/**
 * 分页返回DTO
 *
 * @author xqcao2
 *
 */
public class PageDto<T> implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 1L;

    @JsonProperty("list")
    protected List<T> result = Collections.emptyList();

    @JsonProperty("total")
    protected long totalCount = -1L;

    protected int currentPageNo = 1;

    protected int pageSize = 10;

    public List<T> getResult() {
        return result;
    }

    public void setResult(List<T> result) {
        this.result = result;
    }

    public long getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(long totalCount) {
        this.totalCount = totalCount;
    }

    public int getCurrentPageNo() {
        return currentPageNo;
    }

    public void setCurrentPageNo(int currentPageNo) {
        this.currentPageNo = currentPageNo;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }
}
