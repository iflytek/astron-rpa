package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * <p>
 * <code>UapExtendRelation</code>
 * </p>
 *
 * @author zqzhou2
 * @version 1.0
 * @since 1.0
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class UapExtendRelation extends UapExtand {

    private static final long serialVersionUID = 346092851185314557L;

    /**
     * 关联表id
     */
    private String relationId;

    /**
     * userid or orgId
     */
    private String mainId;

    /**
     * 值
     */
    private String value;

    /**
     * key文本
     */
    private String text;

    public String getRelationId() {
        return relationId;
    }

    public void setRelationId(String relationId) {
        this.relationId = relationId;
    }

    public String getMainId() {
        return mainId;
    }

    public void setMainId(String mainId) {
        this.mainId = mainId;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }
}
