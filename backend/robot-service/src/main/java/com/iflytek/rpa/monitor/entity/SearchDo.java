package com.iflytek.rpa.monitor.entity;

import java.util.List;
import lombok.Data;

@Data
public class SearchDo {
    private String searchType;

    private List<String> deptIdPathList;
}
