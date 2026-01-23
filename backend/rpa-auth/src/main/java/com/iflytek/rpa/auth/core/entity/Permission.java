package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.io.Serializable;

/**
 * Permission 通用模型
 */
public class Permission implements Serializable {
    public String owner;
    public String name;
    public String createdTime;
    public String displayName;
    public String description;

    public String[] users;
    public String[] roles;
    public String[] domains;

    public String model;
    public String adapter;
    public String resourceType;
    public String[] resources;
    public String[] actions;
    public String effect;

    @JsonProperty("isEnabled")
    public boolean isEnabled;

    public String submitter;
    public String approver;
    public String approveTime;
    public String state;

    public Permission() {}

    public Permission(
            String owner,
            String name,
            String createdTime,
            String displayName,
            String description,
            String[] users,
            String[] roles,
            String[] domains,
            String model,
            String resourceType,
            String[] resources,
            String[] actions,
            String effect,
            boolean isEnabled) {
        this.owner = owner;
        this.name = name;
        this.createdTime = createdTime;
        this.displayName = displayName;
        this.description = description;
        this.users = users;
        this.roles = roles;
        this.domains = domains;
        this.model = model;
        this.resourceType = resourceType;
        this.resources = resources;
        this.actions = actions;
        this.effect = effect;
        this.isEnabled = isEnabled;
    }
}
