package com.iflytek.rpa.common.feign.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ExtendRelation extends Extand {
    private static final long serialVersionUID = 346092851185314557L;
    private String relationId;
    private String mainId;
    private String value;
    private String text;

    public ExtendRelation() {}

    public String getRelationId() {
        return this.relationId;
    }

    public void setRelationId(String relationId) {
        this.relationId = relationId;
    }

    public String getMainId() {
        return this.mainId;
    }

    public void setMainId(String mainId) {
        this.mainId = mainId;
    }

    public String getValue() {
        return this.value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getText() {
        return this.text;
    }

    public void setText(String text) {
        this.text = text;
    }
}
